from __future__ import annotations

import enum
import asyncio
import warnings

from io import BytesIO
from typing import Any, Optional
from asyncio import TimeoutError

import PIL

from PIL.Image import DecompressionBombWarning
from discord.ext import commands

from .context import Context
from .regexes import EMOTE_REGEX, CLEAN_URL_REGEX

warnings.simplefilter("error", DecompressionBombWarning)


class ImageType(enum.Enum):
    EMOTE = 0
    EMOJI = 1
    USER = 2
    URL = 3
    ATTACHMENT = 4
    EMBED = 5


class FetchedImage:
    __slots__ = ("bytes",)

    def __init__(self, bytes: bytes):
        self.bytes = bytes

    async def to_pil_image(
        self, ctx: Context, *, max_dimensions: int = 10000
    ) -> PIL.Image:
        """Returns Pillow image created from bytes. Should be closed manually"""

        try:
            img = PIL.Image.open(BytesIO(self.bytes))
        except PIL.Image.DecompressionBombError:
            await ctx.send(
                f"Failed to open image, exceeds **{PIL.Image.MAX_IMAGE_PIXELS}** pixel limit",
                exit=True,
            )
        except OSError as e:
            await ctx.send(f"Failed to open image: {e}", exit=True)

        else:
            if sum(img.size) > max_dimensions:
                img.close()
                await ctx.send(f"Image is too large: {img.size} pixels", exit=True)

        return img

    def __repr__(self) -> str:
        return f"<{type(self).__name__} bytes={len(self.bytes)}>"


