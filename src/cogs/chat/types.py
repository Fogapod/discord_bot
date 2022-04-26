import travitia_talk as tt

from discord.ext import commands  # type: ignore[attr-defined]

from src.context import Context


class Emotion(commands.Converter):
    async def convert(self, _: Context, argument: str) -> tt.Emotion:
        try:
            return tt.Emotion(argument)
        except ValueError:
            raise commands.BadArgument(f"Must be one of {', '.join(e.value for e in tt.Emotion)}")
