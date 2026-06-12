"""Fixtures compartidos para todos los tests."""

import pytest
import pandas as pd
import numpy as np
from config import SimulationConfig


@pytest.fixture
def config() -> SimulationConfig:
    """Configuracion por defecto para tests."""
    return SimulationConfig(ITERATIONS=100, SEED=42)


@pytest.fixture
def rng() -> np.random.Generator:
    """Generator reproducible para tests."""
    return np.random.default_rng(42)


@pytest.fixture
def sample_matches_df() -> pd.DataFrame:
    """Dataset minimo de partidos historicos para tests."""
    np.random.seed(42)
    teams = ["A", "B", "C", "D", "E", "F"]
    rows = []
    for year in range(2005, 2025):
        for t1 in teams:
            for t2 in teams:
                if t1 >= t2:
                    continue
                rows.append({
                    "date": f"{year}-06-15",
                    "home_team": t1,
                    "away_team": t2,
                    "home_score": np.random.poisson(1.5),
                    "away_score": np.random.poisson(1.0),
                    "tournament": "FIFA World Cup",
                    "neutral": False,
                    "country": "Neutral",
                })
    return pd.DataFrame(rows)


@pytest.fixture
def teams_df() -> pd.DataFrame:
    """Fixture con datos basicos de selecciones para tests."""
    return pd.DataFrame({
        "name": list("ABCDEFGH"),
        "group": list("AABBBCCD"),
        "fifa_rank": [1, 2, 3, 4, 5, 6, 7, 8],
    })