class Image:
    DEFAULT_STATIC_FORMAT = "png"
    DEFAULT_ANIMATED_FORMAT = "gif"

    STATIC_FORMATS = (
        DEFAULT_STATIC_FORMAT,
        "jpg",
        "jpeg",
        "webp",
    )
    ANIMATED_FORMATS = (DEFAULT_ANIMATED_FORMAT,)

    __slots__ = (
        "type",
        "url",
        "fetched",
    )

    def __init__(
        self,
        type: ImageType,
        url: str,
        bytes: Optional[bytes] = None,
    ):
        self.type = type
        self.url = url

        self.fetched = FetchedImage(bytes) if bytes else None

    @classmethod
    async def convert(cls, ctx: Context, argument: str) -> Image:
        return await cls.from_pattern(ctx, argument)

    @classmethod
    async def from_pattern(cls, ctx: Context, argument: str) -> Image:
        return await cls._from_pattern(ctx, argument, allow_animated=True)

    @classmethod
    async def _from_pattern(
        cls,
        ctx: Context,
        argument: str,
        *,
        allow_static: bool = True,
        allow_animated: bool = False,
    ) -> Image:
        if not (allow_static or allow_animated):
            raise ValueError("Either animated or static image type should be allowed")

        def pick_format(target_animated: bool) -> Optional[str]:
            if allow_static and allow_animated:
                return (
                    cls.DEFAULT_ANIMATED_FORMAT
                    if target_animated
                    else cls.DEFAULT_STATIC_FORMAT
                )

            if allow_animated and target_animated:
                return cls.DEFAULT_ANIMATED_FORMAT

            if allow_static:
                return cls.DEFAULT_STATIC_FORMAT

            return None

        # check if pattern is emote
        if (emote_match := EMOTE_REGEX.fullmatch(argument)) :
            emote_id = emote_match["id"]
            animated = emote_match["animated"]

            if (emote_format := pick_format(animated)) is None:
                raise commands.BadArgument(
                    "Static images are not allowed, animated emote provided"
                )

            if (emote := ctx.bot.get_emoji(emote_id)) :
                return Image(
                    type=ImageType.EMOTE,
                    url=str(emote.url_as(format=emote_format)),
                )

            return Image(
                type=ImageType.EMOTE,
                url=f"https://cdn.discordapp.com/emojis/{emote_id}.{emote_format}",
            )

        # check if pattern is emoji
        # thanks NotSoSuper#0001 for the API

        # thanks discord for this nonsense
        pattern_no_selector_16 = argument.rstrip("\N{VARIATION SELECTOR-16}")

        code = "-".join(map(lambda c: f"{ord(c):x}", pattern_no_selector_16))
        async with ctx.session.get(
            f"https://bot.mods.nyc/twemoji/{code}.png", timeout=5
        ) as r:
            if r.status == 200:
                return Image(
                    type=ImageType.EMOTE,
                    url=f"https://bot.mods.nyc/twemoji/{code}.png",
                    bytes=await r.read(),
                )

        # check if pattern is user mention
        try:
            user = await commands.UserConverter().convert(ctx, argument)
        except commands.UserNotFound:
            pass
        else:
            if (avatar_format := pick_format(user.is_avatar_animated())) is None:
                raise commands.BadArgument(
                    f"Static images are not allowed, {user} has static avatar",
                )

            return Image(
                type=ImageType.USER,
                url=str(user.avatar_url_as(format=avatar_format)),
            )

        # check if pattern is url
        argument = CLEAN_URL_REGEX.sub("", argument)

        if not argument.startswith(("http://", "https://")):
            raise commands.BadArgument(
                f"Unable to match custom emote, emoji or user with `{argument}`\n"
                f"If input is image url, it should begin with http or https",
            )

        return Image(type=ImageType.URL, url=argument)

    @classmethod
    async def from_history(
        cls,
        ctx: Context,
    ) -> Image:
        return await cls._from_history(ctx, allow_animated=True)

    @classmethod
    async def _from_history(
        cls,
        ctx: Context,
        *,
        allow_static: bool = True,
        allow_animated: bool = False,
    ) -> Image:
        if not (allow_static or allow_animated):
            raise ValueError("Either animated or static image type should be allowed")

        def check_extension(url: str) -> Optional[str]:
            extension = url.rpartition(".")[-1].lower()
            if extension in cls.STATIC_FORMATS and allow_static:
                return extension

            elif extension in cls.ANIMATED_FORMATS and allow_animated:
                return extension

            return None

        # check channel history for attachments
        #
        # command can be invoked by message edit, but we still want
        # to check messages before created_at
        history = await ctx.channel.history(
            limit=200, before=ctx.message.created_at
        ).flatten()

        for m in [ctx.message] + history:
            # check attachments (files uploaded to discord)
            for attachment in m.attachments:
                if check_extension(attachment.filename) is None:
                    continue

                return Image(
                    type=ImageType.ATTACHMENT,
                    url=attachment.url,
                )

            # check embeds (user posted url / bot posted rich embed)
            for embed in m.embeds:
                if embed.image:
                    if check_extension(embed.image.proxy_url) is not None:
                        return Image(
                            type=ImageType.EMBED,
                            url=embed.image.url,
                        )

                # bot condition because we do not want image from
                # rich embed thumbnail
                if not embed.thumbnail or (m.author.bot and embed.type == "rich"):
                    continue

                # avoid case when image embed was created from url that is
                # used as argument or flag
                if m.id == ctx.message.id:
                    if embed.thumbnail.url in m.content:
                        continue

                if check_extension(embed.thumbnail.proxy_url) is None:
                    continue

                return Image(
                    type=ImageType.EMBED,
                    url=embed.thumbnail.url,
                )

        await ctx.send("Nothing found in latest 200 messages", exit=True)

    async def fetch(
        self,
        ctx: Context,
        *,
        url: str = None,
        **kwargs: Any,
    ) -> FetchedImage:
        if url is None:
            url = self.url

        if url == self.url and self.fetched is not None:
            return self.fetched
        else:
            image_bytes = await self._fetch(ctx, url, **kwargs)
            fetched = FetchedImage(image_bytes)

            if url == self.url:
                self.fetched = fetched

        return fetched

    @classmethod
    async def _fetch(
        cls,
        ctx: Context,
        url: str,
        *,
        allow_static: bool = True,
        allow_animated: bool = False,
        timeout: int = 5,
        max_content_length: int = 7000000,
    ) -> bytes:
        try:
            async with ctx.session.get(
                url, timeout=timeout, raise_for_status=True
            ) as r:
                if (r.content_length or 0) > max_content_length:
                    raise Exception("content is too big")

                allowed_extensions = []
                if allow_static:
                    allowed_extensions.extend(cls.STATIC_FORMATS)
                if allow_animated:
                    allowed_extensions.extend(cls.ANIMATED_FORMATS)

                if r.content_type.rpartition("/")[-1].lower() not in allowed_extensions:
                    raise Exception(
                        f'unknown content type: **{r.content_type}**, expected one of **{", ".join(allowed_extensions)}**'
                    )

                return await r.read()
        except (Exception, asyncio.TimeoutError) as e:
            error = "Download error: "
            if isinstance(e, TimeoutError):
                error += f"timeout reached: **{timeout}s**"
            else:
                error += str(e)

            raise commands.ConversionError(error)

    async def to_pil_image(self, ctx: Context) -> PIL.Image:
        fetched = await self.fetch(ctx)

        return await fetched.to_pil_image(ctx)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} type={self.type.name} url={self.url}>"


class StaticImage(Image):
    @classmethod
    async def from_pattern(cls, ctx: Context, argument: str) -> Image:
        return await cls._from_pattern(ctx, argument)

    @classmethod
    async def from_history(
        cls,
        ctx: Context,
    ) -> Image:
        return await cls._from_history(ctx)


class AnimatedImage(Image):
    @classmethod
    async def from_pattern(cls, ctx: Context, argument: str) -> Image:
        return await cls._from_pattern(
            ctx, argument, allow_static=False, allow_animated=True
        )

    @classmethod
    async def from_history(
        cls,
        ctx: Context,
    ) -> Image:
        return await cls._from_history(ctx, allow_static=False, allow_animated=True)
