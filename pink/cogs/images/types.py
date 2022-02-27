from __future__ import annotations

import asyncio
import enum
import re
import warnings

from asyncio import TimeoutError
from io import BytesIO
from typing import Any, List, Optional

import aiohttp
import discord
import PIL

from discord.ext import commands  # type: ignore[attr-defined]
from PIL.Image import DecompressionBombWarning

from pink.context import Context
from pink.errors import PINKError
from pink.regexes import CLEAN_URL_REGEX, EMOTE_REGEX, ID_REGEX

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

    def __init__(self, data: bytes):
        self.bytes = data

    async def to_pil_image(
        self, _: Context, *, max_dimensions: int = 10000
    ) -> PIL.Image:
        """Returns Pillow image created from bytes. Should be closed manually"""

        try:
            img = PIL.Image.open(BytesIO(self.bytes))
        except PIL.Image.DecompressionBombError:
            raise PINKError(
                f"failed to open image, exceeds **{PIL.Image.MAX_IMAGE_PIXELS}** pixel limit"
            )
        except OSError as e:
            raise PINKError(f"failed to open image: {e}", formatted=False)

        else:
            if sum(img.size) > max_dimensions:
                # TODO: clean up close calls? Pillow seem to stop leaking memory
                img.close()

                raise PINKError(f"Image is too large: **{img.size}pix**")

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
        "is_spoiler",
    )

    def __init__(
        self,
        kind: ImageType,
        url: str,
        data: Optional[bytes] = None,
        is_spoiler: bool = False,
    ):
        self.type = kind
        self.url = url
        self.is_spoiler = is_spoiler

        self.fetched = FetchedImage(data) if data else None

    @classmethod
    async def convert(cls, ctx: Context, argument: str) -> Image:
        return await cls.from_text(ctx, argument)

    @classmethod
    async def from_text(cls, ctx: Context, argument: str) -> Image:
        return await cls._from_text(ctx, argument, allow_animated=True)

    @classmethod
    async def _from_reference(
        cls,
        ctx: Context,
        reference: discord.MessageReference,
        *,
        allow_static: bool = True,
        allow_animated: bool = False,
    ) -> Image:
        if (resolved := reference.resolved) is None:
            resolved = await ctx.channel.fetch_message(reference.message_id)

        if isinstance(resolved, discord.Message):  # and not discord.DeletedMessage
            if (
                img := cls.from_message(
                    ctx,
                    resolved,
                    allow_static=allow_static,
                    allow_animated=allow_animated,
                )
            ) is not None:
                return img

            raise commands.BadArgument("No images found in referenced message")

        raise commands.BadArgument(
            f"Unable to fetch referenced message {ctx.channel.id}-{ctx.message.id}",
        )

    @classmethod
    async def _from_text(
        cls,
        ctx: Context,
        argument: str,
        *,
        allow_static: bool = True,
        allow_animated: bool = False,
    ) -> Image:
        if not (allow_static or allow_animated):
            raise ValueError("Either animated or static image type should be allowed")

        # if there is a referenced message, it is more important than message content
        # for these reasons:
        #  - it takes more efdort to reply to message than to attach file/paste url
        #  - if this was a mistake, it's easier for user to use command again relying on
        #    from_history to fetch previous message rather than replying to message
        #    again
        #
        # this implementation is a bit of a mess, there is an `argument` parameter, but
        # we assume that ctx.message is target message in from_history anyway
        if (reference := ctx.message.reference) is not None:
            return await cls._from_reference(
                ctx,
                reference,
                allow_static=allow_static,
                allow_animated=allow_animated,
            )

        if argument == "~":
            return await cls.from_history(ctx)

        # match up to 50 previous messages using one or multiple ^'s
        if re.fullmatch(r"\^{1,50}", argument):
            msgs = await ctx.channel.history(
                before=ctx.message.created_at, limit=50
            ).flatten()

            message = msgs[len(argument) - 1]

            if not (
                image := cls.from_message(
                    ctx,
                    message,
                    allow_static=allow_static,
                    allow_animated=allow_animated,
                )
            ):
                raise commands.BadArgument(
                    f"Nothing found in message <{message.jump_url}>"
                )

            return image

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

            # only static allowed, target is animated
            return None

        # check if pattern is emote
        if emote_match := EMOTE_REGEX.fullmatch(argument):
            emote_id = int(emote_match["id"])
            is_animated = emote_match["animated"] != ""

            if (emote_format := pick_format(is_animated)) is None:
                raise commands.BadArgument(
                    "Static images are not allowed, static emote provided"
                )

            if emote := ctx.bot.get_emoji(emote_id):
                return Image(
                    kind=ImageType.EMOTE,
                    url=str(emote.url_as(format=emote_format)),
                )

            return Image(
                kind=ImageType.EMOTE,
                url=f"https://cdn.discordapp.com/emojis/{emote_id}.{emote_format}",
            )

        # check if pattern is id that points to emote
        if id_match := ID_REGEX.fullmatch(argument):
            if emote := ctx.bot.get_emoji(int(id_match.string)):
                if (emote_format := pick_format(emote.animated)) is None:
                    raise commands.BadArgument(
                        "Static images are not allowed, static emote provided"
                    )

                return Image(
                    kind=ImageType.EMOTE,
                    url=str(emote.url_as(format=emote_format)),
                )

        # check if pattern is emoji
        # thanks NotSoSuper and cake for the CDN

        # thanks discord for this nonsense
        pattern_no_selector_16 = argument.rstrip("\N{VARIATION SELECTOR-16}")

        code = "-".join(map(lambda c: f"{ord(c):x}", pattern_no_selector_16))
        emote_url = f"https://cdn.notsobot.com/twemoji/512x512/{code}.png"

        async with ctx.session.get(
            emote_url, timeout=aiohttp.ClientTimeout(total=5)
        ) as r:
            if r.status == 200:
                return Image(
                    kind=ImageType.EMOTE,
                    url=emote_url,
                    data=await r.read(),
                )

        # check if pattern is user mention
        try:
            # TODO: case insensitive or fuzzy because this is trash
            user = await commands.UserConverter().convert(ctx, argument)
        except commands.UserNotFound:
            pass
        else:
            if (avatar_format := pick_format(user.is_avatar_animated())) is None:
                raise commands.BadArgument(
                    f"Static images are not allowed, {user} has static avatar",
                )

            return Image(
                kind=ImageType.USER,
                url=str(user.display_avatar.with_format(avatar_format)),
            )

        # check if pattern is url
        argument = CLEAN_URL_REGEX.sub("", argument)

        if not argument.startswith(("http://", "https://")):
            raise commands.BadArgument(
                f"Unable to match custom emote, emoji or user with `{argument}`\n"
                f"If input is image url, it should begin with http or https"
            )

        return Image(kind=ImageType.URL, url=argument)

    @classmethod
    async def from_history(
        cls,
        ctx: Context,
    ) -> Image:
        return await cls._from_history(ctx, allow_animated=True)

    @classmethod
    def _check_extension(
        cls,
        url: str,
        *,
        allow_static: bool = True,
        allow_animated: bool = False,
    ) -> Optional[str]:
        extension = url.rpartition(".")[-1].lower()
        if extension in cls.STATIC_FORMATS and allow_static:
            return extension

        elif extension in cls.ANIMATED_FORMATS and allow_animated:
            return extension

        return None

    @classmethod
    def from_message(
        cls,
        ctx: Context,
        msg: discord.Message,
        *,
        allow_static: bool = True,
        allow_animated: bool = False,
    ) -> Optional[Image]:
        # check attachments (files uploaded to discord)
        for attachment in msg.attachments:
            if (
                cls._check_extension(
                    attachment.filename,
                    allow_static=allow_static,
                    allow_animated=allow_animated,
                )
                is None
            ):
                continue

            return Image(
                kind=ImageType.ATTACHMENT,
                url=attachment.url,
                is_spoiler=attachment.is_spoiler(),
            )

        # note on embed type ignores: pretty sure urls are present when objects exist

        # check embeds (user posted url / bot posted rich embed)
        for embed in msg.embeds:
            if embed.image:
                if (
                    cls._check_extension(
                        embed.image.url,  # type: ignore[arg-type]
                        allow_static=allow_static,
                        allow_animated=allow_animated,
                    )
                    is not None
                ):
                    return Image(
                        kind=ImageType.EMBED,
                        url=embed.image.url,  # type: ignore[arg-type]
                    )

            # bot condition because we do not want image from
            # rich embed thumbnail
            if not embed.thumbnail or (msg.author.bot and embed.type == "rich"):
                continue

            # avoid case when image embed was created from url that is
            # used as argument or flag
            if msg.id == ctx.message.id:
                if embed.thumbnail.url in msg.content:  # type: ignore[operator]
                    continue

            if (
                cls._check_extension(
                    embed.thumbnail.url,  # type: ignore[arg-type]
                    allow_static=allow_static,
                    allow_animated=allow_animated,
                )
                is None
            ):
                continue

            return Image(
                kind=ImageType.EMBED,
                url=embed.thumbnail.url,  # type: ignore[arg-type]
            )

        return None

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

        # referenced message is checked second time (first in from_pattern), but
        #  a) it should be in cache by this time
        #  b) usually it is not checked if user does not provide input
        if (reference := ctx.message.reference) is not None:
            return await cls._from_reference(
                ctx,
                reference,
                allow_static=allow_static,
                allow_animated=allow_animated,
            )

        # check channel history for attachments
        #
        # command can be invoked by message edit, but we still want
        # to check messages before created_at
        history = await ctx.channel.history(
            limit=200, before=ctx.message.created_at
        ).flatten()

        for msg in [ctx.message] + history:
            if (
                img := cls.from_message(
                    ctx, msg, allow_static=allow_static, allow_animated=allow_animated
                )
            ) is not None:
                return img

        raise commands.BadArgument("Nothing found in latest 200 messages")

    async def fetch(
        self,
        ctx: Context,
        *,
        url: Optional[str] = None,
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
        timeout: int = 15,
        max_content_length: int = 8000000,
    ) -> bytes:
        try:
            async with ctx.session.get(url, timeout=timeout) as r:
                if r.status != 200:
                    raise PINKError(f"bad status code: **{r.status}**")

                if (r.content_length or 0) > max_content_length:
                    raise PINKError("content is too big", formatted=False)

                allowed_extensions: List[str] = []
                if allow_static:
                    allowed_extensions.extend(cls.STATIC_FORMATS)
                if allow_animated:
                    allowed_extensions.extend(cls.ANIMATED_FORMATS)

                if r.content_type.rpartition("/")[-1].lower() not in allowed_extensions:
                    raise PINKError(
                        f'unknown content type: **{r.content_type}**, expected one of **{", ".join(allowed_extensions)}**'
                    )

                return await r.read()
        except PINKError:
            raise
        except (Exception, asyncio.TimeoutError) as e:
            error = "Download error: "
            if isinstance(e, TimeoutError):
                error += f"timeout reached: **{timeout}s**"
            else:
                error += str(e)

            raise commands.BadArgument(error)

    async def to_pil_image(self, ctx: Context) -> PIL.Image:
        fetched = await self.fetch(ctx)

        return await fetched.to_pil_image(ctx)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} url={self.url} type={self.type.name}>"


class StaticImage(Image):
    @classmethod
    async def from_text(cls, ctx: Context, argument: str) -> Image:
        return await cls._from_text(ctx, argument)

    @classmethod
    async def from_history(
        cls,
        ctx: Context,
    ) -> Image:
        return await cls._from_history(ctx)


class AnimatedImage(Image):
    @classmethod
    async def from_text(cls, ctx: Context, argument: str) -> Image:
        return await cls._from_text(
            ctx, argument, allow_static=False, allow_animated=True
        )

    @classmethod
    async def from_history(
        cls,
        ctx: Context,
    ) -> Image:
        return await cls._from_history(ctx, allow_static=False, allow_animated=True)
