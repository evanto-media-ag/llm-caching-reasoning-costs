import tempfile
import unittest
from pathlib import Path

from lab.articles import check_article

CLAIMS = {"C-001": {"status": "bestätigt"}, "C-002": {"status": "offen"},
          "C-003": {"status": "nicht gemessen"}, "C-004": {"status": "nicht messbar"}}


def check(text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(text)
    return check_article(Path(f.name), CLAIMS)


class ArticleCheckTest(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(check("OpenAI cacht automatisch. <!-- claim:C-001 -->\n"), [])

    def test_unknown_claim_id(self):
        self.assertTrue(check("Satz. <!-- claim:C-999 -->"))

    def test_open_claim_rejected(self):
        self.assertTrue(check("Satz. <!-- claim:C-002 -->"))

    def test_not_measured_needs_label(self):
        self.assertTrue(check("OpenRouter hält Anfragen beim Anbieter. <!-- claim:C-003 -->"))
        self.assertEqual(check("OpenRouter hält Anfragen beim Anbieter (nicht gemessen). <!-- claim:C-003 -->"), [])
        self.assertEqual(check("OpenRouter keeps requests on one provider (not measured). <!-- claim:C-003 -->"), [])
        self.assertTrue(check("Mistral bietet keine Usage-API. <!-- claim:C-004 -->"))
        self.assertEqual(check("Mistral bietet keine Usage-API (nicht messbar). <!-- claim:C-004 -->"), [])
        self.assertEqual(check("No Mistral usage API (not measurable). <!-- claim:C-004 -->"), [])


if __name__ == "__main__":
    unittest.main()
