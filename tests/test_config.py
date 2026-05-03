from pathlib import Path
import os
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuarial_copilot.config import SnowflakeSettings


class SnowflakeSettingsTests(unittest.TestCase):
    def setUp(self):
        self.original = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original)

    def test_externalbrowser_is_default_and_does_not_require_password(self):
        os.environ.pop("ACT_SNOWFLAKE_AUTHENTICATOR", None)
        os.environ["ACT_SNOWFLAKE_ACCOUNT"] = "acct"
        os.environ["ACT_SNOWFLAKE_USER"] = "user@example.com"
        os.environ.pop("ACT_SNOWFLAKE_PASSWORD", None)

        settings = SnowflakeSettings.from_env()

        self.assertEqual(settings.authenticator, "externalbrowser")
        self.assertTrue(settings.is_configured)

    def test_password_auth_requires_password(self):
        os.environ["ACT_SNOWFLAKE_AUTHENTICATOR"] = "snowflake"
        os.environ["ACT_SNOWFLAKE_ACCOUNT"] = "acct"
        os.environ["ACT_SNOWFLAKE_USER"] = "user@example.com"
        os.environ.pop("ACT_SNOWFLAKE_PASSWORD", None)

        self.assertFalse(SnowflakeSettings.from_env().is_configured)


if __name__ == "__main__":
    unittest.main()

