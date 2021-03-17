import os
import math
import functools
import itertools

from io import BytesIO
from typing import Any, Dict, Tuple, Iterator, Optional, Sequence

import PIL
import discord

from PIL import ImageDraw, ImageFont, ImageFilter
from discord.ext import commands
from googletrans import LANGCODES, LANGUAGES, Translator

from potato_bot.bot import Bot
from potato_bot.cog import Cog
from potato_bot.types import Image, StaticImage, AnimatedImage
from potato_bot.context import Context

_VertexType = Dict[str, int]
_VerticesType = Tuple[_VertexType, _VertexType, _VertexType, _VertexType]

OCR_API_URL = "https://content-vision.googleapis.com/v1/images:annotate"


class TROCRException(Exception):
    pass


class AngleUndetectable(TROCRException):
    pass


class TextField:
    def __init__(self, full_text: str, src: PIL.Image, padding: int = 3):
        self.text = full_text

        self.left: Optional[int] = None
        self.upper: Optional[int] = None
        self.right: Optional[int] = None
        self.lower: Optional[int] = None

        self.angle = 0

        self._src_width, self._src_height = src.size

        self._padding = padding

    def add_word(self, vertices: _VerticesType, src_size: Tuple[int, int]) -> None:
        if not self.initialized:
            # Get angle from first word
            self.angle = self._get_angle(vertices)

        left, upper, right, lower = self._vertices_to_coords(
            vertices, src_size, self.angle
        )

        self.left = left if self.left is None else min((self.left, left))
        self.upper = upper if self.upper is None else min((self.upper, upper))
        self.right = right if self.right is None else max((self.right, right))
        self.lower = lower if self.lower is None else max((self.lower, lower))

    @staticmethod
    def _vertices_to_coords(
        vertices: _VerticesType, src_size: Tuple[int, int], angle: int
    ) -> Tuple[int, int, int, int]:
        """Returns Pillow style coordinates (left, upper, right, lower)."""

        # A - 0
        # B - 1
        # C - 2
        # D - 3
        #
        # A----B
        # |    |  angle = 360/0
        # D----C
        #
        #    A
        #  /   \
        # D     B  angle = 315
        #  \   /
        #    C
        #
        # D----A
        # |    |  angle = 270
        # C----B
        #
        #    D
        #  /   \
        # C     A  angle = 225
        #  \   /
        #    B
        #
        # C---D
        # |   | angle = 180
        # B---A
        #
        #    C
        #  /   \
        # B     D angle = 135
        #  \   /
        #    A
        #
        # B---C
        # |   | angle = 90
        # A---D
        #
        #    B
        #  /   \
        # A     C  angle = 45
        #  \   /
        #    D
        if 0 <= angle <= 90:
            left = vertices[0].get("x")
            upper = vertices[1].get("y")
            right = vertices[2].get("x")
            lower = vertices[3].get("y")
        elif 90 < angle <= 180:
            left = vertices[1].get("x")
            upper = vertices[2].get("y")
            right = vertices[3].get("x")
            lower = vertices[0].get("y")
        elif 180 < angle <= 270:
            left = vertices[2].get("x")
            upper = vertices[3].get("y")
            right = vertices[0].get("x")
            lower = vertices[1].get("y")
        elif 270 < angle <= 360:
            left = vertices[3].get("x")
            upper = vertices[0].get("y")
            right = vertices[1].get("x")
            lower = vertices[2].get("y")

        if left is None:
            left = 0
        if upper is None:
            upper = 0
        if right is None:
            right = src_size[0]
        if lower is None:
            lower = src_size[1]

        return (left, upper, right, lower)

    @staticmethod
    def _get_angle(vertices: _VerticesType) -> int:
        def get_coords(vertex: _VertexType) -> Tuple[Optional[int], Optional[int]]:
            return vertex.get("x"), vertex.get("y")

        cycle = itertools.cycle(vertices)
        x, y = get_coords(next(cycle))
        for i in range(4):
            next_x, next_y = get_coords(next(cycle))

            # Any vertex coordinate can be missing
            if None in (x, y, next_x, next_y):
                x, y = next_x, next_y
                continue

            # algo: https://stackoverflow.com/a/27481611

            # mypy literally does not see previous statement
            delta_y = y - next_y  # type: ignore
            delta_x = next_x - x  # type: ignore

            degrees = math.degrees(math.atan2(delta_y, delta_x))

            if degrees < 0:
                degrees += 360

            # compensate missing vertices
            degrees += 90 * i

            break
        else:
            raise AngleUndetectable

        # # truncate last digit, OCR often returns 1-2 degree tilted text, ignore this
        # TEMPORARY: truncate angle to 90 degrees
        return 90 * round(degrees / 90)

    @property
    def coords(self) -> Tuple[int, int, int, int]:
        return (self.left, self.upper, self.right, self.lower)  # type: ignore

    @property
    def coords_padded(self) -> Tuple[int, int, int, int]:
        return (
            max((0, self.left - self._padding)),  # type: ignore
            max((0, self.upper - self._padding)),  # type: ignore
            min((self._src_width, self.right + self._padding)),  # type: ignore
            min((self._src_height, self.lower + self._padding)),  # type: ignore
        )

    # TODO: implement w/h detection ASAP, this is temporary
    # solutions:
    # 1) https://stackoverflow.com/a/9972699
    # text surrounding box dimensions are known, but i had no success implementing this
    # 2) try to keep track of full coords and just calculate distance
    # a lot of coordinates might be missing, 1st solution is more reliable if it worked
    @property
    def width(self) -> int:
        if self.angle in (0, 180, 360):
            return self.right - self.left  # type: ignore

        if self.angle in (90, 270):
            return self.lower - self.upper  # type: ignore

        assert False  # noqa

    @property
    def height(self) -> int:
        if self.angle in (0, 180, 360):
            return self.lower - self.upper  # type: ignore

        if self.angle in (90, 270):
            return self.right - self.left  # type: ignore

        assert False  # noqa

    @property
    def font_size(self) -> int:
        return max((1, int(1.3333333 * self.height) - 2))

    @property
    def stroke_width(self) -> int:
        return max((1, round(self.font_size / 12)))

    @property
    def initialized(self) -> bool:
        return None not in self.coords

    def __repr__(self) -> str:
        return f"<TextField text='{self.text}' coords={self.coords} angle={self.angle}>"


