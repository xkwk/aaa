from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import SnowflakeSettings, snowflake_ident


def qualified(settings: SnowflakeSettings, schema: str, table: str) -> str:
    return ".".join(
        [
            snowflake_ident(settings.database),
            snowflake_ident(schema),
            snowflake_ident(table),
        ]
    )


def bootstrap_sql(settings: SnowflakeSettings | None = None) -> str:
    settings = settings or SnowflakeSettings.from_env()
    db = snowflake_ident(settings.database)
    raw = snowflake_ident(settings.schema_raw)
    curated = snowflake_ident(settings.schema_curated)
    runs = snowflake_ident(settings.schema_runs)
    app = snowflake_ident(settings.schema_app)
    return f"""
CREATE DATABASE IF NOT EXISTS {db};
CREATE SCHEMA IF NOT EXISTS {db}.{raw};
CREATE SCHEMA IF NOT EXISTS {db}.{curated};
CREATE SCHEMA IF NOT EXISTS {db}.{runs};
CREATE SCHEMA IF NOT EXISTS {db}.{app};

CREATE TABLE IF NOT EXISTS {db}.{raw}.FILE_MANIFEST (
  RUN_ID STRING,
  FILE_ID STRING,
  RELATIVE_PATH STRING,
  FILE_NAME STRING,
  ROLE STRING,
  SHA256 STRING,
  SIZE_BYTES NUMBER,
  MODIFIED_AT_UTC STRING,
  LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS {db}.{raw}.VALUATION_RESULTS (
  RUN_ID STRING,
  VALUATION_PERIOD STRING,
  PRODUCT STRING,
  PORTFOLIO STRING,
  COHORT STRING,
  MEASURE STRING,
  AMOUNT NUMBER(38, 10),
  CURRENCY STRING,
  LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS {db}.{raw}.VALUATION_BRIDGE (
  RUN_ID STRING,
  FROM_PERIOD STRING,
  TO_PERIOD STRING,
  PRODUCT STRING,
  PORTFOLIO STRING,
  MEASURE STRING,
  DRIVER STRING,
  AMOUNT NUMBER(38, 10),
  LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS {db}.{curated}.MOVEMENT_RESULTS (
  RUN_ID STRING,
  FROM_PERIOD STRING,
  TO_PERIOD STRING,
  PRODUCT STRING,
  PORTFOLIO STRING,
  MEASURE STRING,
  DRIVER STRING,
  AMOUNT NUMBER(38, 10),
  CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS {db}.{runs}.VALIDATION_RESULTS (
  RUN_ID STRING,
  CHECK_NAME STRING,
  STATUS STRING,
  SEVERITY STRING,
  MESSAGE STRING,
  DETAILS STRING,
  CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS {db}.{runs}.RUN_LOG (
  RUN_ID STRING,
  STEP STRING,
  STATUS STRING,
  MESSAGE STRING,
  CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS {db}.{app}.DASHBOARD_SUMMARY (
  RUN_ID STRING,
  FROM_PERIOD STRING,
  TO_PERIOD STRING,
  PRODUCT STRING,
  PORTFOLIO STRING,
  MEASURE STRING,
  DRIVER STRING,
  AMOUNT NUMBER(38, 10),
  CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
""".strip()


class SnowflakeRepository:
    def __init__(self, settings: SnowflakeSettings | None = None):
        self.settings = settings or SnowflakeSettings.from_env()
        if not self.settings.is_configured:
            raise RuntimeError("Snowflake credentials are not configured")

    def _connect(self):
        try:
            import snowflake.connector
        except ImportError as exc:
            raise RuntimeError("Install the snowflake extra to load Snowflake tables") from exc
        kwargs = {
            "account": self.settings.account,
            "user": self.settings.user,
            "database": self.settings.database,
            "authenticator": self.settings.authenticator,
        }
        if self.settings.authenticator == "snowflake":
            kwargs["password"] = self.settings.password
        elif self.settings.authenticator == "oauth":
            kwargs["token"] = self.settings.token
        if self.settings.role:
            kwargs["role"] = self.settings.role
        if self.settings.warehouse:
            kwargs["warehouse"] = self.settings.warehouse
        return snowflake.connector.connect(**kwargs)

    def bootstrap(self) -> None:
        sql = bootstrap_sql(self.settings)
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                for statement in [s.strip() for s in sql.split(";") if s.strip()]:
                    cursor.execute(statement)
            finally:
                cursor.close()

    def replace_rows(self, schema: str, table: str, run_id: str, columns: list[str], rows: Iterable[tuple]) -> None:
        target = qualified(self.settings, schema, table)
        placeholders = ", ".join(["%s"] * len(columns))
        column_list = ", ".join(columns)
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"DELETE FROM {target} WHERE RUN_ID = %s", (run_id,))
                rows = list(rows)
                if rows:
                    cursor.executemany(f"INSERT INTO {target} ({column_list}) VALUES ({placeholders})", rows)
            finally:
                cursor.close()

    def write_bootstrap_file(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(bootstrap_sql(self.settings) + "\n", encoding="utf-8")
