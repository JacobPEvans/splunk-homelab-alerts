import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME = "HomelabAlert - GitHub runner OpenBao login failed"


def stanza(text, name):
    start = text.index(f"[{name}]\n")
    end = text.find("\n[", start + 1)
    return text[start:] if end == -1 else text[start:end]


class RunnerOpenBaoLoginAlertTest(unittest.TestCase):
    def setUp(self):
        self.body = stanza((ROOT / "default/savedsearches.conf").read_text(), NAME)

    def test_extracts_the_wrapped_audit_json_before_spath(self):
        self.assertIn('rex field=_raw "(?<j>\\{.*)"', self.body)
        self.assertIn("spath input=j", self.body)

    def test_matches_failed_approle_logins_from_runner_sources(self):
        self.assertIn('search type=response rpath="auth/approle/login" error=*', self.body)
        self.assertIn('search type=response role="github-runner"', self.body)
        self.assertIn("join type=inner src", self.body)

    def test_is_enabled_and_runs_every_five_minutes(self):
        self.assertIn("disabled = 0", self.body)
        self.assertIn("cron_schedule = */5 * * * *", self.body)
        self.assertIn("dispatch.earliest_time = -6m", self.body)
        self.assertIn("alert.suppress.period = 60m", self.body)


if __name__ == "__main__":
    unittest.main()