def language_iterator(blocks: Sequence[Any]) -> Iterator[Optional[str]]:
    """Extracts language for each paragraph in Google OCR output"""

    def extract_language(data: Any) -> Optional[str]:
        if (properties := data.get("property")) is None:
            return None

        if (languages := properties.get("detectedLanguages")) is None:
            return None

        return sorted(languages, key=lambda l: l.get("confidence", 1))[-1][
            "languageCode"
        ]

    for block in blocks:
        block_language = extract_language(block)

        for paragraph in block["paragraphs"]:
            paragraph_language = extract_language(paragraph)

            yield paragraph_language or block_language

            # line grouping differs between simple annotations and paragraph grouping in
            # full annotations. "EOL_SURE_SPACE" indicates line break matching simple
            # annotations
            for word in paragraph["words"]:
                last_symbol = word["symbols"][-1]
                if (symbol_properties := last_symbol.get("property")) is None:
                    continue

                if (detected_break := symbol_properties.get("detectedBreak")) is None:
                    continue

                if detected_break["type"] != "EOL_SURE_SPACE":
                    continue

                yield paragraph_language or block_language


class Images(Cog):
    """Image manipulation"""

    async def setup(self) -> None:
        self.font = ImageFont.truetype("DejaVuSans.ttf")

        # TODO: fetch list of languages from API or hardcode
        self.translator = Translator(
            service_urls=[
                "translate.google.com",
                "translate.google.co.kr",
                "translate.google.at",
                "translate.google.de",
                "translate.google.ru",
                "translate.google.ch",
                "translate.google.fr",
                "translate.google.es",
            ]
        )

    @commands.command(hidden=True)
    async def i(self, ctx: Context, i: Image = None) -> None:
        if i is None:
            i = await Image.from_history(ctx)

        await ctx.send(i)

    @commands.command(hidden=True)
    async def si(self, ctx: Context, i: StaticImage = None) -> None:
        if i is None:
            i = await StaticImage.from_history(ctx)

        await ctx.send(i)

    @commands.command(hidden=True)
    async def ai(self, ctx: Context, i: AnimatedImage = None) -> None:
        if i is None:
            i = await AnimatedImage.from_history(ctx)

        await ctx.send(i)

    async def _ocr(self, ctx: Context, image_url: str) -> Dict[str, Any]:
        async with ctx.session.post(
            OCR_API_URL,
            params={
                "key": os.environ["OCR_API_TOKEN"],
            },
            json={
                "requests": [
                    {
                        "features": [{"type": "TEXT_DETECTION"}],
                        "image": {
                            "source": {
                                "imageUri": image_url,
                            }
                        },
                    }
                ]
            },
            headers={
                "x-origin": "https://explorer.apis.google.com",
                "x-referer": "https://explorer.apis.google.com",
            },
        ) as r:
            if r.status != 200:
                if r.content_type.lower() != "application/json":
                    reason = await r.text()
                    if reason.count("\n") > 1:
                        # we got some garbage HTML response
                        reason = "unknown error"

                    await ctx.reply(
                        f"Something really bad happened with underlying API[{r.status}]: {reason}",
                        exit=True,
                    )

                json = await r.json()

                await ctx.reply(
                    f"Error in underlying API[{r.status}]: "
                    f'{json.get("message", "unknown error")}',
                    exit=True,
                )
            json = await r.json()

        if len((responses := json["responses"])) == 0:
            return {}

        return responses[0]

    @commands.command()
    async def ocr(self, ctx: Context, image: Image = None) -> None:
        """Read text on image"""

        if image is None:
            image = await Image.from_history(ctx)

        annotations = await self._ocr(ctx, image.url)

        if not (annotations.get("textAnnotations")):
            return await ctx.reply("No text detected")

        await ctx.send(f"```\n{annotations['fullTextAnnotation']['text']}```")

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 5, type=commands.BucketType.channel)
    async def trocr(
        self, ctx: Context, language: str, image: StaticImage = None
    ) -> None:
        """
        Translate text on image

        Note: text rotation is truncated to 90 degrees for now
        Note:
            Entire text is translated at once for the sake of optimization,
            this might produce bad results. This might be improved in future
            (for multi-language images)
        """

        language = language.lower()

        language = LANGCODES.get(language, language)
        if language not in LANGUAGES:
            ctx.command.reset_cooldown(ctx)

            return await ctx.reply(
                "Invalid language. Use `list` to get list of supported languages"
            )

        if image is None:
            image = await StaticImage.from_history(ctx)

        src = await image.to_pil_image(ctx)

        annotations = await self._ocr(ctx, image.url)

        if not (annotations.get("textAnnotations")):
            return await ctx.reply("No text detected")

        word_annotations = annotations["textAnnotations"][1:]
        block_annotations = annotations["fullTextAnnotation"]["pages"][0]["blocks"]

        # Google OCR API returns entry for each word separately, but they can be joined
        # by checking full image description. In description words are combined into
        # lines, lines are separated by newlines, there is a trailing newline.
        # Coordinates from words in the same line can be merged
        lines = annotations["fullTextAnnotation"]["text"][:-1].split("\n")

        # TODO: group by input languages to improve translation?
        need_trasnslation = {}
        paragraph_languages = language_iterator(block_annotations)

        for i, line in enumerate(lines):
            if next(paragraph_languages) is not None:
                need_trasnslation[i] = line

        if not need_trasnslation:
            return await ctx.send(
                "Nothing to translate on image (either entire text is in target language or language is undetected)"
            )

        translated = await self.translate(
            "\n".join(need_trasnslation.values()), language
        )

        if (accent_cog := self.bot.get_cog("Accents")) is not None:
            # trocr fully depends on newlines, apply accents to each line separately and
            # replace any newlines with spaces to make sure text order is preserved
            translated = "\n".join(
                accent_cog.apply_member_accents_to_text(
                    member=ctx.me, text=line
                ).replace("\n", " ")
                for line in translated.split("\n")
            )

        translated_lines = translated.split("\n")
        if len(translated_lines) != len(need_trasnslation):
            return await ctx.reply(
                f"Error: expected {len(need_trasnslation)} translated lines, got {len(translated_lines)}"
            )

        for idx, translated_line in zip(need_trasnslation.keys(), translated_lines):
            lines[idx] = translated_line

        # error reporting
        notes = ""

        current_word = 0
        fields = []

        for i, line in enumerate(lines):
            field = TextField(line, src)
            original_line = need_trasnslation.get(i, line)

            # TODO: sane iterator instead of this
            for word in word_annotations[current_word:]:
                text = word["description"]
                if original_line.startswith(text):
                    current_word += 1
                    original_line = original_line[len(text) :].lstrip()
                    # TODO: merge multiple lines into box
                    try:
                        field.add_word(word["boundingPoly"]["vertices"], src.size)
                    except AngleUndetectable:
                        notes += f"angle for `{word}` is undetectable\n"
                else:
                    break

            if field.initialized:
                if (original_line := need_trasnslation.get(i, line)) is not None:
                    if line.casefold() != original_line.casefold():
                        fields.append(field)

        if not fields:
            return await ctx.send("Could not translate anything on image")

        result = await self.bot.loop.run_in_executor(None, self.draw, src, fields)

        stats = f"Words: {current_word}\nLines: {len(fields)}"
        if notes:
            stats += f"\nNotes: {notes}"

        await ctx.send(stats, file=discord.File(result, filename="trocr.png"))

    def draw(self, src: PIL.Image, fields: Sequence[TextField]) -> BytesIO:
        FIELD_CAP = 150

        fields = fields[:FIELD_CAP]

        src = src.convert("RGBA")

        for field in fields:
            cropped = src.crop(field.coords_padded)

            # NOTE: next line causes segfaults if coords are wrong, debug from here
            blurred = cropped.filter(ImageFilter.GaussianBlur(10))

            # Does not work anymore for some reason, black stroke is good anyway
            # field.inverted_avg_color = ImageOps.invert(
            #     blurred.resize((1, 1)).convert("L")
            # ).getpixel((0, 0))  # ugly!!!

            src.paste(blurred, field.coords_padded)

        for field in fields:
            # TODO: figure out how to fit text into boxes with Pillow without creating
            # extra images
            font = self.font.font_variant(size=field.font_size)

            text_im = PIL.Image.new(
                "RGBA",
                size=font.getsize(field.text, stroke_width=field.stroke_width),
            )

            ImageDraw.Draw(text_im).text(
                (0, 0),
                text=field.text,
                font=font,
                spacing=0,
                stroke_width=field.stroke_width,
                stroke_fill=(0, 0, 0),
            )

            src.alpha_composite(
                text_im.resize(
                    (
                        min((text_im.width, field.width)),
                        min((text_im.height, field.height)),
                    ),
                ).rotate(field.angle, expand=True, resample=PIL.Image.BICUBIC),
                field.coords_padded[:2],
            )

        result = BytesIO()
        src.save(result, format="PNG")

        return BytesIO(result.getvalue())

    async def translate(self, text: str, out_lang: str) -> str:
        translation = await self.bot.loop.run_in_executor(
            None, functools.partial(self.translator.translate, text, dest=out_lang)
        )

        return translation.text

    @trocr.command(name="list")
    async def _language_list(self, ctx: Context) -> None:
        """Get a list of supported languages"""

        await ctx.send(
            "TODO: <https://github.com/ssut/py-googletrans/blob/d15c94f176463b2ce6199a42a1c517690366977f/googletrans/constants.py#L76-L182>"
        )


def setup(bot: Bot) -> None:
    bot.add_cog(Images(bot))
