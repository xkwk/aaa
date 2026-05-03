from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re


DEFAULT_DATABASE = "ACTUARIAL_AI_DEV"


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @classmethod
    def discover(cls, start: Path | None = None) -> "ProjectPaths":
        root = (start or Path.cwd()).resolve()
        return cls(root=root)

    @property
    def converted_dir(self) -> Path:
        return self.root / "converted"

    @property
    def runs_dir(self) -> Path:
        return self.root / "runs"

    @property
    def wiki_dir(self) -> Path:
        return self.root / "wiki"

    def run_dir(self, run_id: str) -> Path:
        return self.runs_dir / run_id

    def converted_run_dir(self, run_id: str) -> Path:
        return self.converted_dir / run_id


@dataclass(frozen=True)
class SnowflakeSettings:
    account: str
    user: str
    password: str
    authenticator: str
    token: str
    role: str | None
    warehouse: str | None
    database: str
    schema_raw: str
    schema_curated: str
    schema_runs: str
    schema_app: str

    @classmethod
    def from_env(cls) -> "SnowflakeSettings":
        return cls(
            account=os.getenv("ACT_SNOWFLAKE_ACCOUNT", ""),
            user=os.getenv("ACT_SNOWFLAKE_USER", ""),
            password=os.getenv("ACT_SNOWFLAKE_PASSWORD", ""),
            authenticator=os.getenv("ACT_SNOWFLAKE_AUTHENTICATOR", "externalbrowser"),
            token=os.getenv("ACT_SNOWFLAKE_TOKEN", ""),
            role=os.getenv("ACT_SNOWFLAKE_ROLE") or None,
            warehouse=os.getenv("ACT_SNOWFLAKE_WAREHOUSE") or None,
            database=os.getenv("ACT_SNOWFLAKE_DATABASE", DEFAULT_DATABASE),
            schema_raw=os.getenv("ACT_SNOWFLAKE_SCHEMA_RAW", "RAW"),
            schema_curated=os.getenv("ACT_SNOWFLAKE_SCHEMA_CURATED", "CURATED"),
            schema_runs=os.getenv("ACT_SNOWFLAKE_SCHEMA_RUNS", "RUNS"),
            schema_app=os.getenv("ACT_SNOWFLAKE_SCHEMA_APP", "APP"),
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


def snowflake_ident(value: str) -> str:
    """Return a safe Snowflake identifier for configured object names."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError(f"Unsafe Snowflake identifier: {value!r}")
    return value.upper()
