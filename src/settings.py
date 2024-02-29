from __future__ import annotations

import contextlib
import os
import typing

from collections.abc import Iterable
from enum import Enum, auto
from pathlib import Path
from typing import Any, ClassVar, Literal, Optional, TypeVar

__all__ = ("settings",)


class _MissingClass:
    def __repr__(self) -> str:
        return "<Missing>"


Missing = _MissingClass()


class Loader(Enum):
    TOML = auto()
    JSON = auto()


class Field:
    __slots__ = (
        "name",
        "annotation",
        "default",
    )

    def __init__(self, name: str, annotation: Any, default: Any) -> None:
        self.name = name
        self.annotation = annotation
        self.default = default


class BaseConfig: ...


def merge_configs(base: type[BaseConfig], overrides: Optional[type[BaseConfig]]) -> type[BaseConfig]:
    bases: tuple[type[BaseConfig], ...]

    if overrides is None:
        bases = (base,)
    elif base == overrides:
        bases = (overrides,)
    else:
        bases = (overrides, base)

    return type("Config", bases, {})


class ModelMeta(type):
    def __new__(
        mcls,  # noqa: N804
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> type:
        config = BaseConfig

        for base in reversed(bases):
            if issubclass(base, BaseModel):
                config = merge_configs(config, base.__config__)

        if config_override := namespace.get("Config"):
            config = merge_configs(config, config_override)

        fields = []
        all_fields_optional = True

        # an ugly hack. this is only constructed to be passed to typing.get_type_hints
        cls_for_annotation_inspection = super().__new__(mcls, name, (), namespace, **kwargs)

        for ann_name, ann_type in typing.get_type_hints(cls_for_annotation_inspection).items():
            default_value = namespace.get(ann_name, Missing)

            fields.append(Field(ann_name, ann_type, default_value))

        cls = super().__new__(
            mcls,
            name,
            bases,
            {
                "__config__": config,
                "__all_fields_optional__": all_fields_optional,
                "__fields__": fields,
                **namespace,
            },
            **kwargs,
        )

        return cls


class BaseModel(metaclass=ModelMeta):
    __config__: ClassVar[type[BaseConfig]]
    # TODO
    __all_fields_optional__: ClassVar[bool]
    __fields__: ClassVar[Iterable[Field]]

    @classmethod
    def validate(cls, data: _MissingClass | dict[str, Any], env_prefix: str = "") -> None:
        """Not an actual validation, just env lookup"""

        for field in cls.__fields__:
            annotation = field.annotation

            if env_prefix:
                env_subprefix = f"{env_prefix}_{field.name.upper()}"
            else:
                env_subprefix = field.name.upper()

            if (raw_value := os.environ.get(env_subprefix)) is not None:
                # this is super wrong and broken. proper parsing needed
                value = annotation(raw_value)
            else:
                if data is Missing:
                    value = Missing
                else:
                    # does not understand Missing check for some reason
                    value = data.get(field.name, Missing)  # type: ignore

                # not a good indicator but issubclass/inspect.isclass behave weird with type aliases
                if hasattr(annotation, "__fields__"):
                    annotation.validate(value, env_subprefix)
                    value = annotation
                else:
                    if value is Missing:
                        if (value := field.default) is Missing:
                            raise Exception(f"Missing config value {field.name} / {env_subprefix}")
                    else:
                        # super ugly hack for basic types until proper conversion map for supported types is done
                        with contextlib.suppress(TypeError):
                            value = annotation(value)

            # this is wrong. we should do this on instance, not class
            setattr(cls, field.name, value)


SettingsT = TypeVar("SettingsT", bound="BaseSettings")


class BaseSettings(BaseModel):
    """TOML settings"""

    __config__: ClassVar[type[Config]]
    __data__: dict[str, Any]

    def __init__(self, *, data: Optional[dict[str, Any]] = None) -> None:
        if data is None:
            data = self.__loader_impl__()

        self.__data__ = data

        self.validate(data, self.__config__.env_prefix)

    def __loader_impl__(self) -> dict[str, Any]:
        settings_file = Path(self.__config__.settings_file)

        if self.__config__.loader == Loader.TOML:
            import tomllib

            with settings_file.open("rb") as f:
                return tomllib.load(f)
        elif self.__config__.loader == Loader.JSON:
            import json

            with settings_file.open() as f:
                return json.load(f)
        else:
            raise NotImplementedError(f"Unknown loader {self.__config__.loader}")

    def subsettings(self, settings: type[SettingsT]) -> SettingsT:
        data = self.__data__

        subsections = settings.__config__.section.split(".")
        for subsection in subsections:
            data = data[subsection]

        if env_prefix := settings.__config__.env_prefix:
            settings.__config__.env_prefix = f"{env_prefix}_{'_'.join(subsections).upper()}"
        else:
            settings.__config__.env_prefix = "_".join(subsections).upper()

        return settings(data=data)

    class Config(BaseConfig):
        settings_file: str = "settings.toml"
        loader = Loader.TOML
        env_prefix = ""
        section = ""

    def __repr__(self) -> str:
        return f"<{type(self).__name__} data={self.__data__}>"


class BotSettings(BaseModel):
    token: str
    prefix: str


class DatabaseSettings(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str


class RedisSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 6379
    db: str = "0"


class SentrySettings(BaseSettings):
    dsn: Optional[str] = None


class OwnersSettings(BaseModel):
    ids: set[int] = set()  # noqa: RUF012
    mode: Literal["combine", "overwrite"] = "combine"


class Settings(BaseSettings):
    bot: BotSettings
    database: DatabaseSettings
    redis: RedisSettings
    sentry: SentrySettings
    owners: OwnersSettings

    class Config(BaseConfig):
        env_prefix = "PINK_BOT"


settings = Settings()
