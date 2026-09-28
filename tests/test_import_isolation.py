from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ImportIsolationTests(unittest.TestCase):
    def test_retrieval_config_import_does_not_load_pdfplumber(self) -> None:
        code = (
            "import sys; "
            f"sys.path.insert(0, {str(ROOT / 'src')!r}); "
            "import testrx_retriever.configuration; "
            "assert 'pdfplumber' not in sys.modules"
        )
        completed = subprocess.run([sys.executable, "-c", code], check=False)
        self.assertEqual(completed.returncode, 0)
