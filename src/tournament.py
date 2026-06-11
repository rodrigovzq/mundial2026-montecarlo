"""Logica del torneo: fase de grupos y eliminatorias (SPEC Section 5)."""

import numpy as np
import pandas as pd
from config import SimulationConfig
from src.model import MatchPredictor


def simulate_group(
    teams: list[str],
    predictor: MatchPredictor,
    config: SimulationConfig,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Simula fase de grupos (todos contra todos, SPEC 5.1).

    Cada equipo juega contra los otros 3 de su grupo.
    Victoria = 3 puntos, empate = 1, derrota = 0.
    """
    standings = {
        t: {"team": t, "points": 0, "gf": 0, "ga": 0, "gd": 0}
        for t in teams
    }

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            home, away = teams[i], teams[j]
            g_home, g_away = predictor.predict(home, away, rng)

            standings[home]["gf"] += g_home
            standings[home]["ga"] += g_away
            standings[home]["gd"] += g_home - g_away
            standings[away]["gf"] += g_away
            standings[away]["ga"] += g_home
            standings[away]["gd"] += g_away - g_home

            if g_home > g_away:
                standings[home]["points"] += 3
            elif g_away > g_home:
                standings[away]["points"] += 3
            else:
                standings[home]["points"] += 1
                standings[away]["points"] += 1

    df = pd.DataFrame.from_records(list(standings.values()))
    df = df.sort_values(
        ["points", "gd", "gf"], ascending=False
    ).reset_index(drop=True)
    df.index += 1
    df["position"] = df.index
    return df


def select_best_third_places(
    all_group_results: list[pd.DataFrame],
) -> list[dict]:
    """Selecciona los 8 mejores terceros puestos de 12 grupos (SPEC 5.1)."""
    third_placed = []
    for group_df in all_group_results:
        third = group_df[group_df["position"] == 3].iloc[0].to_dict()
        third_placed.append(third)

    third_placed.sort(
        key=lambda t: (t["points"], t["gd"], t["gf"]),
        reverse=True,
    )
    return third_placed[:8]


def build_round_of_32(
    group_winners: list[str],
    group_runners_up: list[str],
    best_third_places: list[str],
) -> list[tuple[str, str]]:
    """Construye los enfrentamientos de 16avos de final (SPEC 5.2).

    Usa bracket semi-seed: los 12 ganadores se rankean, los 12 segundos
    tambien, y los 8 mejores terceros se asignan.
    """
    all_advancing = group_winners + group_runners_up + best_third_places

    bracket_indices = [
        (0, 31), (15, 16), (7, 24), (8, 23),
        (4, 27), (11, 20), (3, 28), (12, 19),
        (2, 29), (13, 18), (5, 26), (10, 21),
        (6, 25), (9, 22), (1, 30), (14, 17),
    ]

    matches = []
    for i, j in bracket_indices:
        if i < len(all_advancing) and j < len(all_advancing):
            matches.append((all_advancing[i], all_advancing[j]))

    return matches


def simulate_knockout_round(
    matches: list[tuple[str, str]],
    predictor: MatchPredictor,
    config: SimulationConfig,
    rng: np.random.Generator,
) -> list[str]:
    """Simula una ronda eliminatoria completa."""
    winners = []
    for home, away in matches:
        winner = resolve_knockout_match(home, away, predictor, config, rng)
        winners.append(winner)
    return winners


def resolve_knockout_match(
    team1: str,
    team2: str,
    predictor: MatchPredictor,
    config: SimulationConfig,
    rng: np.random.Generator,
) -> str:
    """Resuelve un partido eliminatorio con alargue y penales si es necesario (SPEC 4.2.4, 5.2)."""
    g1, g2 = predictor.predict(team1, team2, rng)

    if g1 != g2:
        return team1 if g1 > g2 else team2

    # Extra time (30 min)
    et1, et2 = predictor.simulate_extra_time(team1, team2, rng)
    if et1 != et2:
        return team1 if et1 > et2 else team2

    # Penalties
    winner, _ = predictor.simulate_penalties(team1, team2, rng)
    return winner


def simulate_tournament(
    predictor: MatchPredictor,
    config: SimulationConfig,
    rng: np.random.Generator,
    group_winners: list[str] | None = None,
    group_runners_up: list[str] | None = None,
    all_group_results: list[pd.DataFrame] | None = None,
) -> str:
    """Simula un torneo completo desde grupos hasta final, o desde KO si se proveen resultados."""
    if all_group_results is None:
        import json
        with open("data/teams.json", "r") as f:
            teams_data = json.load(f)

        groups: dict[str, list[str]] = {}
        for team in teams_data["teams"]:
            groups.setdefault(team["group"], []).append(team["name"])

        all_group_results = []
        for group_name in sorted(groups.keys()):
            grp = simulate_group(groups[group_name], predictor, config, rng)
            all_group_results.append(grp)

    group_winners = [g.iloc[0]["team"] for g in all_group_results]
    group_runners_up = [g.iloc[1]["team"] for g in all_group_results]
    best_third = select_best_third_places(all_group_results)

    third_team_names = [t["team"] for t in best_third]
    r32 = build_round_of_32(group_winners, group_runners_up, third_team_names)

    # Round of 32
    r16_winners = simulate_knockout_round(r32, predictor, config, rng)

    # Round of 16
    r16_matches = [(r16_winners[i], r16_winners[i + 1]) for i in range(0, 16, 2)]
    qf_winners = simulate_knockout_round(r16_matches, predictor, config, rng)

    # Quarterfinals
    qf_matches = [(qf_winners[i], qf_winners[i + 1]) for i in range(0, 8, 2)]
    sf_winners = simulate_knockout_round(qf_matches, predictor, config, rng)

    # Semifinals
    sf_matches = [(sf_winners[i], sf_winners[i + 1]) for i in range(0, 4, 2)]
    finalists = simulate_knockout_round(sf_matches, predictor, config, rng)

    # Final
    winner = resolve_knockout_match(finalists[0], finalists[1], predictor, config, rng)
    return winner
