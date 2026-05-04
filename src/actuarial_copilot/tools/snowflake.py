"""Snowflake posture and object proposal capability."""

from __future__ import annotations

from dataclasses import asdict

from ..config import SnowflakeSettings, safe_identifier


def inspect_snowflake() -> dict:
    """Return Snowflake connection posture without opening a connection."""
    settings = SnowflakeSettings.from_env()
    payload = asdict(settings)
    payload["password"] = "***" if settings.password else ""
    payload["token"] = "***" if settings.token else ""
    payload["is_configured"] = settings.is_configured
    return payload


def propose_snowflake_objects(domain_hint: str, source_profile: dict | None = None) -> dict:
    """Propose object names only; the LLM decides whether they make sense."""
    domain = safe_identifier(domain_hint)
    objects = {
        "raw": f"RAW.{domain}_SOURCE",
        "curated": f"CURATED.{domain}_RESULTS",
        "app": f"APP.{domain}_DASHBOARD",
    }
    notes = ["Names are draft proposals generated from the domain hint."]
    if source_profile:
        tabular = [file for file in source_profile.get("files", []) if file.get("kind") == "tabular"]
        notes.append(f"Source profile contains {len(tabular)} tabular file(s).")
    return {"domain_hint": domain_hint, "objects": objects, "notes": notes}
