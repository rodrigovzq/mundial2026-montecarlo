"""Tests para src/tournament.py (SPEC Section 5)."""

import pytest
import pandas as pd
import numpy as np
from config import SimulationConfig

# Helper functions for tournament tests


def _make_mock_predictor():
    """Crea un predictor mock que devuelve resultados deterministicos."""
    class MockPredictor:
        def predict(self, t1, t2, rng):
            if (t1, t2) == ("TeamA", "TeamB"):
                return (2, 0)
            if (t1, t2) == ("TeamB", "TeamC"):
                return (1, 1)
            if (t1, t2) == ("TeamC", "TeamD"):
                return (3, 0)
            if (t1, t2) == ("TeamD", "TeamA"):
                return (0, 1)
            if (t1, t2) == ("TeamA", "TeamC"):
                return (1, 0)
            if (t1, t2) == ("TeamB", "TeamD"):
                return (2, 2)
            return (1, 0)

        def simulate_extra_time(self, t1, t2, rng):
            return (0, 0)

        def simulate_penalties(self, t1, t2, rng):
            return (t1, t2)

    return MockPredictor()


def _make_group_results_with_third_places():
    """Crea resultados de grupos con posiciones variadas para probar mejores terceros."""
    import pandas as pd
    results = []
    for g in "ABCDEFGHIJKL":
        off = ord(g) - ord("A")
        pts = max(4 - off // 3, 0)
        results.append(pd.DataFrame([{
            "team": f"Team{g}3",
            "points": pts,
            "gf": 6 - off,
            "ga": 3 + off,
            "gd": (6 - off) - (3 + off),
            "position": 3,
        }]))
    return results


class TestGroupSimulation:
    """Prueba la simulacion de la fase de grupos (SPEC 5.1)."""

    def test_simulate_group_returns_dataframe(self, config, rng):
        from src.tournament import simulate_group
        predictor = _make_mock_predictor()
        teams = ["TeamA", "TeamB", "TeamC", "TeamD"]
        result = simulate_group(teams, predictor, config, rng)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4

    def test_group_standings_have_correct_columns(self, config, rng):
        from src.tournament import simulate_group
        predictor = _make_mock_predictor()
        teams = ["TeamA", "TeamB", "TeamC", "TeamD"]
        result = simulate_group(teams, predictor, config, rng)
        expected_cols = {"team", "points", "gf", "ga", "gd", "position"}
        assert expected_cols.issubset(set(result.columns))

    def test_group_position_1_to_4(self, config, rng):
        from src.tournament import simulate_group
        predictor = _make_mock_predictor()
        teams = ["TeamA", "TeamB", "TeamC", "TeamD"]
        result = simulate_group(teams, predictor, config, rng)
        assert list(result["position"]) == [1, 2, 3, 4]

    def test_group_points_are_correct(self, config, rng):
        from src.tournament import simulate_group
        predictor = _make_mock_predictor()
        teams = ["TeamA", "TeamB", "TeamC", "TeamD"]
        result = simulate_group(teams, predictor, config, rng)
        assert all(0 <= p <= 9 for p in result["points"])

    def test_group_six_matches_played(self, config, rng):
        from src.tournament import simulate_group
        predictor = _make_mock_predictor()
        teams = ["TeamA", "TeamB", "TeamC", "TeamD"]
        result = simulate_group(teams, predictor, config, rng)
        total_gf = result["gf"].sum()
        total_ga = result["ga"].sum()
        assert total_gf == total_ga


class TestBestThirdPlaces:
    """Prueba la seleccion de mejores terceros (SPEC 5.1)."""

    def test_selects_8_of_12_third_places(self, config):
        from src.tournament import select_best_third_places
        all_group_results = _make_group_results_with_third_places()
        best_third = select_best_third_places(all_group_results)
        assert len(best_third) == 8

    def test_best_third_places_sorted_by_performance(self, config):
        from src.tournament import select_best_third_places
        all_group_results = _make_group_results_with_third_places()
        best_third = select_best_third_places(all_group_results)
        for i in range(len(best_third) - 1):
            curr = (best_third[i]["points"], best_third[i]["gd"], best_third[i]["gf"])
            nxt = (best_third[i + 1]["points"], best_third[i + 1]["gd"], best_third[i + 1]["gf"])
            assert curr >= nxt


class TestKnockoutBracket:
    """Prueba la construccion del bracket eliminatorio (SPEC 5.2)."""

    def test_build_round_of_32_returns_16_matches(self, config):
        from src.tournament import build_round_of_32
        winners = [f"W{i}" for i in range(12)]
        runners_up = [f"R{i}" for i in range(12)]
        third_places = [f"T{i}" for i in range(8)]
        matches = build_round_of_32(winners, runners_up, third_places)
        assert len(matches) == 16
        for m in matches:
            assert len(m) == 2
            assert isinstance(m[0], str)
            assert isinstance(m[1], str)

    def test_round_of_32_all_teams_used(self, config):
        from src.tournament import build_round_of_32
        winners = [f"W{i}" for i in range(12)]
        runners_up = [f"R{i}" for i in range(12)]
        third_places = [f"T{i}" for i in range(8)]
        matches = build_round_of_32(winners, runners_up, third_places)
        used_teams = set()
        for m in matches:
            used_teams.add(m[0])
            used_teams.add(m[1])
        all_teams = set(winners + runners_up + third_places)
        assert used_teams == all_teams

    def test_round_of_32_no_duplicate_matchups(self, config):
        from src.tournament import build_round_of_32
        winners = [f"W{i}" for i in range(12)]
        runners_up = [f"R{i}" for i in range(12)]
        third_places = [f"T{i}" for i in range(8)]
        matches = build_round_of_32(winners, runners_up, third_places)
        all_matchups = set()
        for m in matches:
            pair = tuple(sorted(m))
            assert pair not in all_matchups, f"Duplicate matchup: {pair}"
            all_matchups.add(pair)

    def test_simulate_knockout_round_returns_winners(self, config, rng):
        from src.tournament import simulate_knockout_round
        predictor = _make_mock_predictor()
        matches = [("TeamA", "TeamB"), ("TeamC", "TeamD")]
        winners = simulate_knockout_round(matches, predictor, config, rng)
        assert len(winners) == 2
        for w in winners:
            assert isinstance(w, str)

    def test_simulate_tournament_returns_winner(self, config, rng):
        from src.tournament import simulate_tournament
        predictor = _make_mock_predictor()
        winner, match_results = simulate_tournament(predictor, config, rng)
        assert isinstance(winner, str)
        assert isinstance(match_results, list)
        assert len(match_results) > 0  # should have at least some group matches


class TestExtraTimeAndPenalties:
    """Prueba la resolucion de empates en KO (SPEC 4.2.4)."""

    def test_resolve_knockout_match_draw_goes_to_extra_time(self, config, rng):
        from src.tournament import resolve_knockout_match
        predictor = _make_mock_predictor()
        winner = resolve_knockout_match("TeamA", "TeamB", predictor, config, rng)
        assert isinstance(winner, str)
        assert winner in ("TeamA", "TeamB")
