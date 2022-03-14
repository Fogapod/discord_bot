import asyncio

import googletrans

from discord.ext import commands  # type: ignore[attr-defined]

from pink.bot import PINK
from pink.cog import Cog
from pink.context import Context

from .constants import LANGUAGES, REVERSE_LANGCODE_ALIASES
from .types import Language


class Translator(Cog):
    async def cog_load(self) -> None:
        self.translator = googletrans.Translator(service_urls=googletrans.constants.DEFAULT_SERVICE_URLS)

    @commands.group(
        name="translate",
        aliases=["tr"],
        invoke_without_command=True,
        ignore_extra=False,
    )
    async def _translate(self, ctx: Context, language: Language, *, text: str) -> None:
        """Translate text into specified language"""

        translated = await self._raw_translate(text, language)

        maybe_in_lang_alias = REVERSE_LANGCODE_ALIASES.get(translated.src.lower(), translated.src)

        if (in_lang := LANGUAGES.get(maybe_in_lang_alias)) is not None:
            # full name found, need to title() it
            in_lang = in_lang.title()
        else:
            in_lang = translated.src

        out_lang = LANGUAGES[language].title()

        await ctx.send(f"**{in_lang}** -> **{out_lang}**```\n{translated.text}```")

    async def _raw_translate(self, text: str, out_lang: str) -> googletrans.models.Translated:
        return await asyncio.to_thread(self.translator.translate, text, dest=out_lang)

    async def translate(self, text: str, out_lang: str) -> str:
        translated = await self._raw_translate(text, out_lang)

        return translated.text

    @_translate.command(name="list")
    async def _language_list(self, ctx: Context) -> None:
        """Get a list of supported languages"""

        await ctx.send(
            "TODO: <https://github.com/ssut/py-googletrans/blob/d15c94f176463b2ce6199a42a1c517690366977f/googletrans/constants.py#L76-L182>"
        )


async def setup(bot: PINK) -> None:
    await bot.add_cog(Translator(bot))
