"""Tests para src/simulation.py (SPEC Section 6)."""

import pytest
import pandas as pd
import numpy as np
from config import SimulationConfig
from src.model import MatchPredictor


class TestRunSimulation:
    """Prueba el motor Montecarlo (SPEC 6.2)."""

    def test_run_returns_counts_and_snapshots(self, sample_matches_df, config):
        from src.simulation import run_simulation
        predictor = MatchPredictor(sample_matches_df, config)
        rng = np.random.default_rng(42)

        counts, snapshots, match_scores = run_simulation(predictor, config, rng)
        assert isinstance(counts, dict)
        assert isinstance(snapshots, list)
        assert isinstance(match_scores, dict)

    def test_counts_sum_to_iterations(self, sample_matches_df, config):
        from src.simulation import run_simulation
        predictor = MatchPredictor(sample_matches_df, config)
        rng = np.random.default_rng(42)

        counts, _, _ = run_simulation(predictor, config, rng)
        total = sum(counts.values())
        assert total == config.ITERATIONS

    def test_snapshots_every_100_iterations(self, sample_matches_df, config):
        from src.simulation import run_simulation
        predictor = MatchPredictor(sample_matches_df, config)
        rng = np.random.default_rng(42)

        _, snapshots, _ = run_simulation(predictor, config, rng)
        expected_snapshots = config.ITERATIONS // 100
        assert len(snapshots) == expected_snapshots

    def test_snapshot_contains_top_10(self, sample_matches_df, config):
        from src.simulation import run_simulation
        predictor = MatchPredictor(sample_matches_df, config)
        rng = np.random.default_rng(42)

        _, snapshots, _ = run_simulation(predictor, config, rng)
        last_snap = snapshots[-1]
        assert "team" in last_snap.columns
        assert "probability" in last_snap.columns
        assert "iteration" in last_snap.columns
        assert len(last_snap) == 10

    def test_probabilities_in_snapshot_sum_to_100(self, sample_matches_df, config):
        from src.simulation import run_simulation
        predictor = MatchPredictor(sample_matches_df, config)
        rng = np.random.default_rng(42)

        _, snapshots, _ = run_simulation(predictor, config, rng)
        last_snap = snapshots[-1]
        total_prob = last_snap["probability"].sum()
        assert abs(total_prob - 100.0) < 1.0

    def test_reproducible_with_same_seed(self, sample_matches_df, config):
        from src.simulation import run_simulation
        predictor = MatchPredictor(sample_matches_df, config)

        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)

        counts1, _, _ = run_simulation(predictor, config, rng1)
        counts2, _, _ = run_simulation(predictor, config, rng2)

        assert counts1 == counts2

    def test_different_seed_gives_different_counts(self, sample_matches_df, config):
        from src.simulation import run_simulation
        predictor = MatchPredictor(sample_matches_df, config)

        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(99)

        counts1, _, _ = run_simulation(predictor, config, rng1)
        counts2, _, _ = run_simulation(predictor, config, rng2)

        assert counts1 != counts2

    def test_snapshot_probability_evolution(self, sample_matches_df, config):
        from src.simulation import run_simulation
        predictor = MatchPredictor(sample_matches_df, config)
        rng = np.random.default_rng(42)

        _, snapshots, _ = run_simulation(predictor, config, rng)
        for i, snap in enumerate(snapshots):
            assert (snap["iteration"] == (i + 1) * 100).all()

    def test_returns_match_score_counts(self, sample_matches_df, config):
        from src.simulation import run_simulation
        predictor = MatchPredictor(sample_matches_df, config)
        rng = np.random.default_rng(42)
        _, _, match_scores = run_simulation(predictor, config, rng)
        assert isinstance(match_scores, dict)
        # At least some match scores should be tracked
        if match_scores:
            key = list(match_scores.keys())[0]
            assert len(key) == 3  # (group, home, away)
            scores = match_scores[key]
            total = sum(scores.values())
            assert total > 0
