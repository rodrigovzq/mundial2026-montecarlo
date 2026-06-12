"""Tests para src/visualize.py (SPEC Section 7)."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path


class TestPlotConvergence:
    """Prueba el grafico de convergencia (SPEC 7.1)."""

    def test_plot_convergence_creates_file(self, tmp_path):
        from src.visualize import plot_convergence
        snapshots = _make_sample_snapshots()
        output = tmp_path / "convergence.png"
        plot_convergence(snapshots, str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_plot_convergence_dark_theme(self, tmp_path):
        from src.visualize import plot_convergence
        snapshots = _make_sample_snapshots()
        output = tmp_path / "dark_test.png"
        plot_convergence(snapshots, str(output))
        assert output.exists()


class TestBuildTop10Table:
    """Prueba la tabla Top 10 (SPEC 7.2)."""

    def test_build_top10_table_returns_dataframe(self):
        from src.visualize import build_top10_table
        winner_counts = {"Argentina": 30, "Brazil": 25, "France": 20, "Germany": 15, "Spain": 10}
        result = build_top10_table(winner_counts, 100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5

    def test_top10_table_has_correct_columns(self):
        from src.visualize import build_top10_table
        winner_counts = {"Argentina": 30, "Brazil": 25}
        result = build_top10_table(winner_counts, 100)
        assert "Seleccion" in result.columns
        assert "Probabilidad de ganar" in result.columns
        assert "#" in result.columns

    def test_top10_limits_to_10_rows(self):
        from src.visualize import build_top10_table
        teams = {f"Team{i}": i for i in range(1, 20)}
        result = build_top10_table(teams, 100)
        assert len(result) == 10

    def test_top10_sorted_by_probability_desc(self):
        from src.visualize import build_top10_table
        winner_counts = {"A": 50, "B": 30, "C": 20}
        result = build_top10_table(winner_counts, 100)
        probs = result["Probabilidad de ganar"].tolist()
        for i in range(len(probs) - 1):
            pct_i = float(probs[i].replace("%", ""))
            pct_ip1 = float(probs[i + 1].replace("%", ""))
            assert pct_i >= pct_ip1

    def test_probabilities_sum_reasonable(self):
        from src.visualize import build_top10_table
        winner_counts = {"A": 30, "B": 25, "C": 20, "D": 15, "E": 10}
        result = build_top10_table(winner_counts, 100)
        total = sum(float(p.replace("%", "")) for p in result["Probabilidad de ganar"])
        assert abs(total - 100.0) < 1.0


class TestExportTop10:
    """Prueba la exportacion a CSV (SPEC 7.2)."""

    def test_export_top10_creates_csv(self, tmp_path):
        from src.visualize import export_top10
        winner_counts = {"Argentina": 30, "Brazil": 25}
        output = tmp_path / "top10.csv"
        export_top10(winner_counts, 100, str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_export_top10_csv_readable(self, tmp_path):
        from src.visualize import export_top10
        winner_counts = {"Argentina": 30, "Brazil": 25}
        output = tmp_path / "top10.csv"
        export_top10(winner_counts, 100, str(output))

        df_check = pd.read_csv(output)
        assert "Seleccion" in df_check.columns
        assert len(df_check) == 2


class TestGroupStagePredictions:
    """Prueba la tabla de predicciones de fase de grupos."""

    def test_group_stage_predictions_returns_dataframe(self, sample_matches_df, config, teams_df):
        from src.visualize import build_group_stage_predictions_table
        from src.model import MatchPredictor
        predictor = MatchPredictor(sample_matches_df, config)
        result = build_group_stage_predictions_table(predictor, teams_df)
        assert isinstance(result, pd.DataFrame)

    def test_group_stage_predictions_has_expected_columns(self, sample_matches_df, config, teams_df):
        from src.visualize import build_group_stage_predictions_table
        from src.model import MatchPredictor
        predictor = MatchPredictor(sample_matches_df, config)
        result = build_group_stage_predictions_table(predictor, teams_df)
        expected = {"Group", "Home", "Away", "Predicted Home Goals", "Predicted Away Goals"}
        assert expected.issubset(set(result.columns))

    def test_group_stage_predictions_saves_csv(self, sample_matches_df, config, teams_df, tmp_path):
        from src.visualize import build_group_stage_predictions_table
        from src.model import MatchPredictor
        predictor = MatchPredictor(sample_matches_df, config)
        output = tmp_path / "group_predictions.csv"
        build_group_stage_predictions_table(predictor, teams_df, str(output))
        assert output.exists()
        assert output.stat().st_size > 0


class TestExportGroupStagePredictions:
    """Prueba la exportacion de predicciones de grupo desde Monte Carlo."""

    def test_export_empty_df_does_not_crash(self, tmp_path):
        from src.visualize import export_group_stage_predictions
        empty_df = pd.DataFrame()
        result = export_group_stage_predictions(empty_df, str(tmp_path / "empty.csv"))
        assert result.empty

    def test_export_creates_csv(self, tmp_path):
        from src.visualize import export_group_stage_predictions
        df = pd.DataFrame([
            {"group": "A", "home": "A1", "away": "A2",
             "predicted_home_goals": 2, "predicted_away_goals": 1, "samples": 100},
        ])
        output = tmp_path / "group_preds.csv"
        export_group_stage_predictions(df, str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_export_csv_readable(self, tmp_path):
        from src.visualize import export_group_stage_predictions
        df = pd.DataFrame([
            {"group": "A", "home": "A1", "away": "A2",
             "predicted_home_goals": 2, "predicted_away_goals": 1, "samples": 100},
        ])
        output = tmp_path / "group_preds.csv"
        export_group_stage_predictions(df, str(output))
        df_check = pd.read_csv(output)
        assert "group" in df_check.columns
        assert "home" in df_check.columns
        assert "away" in df_check.columns
        assert "predicted_home_goals" in df_check.columns
        assert "predicted_away_goals" in df_check.columns
        assert "samples" in df_check.columns
        assert len(df_check) == 1

    def test_export_returns_dataframe(self, tmp_path):
        from src.visualize import export_group_stage_predictions
        df = pd.DataFrame([
            {"group": "A", "home": "A1", "away": "A2",
             "predicted_home_goals": 2, "predicted_away_goals": 1, "samples": 100},
        ])
        result = export_group_stage_predictions(df, str(tmp_path / "test.csv"))
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1


# Helpers
def _make_sample_snapshots() -> list[pd.DataFrame]:
    """Crea snapshots de prueba para tests de visualizacion."""
    snapshots = []
    for iteration in [100, 200, 300, 400, 500]:
        top = min(10, iteration // 10)
        teams = [f"Team{i}" for i in range(top)]
        probs = [100.0 / top] * top
        snapshots.append(pd.DataFrame({
            "team": teams,
            "probability": probs,
            "iteration": [iteration] * top,
        }))
    return snapshots
