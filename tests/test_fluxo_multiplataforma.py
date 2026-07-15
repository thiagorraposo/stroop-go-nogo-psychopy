import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import run_dashboard  # noqa: E402
import setup_env  # noqa: E402


class FluxoMultiplataformaTests(unittest.TestCase):
    def test_detecta_sistema_operacional(self):
        with patch("platform.system", return_value="Windows"):
            self.assertEqual(setup_env.operating_system(), "Windows")

    def test_resolve_python_da_venv_por_sistema(self):
        root = Path("projeto") / ".venv"
        self.assertEqual(
            setup_env.venv_python_path(root, "Windows"),
            root / "Scripts" / "python.exe",
        )
        self.assertEqual(
            run_dashboard.venv_python_path(root, "Linux"), root / "bin" / "python"
        )
        self.assertEqual(
            run_dashboard.venv_python_path(root, "Darwin"), root / "bin" / "python"
        )

    def test_localiza_csv_mais_recente_sem_alterar_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            older = data_dir / "a_trials.csv"
            newer = data_dir / "b_trials.csv"
            ignored = data_dir / "outro.csv"
            older.write_text("antigo", encoding="utf-8")
            newer.write_text("novo", encoding="utf-8")
            ignored.write_text("ignorado", encoding="utf-8")
            os.utime(older, (1, 1))
            os.utime(newer, (2, 2))
            before = {path.name: path.read_bytes() for path in data_dir.iterdir()}

            selected = run_dashboard.find_latest_csv(data_dir)

            after = {path.name: path.read_bytes() for path in data_dir.iterdir()}
            self.assertEqual(selected, newer)
            self.assertEqual(before, after)

    def test_ausencia_de_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(run_dashboard.find_latest_csv(Path(tmp)))

    def test_ausencia_de_venv_retorna_erro_sem_subprocesso(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
            run_dashboard, "VENV_DIR", Path(tmp) / ".venv"
        ), patch("run_dashboard.subprocess.run") as mocked_run:
            self.assertEqual(run_dashboard.main([]), 1)
            mocked_run.assert_not_called()

    def test_comando_streamlit_nao_usa_shell(self):
        python_path = Path(".venv") / "bin" / "python"
        command = run_dashboard.build_streamlit_command(python_path)
        self.assertEqual(command[:4], [str(python_path), "-m", "streamlit", "run"])
        self.assertIsInstance(command, list)
        self.assertNotIn("shell", command)


if __name__ == "__main__":
    unittest.main()
