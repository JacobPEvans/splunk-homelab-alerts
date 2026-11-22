import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STANZA = "HomelabAlert - Mac memory used above threshold"


def stanza(text, name):
    start = text.index(f"[{name}]\n")
    end = text.find("\n[", start + 1)
    return text[start:] if end == -1 else text[start:end]


class MacMemoryHeadroomAlertTest(unittest.TestCase):
    def setUp(self):
        self.saved = (ROOT / "default/savedsearches.conf").read_text()
        self.macros = (ROOT / "default/macros.conf").read_text()

    def test_search_reads_system_metrics_memory_percent_per_host(self):
        body = stanza(self.saved, STANZA)

        self.assertIn(
            "search = index=llm sourcetype=mlx:metrics node_memory_used_percent=*",
            body,
        )
        self.assertIn(
            "stats avg(node_memory_used_percent) AS avg_used_pct count AS samples by host",
            body,
        )
        self.assertIn("alert.suppress.fields = host", body)

    def test_threshold_comes_from_the_shared_macro_and_needs_three_samples(self):
        body = stanza(self.saved, STANZA)

        self.assertIn(
            "where samples>=3 AND avg_used_pct > `homelab_mac_memory_used_pct_threshold`",
            body,
        )

    def test_window_is_five_minutes_on_a_five_minute_cadence(self):
        body = stanza(self.saved, STANZA)

        self.assertIn("dispatch.earliest_time = -5m", body)
        self.assertIn("cron_schedule = */5 * * * *", body)

    def test_detector_is_promoted(self):
        body = stanza(self.saved, STANZA)

        self.assertIn("\ndisabled = 0\n", body)
        self.assertNotIn("\ndisabled = 1\n", body)

    def test_threshold_macro_is_defined_once_at_ninety_percent(self):
        matches = re.findall(
            r"(?m)^\[homelab_mac_memory_used_pct_threshold\]\ndefinition = (.+)$",
            self.macros,
        )
        self.assertEqual(matches, ["90"])


if __name__ == "__main__":
    unittest.main()
