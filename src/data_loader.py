"""Carga y preprocesamiento del dataset historico de partidos (SPEC Section 3 y 4.1)."""

import pandas as pd
import numpy as np
from config import SimulationConfig


def classify_tournament(tournament: str) -> str:
    """Clasifica un torneo en categorias de peso (SPEC 4.1.2)."""
    t = tournament.lower()
    if "world cup" in t and "qualif" not in t and "women" not in t:
        return "FIFA World Cup"
    if "qualif" in t:
        return "FIFA World Cup qualification"
    known = {
        "Friendly", "Copa America", "UEFA Euro", "African Cup of Nations",
        "AFC Asian Cup", "CONCACAF Gold Cup", "OFC Nations Cup",
        "Confederation Cup",
    }
    if tournament in known:
        return tournament
    return "default"


def compute_weights(df: pd.DataFrame, config: SimulationConfig) -> pd.DataFrame:
    """Anade columna 'weight' a un DataFrame de partidos (SPEC 4.1).

    Clasifica torneos, calcula decaimiento temporal lineal con minimo 0.2 y combina ambos pesos.
    No modifica el DataFrame original.
    """
    result = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(result["date"]):
        result["date"] = pd.to_datetime(result["date"])
    if "tournament_category" not in result.columns:
        result["tournament_category"] = result["tournament"].map(classify_tournament)

    current_year = config.YEAR_MAX
    result["years_ago"] = current_year - result["date"].dt.year
    window_size = config.YEAR_MAX - config.YEAR_MIN
    result["time_weight"] = 1.0 - 0.8 * result["years_ago"] / window_size

    result["weight"] = (
        result["time_weight"]
        * result["tournament_category"].map(config.TOURNAMENT_WEIGHTS).fillna(0.5)
    )

    return result


def load_matches(filepath: str, config: SimulationConfig) -> pd.DataFrame:
    """Carga y limpia el dataset historico (SPEC 3.2, 3.3).

    Filtra por ventana temporal, clasifica torneos y calcula pesos.
    """
    df = pd.read_csv(filepath, parse_dates=["date"])

    df = df[(df["date"].dt.year >= config.YEAR_MIN) &
            (df["date"].dt.year <= config.YEAR_MAX)].copy()

    if "neutral" not in df.columns:
        df["neutral"] = False

    df["tournament_category"] = df["tournament"].map(classify_tournament)

    df = compute_weights(df, config)

    return df


def build_strength_matrix(
    matches: pd.DataFrame, config: SimulationConfig,
) -> dict[tuple[str, str], float]:
    """Construye matriz de fuerza historica entre pares de selecciones (SPEC 4.1.4).

    Para cada par (team_a, team_b) calcula el promedio ponderado de goles
    anotados por team_a cuando enfrento a team_b. Usa los pesos combinados
    (temporales + torneo).
    """
    pairs: dict[tuple[str, str], list[float]] = {}

    for _, row in matches.iterrows():
        pair_home = (row["home_team"], row["away_team"])
        pair_away = (row["away_team"], row["home_team"])

        w = row["weight"]

        pairs.setdefault(pair_home, []).append(w * row["home_score"])
        pairs.setdefault(pair_away, []).append(w * row["away_score"])

    matrix: dict[tuple[str, str], float] = {}
    for pair, values in pairs.items():
        matrix[pair] = float(np.average(values)) if values else 0.0

    return matrix


def get_team_lambdas(
    team1: str,
    team2: str,
    strength_matrix: dict[tuple[str, str], float],
    config: SimulationConfig,
    teams_df: pd.DataFrame | None = None,
) -> tuple[float, float]:
    """Calcula los lambdas Poisson para un enfrentamiento (SPEC 4.2).

    Usa datos historicos directos si hay al menos MIN_MATCHES partidos.
    Sino, usa proxy por ranking FIFA (SPEC 4.3).
    """
    key12 = (team1, team2)
    key21 = (team2, team1)

    s12 = strength_matrix.get(key12)
    s21 = strength_matrix.get(key21)

    if s12 is not None and s21 is not None and (s12 + s21) > 0:
        total = s12 + s21
        lambda_1 = config.BASE_GOALS_PER_MATCH * s12 / total
        lambda_2 = config.BASE_GOALS_PER_MATCH * s21 / total
    elif teams_df is not None:
        lambda_1, lambda_2 = get_proxy_lambdas(team1, team2, teams_df, config)
    else:
        lambda_1 = config.BASE_GOALS_PER_MATCH / 2
        lambda_2 = config.BASE_GOALS_PER_MATCH / 2

    return max(lambda_1, 0.01), max(lambda_2, 0.01)


def get_proxy_lambdas(
    team1: str, team2: str, teams_df: pd.DataFrame, config: SimulationConfig,
) -> tuple[float, float]:
    """Calcula lambda usando ranking FIFA como proxy (SPEC 4.3).

    Convierte ranking a fuerza con transformacion logaritmica suave.
    """
    def rank_to_strength(rank: int) -> float:
        return 1.0 / (1.0 + np.log(max(rank, 1)))

    r1 = teams_df.loc[teams_df["name"] == team1, "fifa_rank"].iloc[0]
    r2 = teams_df.loc[teams_df["name"] == team2, "fifa_rank"].iloc[0]

    s1 = rank_to_strength(r1)
    s2 = rank_to_strength(r2)
    total = s1 + s2

    lambda_1 = config.BASE_GOALS_PER_MATCH * s1 / total
    lambda_2 = config.BASE_GOALS_PER_MATCH * s2 / total

    return max(lambda_1, 0.01), max(lambda_2, 0.01)
