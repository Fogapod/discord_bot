import functools

import googletrans

from discord.ext import commands

from pink.bot import Bot
from pink.cog import Cog
from pink.context import Context

from .types import Language


class Translator(Cog):
    async def setup(self) -> None:
        # TODO: fetch list of languages from API or hardcode
        self.translator = googletrans.Translator(
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

    @commands.group(
        name="translate",
        aliases=["tr"],
        invoke_without_command=True,
        ignore_extra=False,
    )
    async def _translate(self, ctx: Context, language: Language, *, text: str) -> None:
        """Translate text into specified language"""

        translated = await self._raw_translate(text, language)

        await ctx.send(f"{translated.src} -> {language}```\n{translated.text}```")

    async def _raw_translate(
        self, text: str, out_lang: str
    ) -> googletrans.models.Translated:
        return await self.bot.loop.run_in_executor(
            None, functools.partial(self.translator.translate, text, dest=out_lang)
        )

    async def translate(self, text: str, out_lang: str) -> str:
        translated = await self._raw_translate(text, out_lang)

        return translated.text

    @_translate.command(name="list")
    async def _language_list(self, ctx: Context) -> None:
        """Get a list of supported languages"""

        await ctx.send(
            "TODO: <https://github.com/ssut/py-googletrans/blob/d15c94f176463b2ce6199a42a1c517690366977f/googletrans/constants.py#L76-L182>"
        )


def setup(bot: Bot) -> None:
    bot.add_cog(Translator(bot))
