import tempfile
import unittest
from pathlib import Path

from lab.claims import load_claims, set_status, validate_claims


def row(**over):
    base = {"id": "C-001", "claim_de": "x", "claim_en": "x", "source_url": "https://a", "source_date": "2026-10-18",
            "target": "anthropic", "model": "", "measurement": "M1", "status": "offen", "evidence": "", "measured_on": ""}
    base.update(over)
    return base


class ClaimsTest(unittest.TestCase):
    def test_register_valid(self):
        self.assertEqual(validate_claims(load_claims()), [])

    def test_rejects_unknown_status(self):
        self.assertTrue(validate_claims({"C-001": row(status="ok")}))

    def test_measured_requires_evidence(self):
        self.assertTrue(validate_claims({"C-001": row(status="bestätigt", evidence="data/missing.json")}))

    def test_measurement_ids(self):
        self.assertTrue(validate_claims({"C-001": row(measurement="M10")}))
        self.assertEqual(validate_claims({"C-001": row(measurement="", status="nicht messbar")}), [])

    def test_set_status_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "claims.csv"
            path.write_text("id,claim_de,claim_en,source_url,source_date,target,model,measurement,status,evidence,measured_on\n"
                            "C-001,a,b,https://a,2026-10-18,xai,,M1,offen,,\n")
            set_status(path, "C-001", "nicht gemessen", "", "2026-10-20")
            self.assertEqual(load_claims(path)["C-001"]["status"], "nicht gemessen")


if __name__ == "__main__":
    unittest.main()
