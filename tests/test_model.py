"""Tests para src/model.py (SPEC Sections 4.2 y 4.3)."""

import pytest
import numpy as np
import pandas as pd
from config import SimulationConfig


class TestMatchPredictorInit:
    """Prueba la inicializacion del predictor."""

    def test_init_with_config(self, sample_matches_df, config):
        from src.model import MatchPredictor
        predictor = MatchPredictor(sample_matches_df, config)
        assert predictor.config is config

    def test_strength_matrix_built(self, sample_matches_df, config):
        from src.model import MatchPredictor
        predictor = MatchPredictor(sample_matches_df, config)
        assert hasattr(predictor, "strength_matrix")
        assert isinstance(predictor.strength_matrix, dict)


class TestMatchPredictorPredict:
    """Prueba el metodo predict (SPEC 4.2)."""

    def test_predict_returns_tuple_of_ints(self, sample_matches_df, config, rng):
        from src.model import MatchPredictor
        predictor = MatchPredictor(sample_matches_df, config)
        result = predictor.predict("A", "B", rng)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)

    def test_predict_most_likely_returns_deterministic(self, sample_matches_df, config):
        """predict_most_likely debe ser deterministico (sin RNG)."""
        from src.model import MatchPredictor
        predictor = MatchPredictor(sample_matches_df, config)
        result1 = predictor.predict_most_likely("A", "B")
        result2 = predictor.predict_most_likely("A", "B")
        assert result1 == result2

    def test_predict_most_likely_returns_two_ints(self, sample_matches_df, config):
        from src.model import MatchPredictor
        predictor = MatchPredictor(sample_matches_df, config)
        result = predictor.predict_most_likely("A", "B")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)

    def test_predict_non_negative_goals(self, sample_matches_df, config, rng):
        from src.model import MatchPredictor
        predictor = MatchPredictor(sample_matches_df, config)
        for _ in range(20):
            g1, g2 = predictor.predict("A", "B", rng)
            assert g1 >= 0
            assert g2 >= 0

    def test_predict_unknown_team_uses_proxy(self, config, rng):
        """Si no hay datos historicos, usa proxy y no crashea (SPEC 4.3)."""
        import pandas as pd
        tmp_data = {
            "date": pd.to_datetime(["2024-01-01"]),
            "home_team": ["France"],
            "away_team": ["Germany"],
            "home_score": [2],
            "away_score": [1],
            "tournament": ["Friendly"],
            "neutral": [False],
            "country": ["France"],
        }
        df = pd.DataFrame(tmp_data)

        teams_df = pd.DataFrame({
            "name": ["Argentina", "Brazil", "France", "Germany", "New Zealand"],
            "fifa_rank": [1, 3, 2, 9, 48],
            "group": ["A", "B", "C", "D", "L"],
        })

        from src.model import MatchPredictor
        predictor = MatchPredictor(df, config, teams_df)
        g1, g2 = predictor.predict("Argentina", "New Zealand", rng)
        assert isinstance(g1, int)
        assert isinstance(g2, int)
        assert g1 >= 0
        assert g2 >= 0

    def test_predict_is_reproducible_with_same_seed(self, sample_matches_df, config):
        """Misma semilla debe dar los mismos resultados."""
        from src.model import MatchPredictor
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)
        predictor = MatchPredictor(sample_matches_df, config)

        results1 = [predictor.predict("A", "B", rng1) for _ in range(10)]
        results2 = [predictor.predict("A", "B", rng2) for _ in range(10)]

        assert results1 == results2


class TestMatchPredictorExtraTime:
    """Prueba la simulacion de alargue (SPEC 4.2.4)."""

    def test_extra_time_returns_tuple(self, sample_matches_df, config, rng):
        from src.model import MatchPredictor
        predictor = MatchPredictor(sample_matches_df, config)
        result = predictor.simulate_extra_time("A", "B", rng)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)


class TestMatchPredictorPenalties:
    """Prueba la simulacion de penales (SPEC 4.2.4)."""

    def test_penalties_returns_winner_loser(self, sample_matches_df, config, rng):
        from src.model import MatchPredictor
        predictor = MatchPredictor(sample_matches_df, config)
        result = predictor.simulate_penalties("A", "B", rng)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] in ("A", "B")
        assert result[1] in ("A", "B")
        assert result[0] != result[1]

    def test_stronger_team_wins_more_often_penalties(self, config, rng):
        """El equipo con mejor ranking debe ganar penales mas seguido."""
        import pandas as pd
        teams_df = pd.DataFrame({
            "name": ["Brazil", "New Zealand"],
            "fifa_rank": [3, 48],
            "group": ["A", "B"],
        })
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01"]),
            "home_team": ["Brazil"],
            "away_team": ["New Zealand"],
            "home_score": [0],
            "away_score": [0],
            "tournament": ["Friendly"],
            "neutral": [False],
            "country": ["Brazil"],
        })
        from src.model import MatchPredictor
        predictor = MatchPredictor(df, config, teams_df)
        wins = 0
        trials = 500
        rng_local = np.random.default_rng(42)
        for _ in range(trials):
            w, _ = predictor.simulate_penalties("Brazil", "New Zealand", rng_local)
            if w == "Brazil":
                wins += 1
        assert wins > trials * 0.5
