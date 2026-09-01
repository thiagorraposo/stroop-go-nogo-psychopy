"""Regressoes estaticas da infraestrutura local da Etapa 3."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InfraestruturaDockerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        cls.dockerfile = (ROOT / "Dockerfile.dashboard").read_text(encoding="utf-8")
        cls.dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        cls.env_example = (ROOT / ".env.example").read_text(encoding="utf-8")

    def test_servicos_dashboard_e_postgres_separados(self) -> None:
        self.assertRegex(self.compose, r"(?m)^  postgres:$")
        self.assertRegex(self.compose, r"(?m)^  dashboard:$")
        self.assertIn("image: postgres:17.6-bookworm", self.compose)

    def test_postgres_tem_volume_e_healthcheck(self) -> None:
        self.assertIn("postgres_data:/var/lib/postgresql/data", self.compose)
        self.assertIn("pg_isready", self.compose)
        self.assertRegex(self.compose, r"(?m)^volumes:\n  postgres_data:$")

    def test_dashboard_aguarda_saude_do_postgres(self) -> None:
        self.assertIn("condition: service_healthy", self.compose)
        self.assertIn("DATABASE_URL: postgresql://", self.compose)

    def test_imagem_preserva_ponto_de_entrada_e_nao_instala_psychopy(self) -> None:
        self.assertIn('"dashboard/app.py"', self.dockerfile)
        self.assertNotIn("psychopy", self.dockerfile.lower())
        self.assertIn("COPY dashboard /app/dashboard", self.dockerfile)

    def test_contexto_exclui_dados_e_segredos(self) -> None:
        exclusions = {
            ".env",
            "data",
            "database",
            "backups",
            "*.sqlite3",
            "*.pem",
            "*.key",
        }
        self.assertTrue(exclusions.issubset(set(self.dockerignore.splitlines())))

    def test_exemplo_de_ambiente_e_ficticio(self) -> None:
        self.assertIn("POSTGRES_DB=stroop_dev", self.env_example)
        self.assertIn("POSTGRES_USER=stroop_dev", self.env_example)
        self.assertIn("POSTGRES_PASSWORD=troque-esta-senha-local", self.env_example)
        self.assertNotRegex(self.env_example, re.compile(r"participant", re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
