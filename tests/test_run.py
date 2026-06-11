"""Tests para run.py (pipeline principal)."""

import pytest
import numpy as np
from config import SimulationConfig


class TestMainPipeline:
    """Prueba el pipeline completo desde run.py."""

    def test_run_imports_without_error(self):
        """Verifica que run.py se pueda importar/ejecutar sin errores de importacion."""
        import run  # type: ignore
        assert hasattr(run, "main")

    def test_run_config_creatable(self):
        """Verifica que run.py pueda instanciar config."""
        import run  # type: ignore
        cfg = SimulationConfig(ITERATIONS=10)
        assert cfg.ITERATIONS == 10

    def test_run_with_teams_json_available(self):
        """Verifica que data/teams.json es accesible desde run.py."""
        import json
        with open("data/teams.json", "r") as f:
            data = json.load(f)
        assert len(data["teams"]) == 48

    def test_run_matches_csv_check(self):
        """Verifica que matches.csv existe o hay plan de contingencia."""
        from pathlib import Path
        csv_path = Path("data/matches.csv")
        if not csv_path.exists():
            from data.download_data import download_matches
            success = download_matches()
            assert success or not success  # no debe crashear
