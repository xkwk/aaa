from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @classmethod
    def discover(cls, start: Path | None = None) -> "ProjectPaths":
        return cls(root=(start or Path.cwd()).resolve())


@dataclass(frozen=True)
class SnowflakeSettings:
    account: str
    user: str
    authenticator: str
    password: str
    token: str
    role: str | None
    warehouse: str | None
    database: str | None

    @classmethod
    def from_env(cls) -> "SnowflakeSettings":
        return cls(
            account=os.getenv("ACT_SNOWFLAKE_ACCOUNT", ""),
            user=os.getenv("ACT_SNOWFLAKE_USER", ""),
            authenticator=os.getenv("ACT_SNOWFLAKE_AUTHENTICATOR", "externalbrowser"),
            password=os.getenv("ACT_SNOWFLAKE_PASSWORD", ""),
            token=os.getenv("ACT_SNOWFLAKE_TOKEN", ""),
            role=os.getenv("ACT_SNOWFLAKE_ROLE") or None,
            warehouse=os.getenv("ACT_SNOWFLAKE_WAREHOUSE") or None,
            database=os.getenv("ACT_SNOWFLAKE_DATABASE") or None,
        )

    @property
    def is_configured(self) -> bool:
        if not (self.account and self.user):
            return False
        if self.authenticator == "snowflake":
            return bool(self.password)
        if self.authenticator == "oauth":
            return bool(self.token)
        return True


def safe_identifier(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")
    if not cleaned:
        cleaned = "object"
    if cleaned[0].isdigit():
        cleaned = f"obj_{cleaned}"
    return cleaned.upper()

