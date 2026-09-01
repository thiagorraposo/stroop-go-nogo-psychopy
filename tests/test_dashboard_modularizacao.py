import ast
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dashboard import app, components, data_access, transformations  # noqa: E402
from scripts import run_dashboard  # noqa: E402


MODULE_PATHS = {
    "app": ROOT / "dashboard" / "app.py",
    "components": ROOT / "dashboard" / "components.py",
    "data_access": ROOT / "dashboard" / "data_access.py",
    "transformations": ROOT / "dashboard" / "transformations.py",
}


def imported_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


class DashboardModularizacaoTests(unittest.TestCase):
    def test_api_publica_anterior_e_reexportada_pelo_app(self):
        self.assertIs(app.connect_readonly, data_access.connect_readonly)
        self.assertIs(app.load_sqlite_data, data_access.load_sqlite_data)
        self.assertIs(app.DashboardDataError, data_access.DashboardDataError)
        self.assertIs(app.DashboardFilters, transformations.DashboardFilters)
        self.assertIs(app.build_assessment_table, transformations.build_assessment_table)
        self.assertIs(app.calculate_cards, transformations.calculate_cards)
        self.assertIs(app.render_metric_card, components.render_metric_card)

    def test_dependencias_apontam_para_a_interface_sem_ciclos(self):
        data_imports = imported_modules(MODULE_PATHS["data_access"])
        transformation_imports = imported_modules(MODULE_PATHS["transformations"])
        component_imports = imported_modules(MODULE_PATHS["components"])
        app_imports = imported_modules(MODULE_PATHS["app"])

        self.assertFalse(any(name.startswith("dashboard") for name in data_imports))
        self.assertFalse(any(name.startswith("dashboard") for name in transformation_imports))
        self.assertEqual(
            {name for name in component_imports if name.startswith("dashboard")},
            {"dashboard.transformations"},
        )
        self.assertTrue(
            {
                "dashboard.components",
                "dashboard.data_access",
                "dashboard.transformations",
            }.issubset(app_imports)
        )

    def test_modulos_de_dados_importam_sem_iniciar_streamlit(self):
        code = (
            "import sys; "
            "import dashboard.data_access, dashboard.transformations; "
            "raise SystemExit(1 if 'streamlit' in sys.modules else 0)"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_launcher_preserva_app_como_ponto_de_entrada(self):
        self.assertEqual(run_dashboard.DASHBOARD_APP, ROOT / "dashboard" / "app.py")
        command = run_dashboard.build_streamlit_command(Path("python-sintetico"))
        self.assertEqual(command[-2:], ["run", str(run_dashboard.DASHBOARD_APP)])


if __name__ == "__main__":
    unittest.main()
