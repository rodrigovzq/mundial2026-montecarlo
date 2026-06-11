"""Modelo estadistico para simulacion de partidos (SPEC Section 4)."""

import numpy as np
import pandas as pd
from config import SimulationConfig
from src.data_loader import (
    build_strength_matrix,
    compute_weights,
    get_team_lambdas,
)


class MatchPredictor:
    """Predice resultados de partidos usando modelo Poisson (SPEC 4.2).

    Construye una matriz de fuerza historica entre pares de selecciones
    y la usa para muestrear goles con distribucion Poisson.
    """

    def __init__(
        self,
        matches: pd.DataFrame,
        config: SimulationConfig,
        teams_df: pd.DataFrame | None = None,
    ):
        self.config = config
        self.teams_df = teams_df
        if "weight" not in matches.columns:
            matches = compute_weights(matches, config)
        self.strength_matrix = build_strength_matrix(matches, config)

    def get_lambdas(self, team1: str, team2: str) -> tuple[float, float]:
        """Obtiene los lambdas Poisson para team1 vs team2.
        
        Delega en data_loader.get_team_lambdas() que maneja proxy
        por ranking FIFA si no hay datos historicos suficientes.
        """
        return get_team_lambdas(
            team1, team2, self.strength_matrix, self.config, self.teams_df,
        )

    def predict(self, team1: str, team2: str, rng: np.random.Generator) -> tuple[int, int]:
        """Simula un partido completo usando la distribucion de Poisson (SPEC 4.2)."""
        lambda1, lambda2 = self.get_lambdas(team1, team2)
        return (int(rng.poisson(lambda1)), int(rng.poisson(lambda2)))

    def predict_most_likely(self, team1: str, team2: str) -> tuple[int, int]:
        """Predice el resultado mas probable (moda de Poisson) sin aleatoriedad.

        La moda de Poisson(lambda) es int(floor(lambda)).
        Esto da el resultado esperado 'promedio' del partido.
        """
        lambda1, lambda2 = self.get_lambdas(team1, team2)
        return (int(np.floor(lambda1)), int(np.floor(lambda2)))

    def simulate_extra_time(
        self, team1: str, team2: str, rng: np.random.Generator,
    ) -> tuple[int, int]:
        """Simula alargue (30 min) con tasa reducida de goles (SPEC 4.2.4)."""
        lambda_1, lambda_2 = self.get_lambdas(team1, team2)
        factor = self.config.EXTRA_TIME_GOAL_FACTOR
        goals_1 = int(rng.poisson(lambda_1 * factor))
        goals_2 = int(rng.poisson(lambda_2 * factor))
        return goals_1, goals_2

    def simulate_penalties(
        self, team1: str, team2: str, rng: np.random.Generator,
    ) -> tuple[str, str]:
        """Simula tanda de penales con sesgo hacia el equipo mas fuerte (SPEC 4.2.4).

        Returns:
            Tupla (ganador, perdedor).
        """
        lambda_1, lambda_2 = self.get_lambdas(team1, team2)
        total = lambda_1 + lambda_2
        if total > 0:
            strength_diff = (lambda_1 - lambda_2) / total
        else:
            strength_diff = 0.0

        bias = np.clip(
            strength_diff * self.config.PENALTY_BIAS,
            -self.config.PENALTY_BIAS,
            self.config.PENALTY_BIAS,
        )
        team1_win_prob = 0.5 + bias
        team1_win_prob = np.clip(team1_win_prob, 0.05, 0.95)

        if rng.random() < team1_win_prob:
            return team1, team2
        return team2, team1
