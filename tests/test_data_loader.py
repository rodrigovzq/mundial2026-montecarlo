"""Tests para src/data_loader.py (SPEC Sections 3 y 4.1)."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path


class TestClassifyTournament:
    """Prueba la clasificacion de torneos en categorias."""

    def test_world_cup(self):
        from src.data_loader import classify_tournament
        assert classify_tournament("FIFA World Cup") == "FIFA World Cup"

    def test_qualification(self):
        from src.data_loader import classify_tournament
        result = classify_tournament("FIFA World Cup qualification CONMEBOL")
        assert result == "FIFA World Cup qualification"

    def test_friendly(self):
        from src.data_loader import classify_tournament
        assert classify_tournament("Friendly") == "Friendly"

    def test_continental_cup(self):
        from src.data_loader import classify_tournament
        assert classify_tournament("Copa America") == "Copa America"
        assert classify_tournament("UEFA Euro") == "UEFA Euro"
        assert classify_tournament("African Cup of Nations") == "African Cup of Nations"

    def test_unknown_tournament_defaults(self):
        from src.data_loader import classify_tournament
        assert classify_tournament("Some obscure cup") == "default"


class TestLoadMatches:
    """Prueba la carga y limpieza del dataset."""

    def test_returns_dataframe(self, sample_matches_df, tmp_path, config):
        from src.data_loader import load_matches
        csv_path = tmp_path / "matches.csv"
        sample_matches_df.to_csv(csv_path, index=False)
        result = load_matches(str(csv_path), config)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_filters_by_year(self, sample_matches_df, tmp_path, config):
        from src.data_loader import load_matches
        csv_path = tmp_path / "matches.csv"
        sample_matches_df.to_csv(csv_path, index=False)
        result = load_matches(str(csv_path), config)
        for _, row in result.iterrows():
            assert config.YEAR_MIN <= row["date"].year <= config.YEAR_MAX

    def test_contains_weight_column(self, sample_matches_df, tmp_path, config):
        from src.data_loader import load_matches
        csv_path = tmp_path / "matches.csv"
        sample_matches_df.to_csv(csv_path, index=False)
        result = load_matches(str(csv_path), config)
        assert "weight" in result.columns

    def test_weight_values_are_positive(self, sample_matches_df, tmp_path, config):
        from src.data_loader import load_matches
        csv_path = tmp_path / "matches.csv"
        sample_matches_df.to_csv(csv_path, index=False)
        result = load_matches(str(csv_path), config)
        assert (result["weight"] > 0).all()


class TestBuildStrengthMatrix:
    """Prueba la construccion de la matriz de fuerzas (SPEC 4.1.4)."""

    def test_returns_dict(self, sample_matches_df, tmp_path, config):
        from src.data_loader import load_matches
        csv_path = tmp_path / "matches.csv"
        sample_matches_df.to_csv(csv_path, index=False)
        matches = load_matches(str(csv_path), config)

        from src.data_loader import build_strength_matrix
        matrix = build_strength_matrix(matches, config)
        assert isinstance(matrix, dict)

    def test_strength_values_are_float(self, sample_matches_df, tmp_path, config):
        from src.data_loader import load_matches
        csv_path = tmp_path / "matches.csv"
        sample_matches_df.to_csv(csv_path, index=False)
        matches = load_matches(str(csv_path), config)

        from src.data_loader import build_strength_matrix
        matrix = build_strength_matrix(matches, config)
        for val in matrix.values():
            assert isinstance(val, float)


class TestGetTeamLambdas:
    """Prueba el calculo de lambda Poisson para un enfrentamiento (SPEC 4.3)."""

    def test_returns_two_floats(self, sample_matches_df, tmp_path, config):
        from src.data_loader import load_matches
        csv_path = tmp_path / "matches.csv"
        sample_matches_df.to_csv(csv_path, index=False)
        matches = load_matches(str(csv_path), config)

        from src.data_loader import build_strength_matrix
        matrix = build_strength_matrix(matches, config)

        from src.data_loader import get_team_lambdas
        l1, l2 = get_team_lambdas("A", "B", matrix, config)
        assert isinstance(l1, float)
        assert isinstance(l2, float)
        assert l1 > 0
        assert l2 > 0

    def test_proxy_for_unknown_pair(self, teams_df, config):
        """Si no hay datos directos, usa proxy basado en ranking (SPEC 4.3)."""
        from src.data_loader import get_proxy_lambdas
        l1, l2 = get_proxy_lambdas("A", "H", teams_df, config)
        assert isinstance(l1, float)
        assert isinstance(l2, float)
        assert l1 > 0
        assert l2 > 0

    def test_proxy_favors_higher_ranked_team(self, config):
        """El equipo mejor rankead debe tener lambda mas alto."""
        import pandas as pd
        df = pd.DataFrame({
            "name": ["Argentina", "New Zealand"],
            "fifa_rank": [1, 48],
            "group": ["A", "L"],
        })
        from src.data_loader import get_proxy_lambdas
        l_arg, l_nzl = get_proxy_lambdas("Argentina", "New Zealand", df, config)
        assert l_arg > l_nzl
