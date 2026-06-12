"""Motor de simulacion Montecarlo (SPEC Section 6)."""

import logging
from collections import Counter

import numpy as np
import pandas as pd
from tqdm import tqdm

from config import SimulationConfig
from src.model import MatchPredictor
from src.tournament import simulate_tournament

log = logging.getLogger(__name__)


def run_simulation(
    predictor: MatchPredictor,
    config: SimulationConfig,
    rng: np.random.Generator,
) -> tuple[dict[str, int], list[pd.DataFrame], dict[tuple[str, str, str], dict[str, int]]]:
    """Ejecuta el loop Montecarlo completo (SPEC 6.2).

    Args:
        predictor: Predictor de partidos con matriz de fuerza.
        config: Parametros de simulacion.
        rng: Generador de numeros aleatorios.

    Returns:
        Tupla (winner_counts, snapshots, match_score_counts):
        - winner_counts: dict {team_name: count}
        - snapshots: lista de DataFrames (uno cada 100 iteraciones) con top-10
        - match_score_counts: dict {(group, home, away): {score_str: count}}
    """
    winner_counts: dict[str, int] = Counter()
    snapshots: list[pd.DataFrame] = []
    match_score_counts: dict[tuple[str, str, str], dict[str, int]] = {}

    total = config.ITERATIONS
    pbar = tqdm(total=total, desc="Simulando mundiales", unit="iter")

    for i in range(1, total + 1):
        winner, match_results = simulate_tournament(predictor, config, rng)
        winner_counts[winner] = winner_counts.get(winner, 0) + 1

        # Track group match results
        for m in match_results:
            key = (m["group"], m["home"], m["away"])
            score_key = f"{m['goals_home']}-{m['goals_away']}"
            if key not in match_score_counts:
                match_score_counts[key] = {}
            match_score_counts[key][score_key] = match_score_counts[key].get(score_key, 0) + 1

        if i % 100 == 0:
            total_so_far = i
            top10 = sorted(
                winner_counts.items(), key=lambda x: -x[1]
            )[:10]

            # Normalize probabilities within top-10 to sum to 100%
            top10_total = sum(c for _, c in top10)
            snapshot = pd.DataFrame({
                "team": [t for t, _ in top10],
                "probability": [
                    c / top10_total * 100 if top10_total > 0 else 0.0
                    for _, c in top10
                ],
                "iteration": [total_so_far] * len(top10),
            })
            snapshots.append(snapshot)

        pbar.update(1)

    pbar.close()
    return dict(winner_counts), snapshots, match_score_counts
