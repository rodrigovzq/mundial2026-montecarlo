"""Pipeline principal de la simulacion Montecarlo.

Usage:
    python run.py

Orquestacion completa:
    1. Descargar datos historicos (si no existen)
    2. Cargar y procesar datos
    3. Construir modelo estadistico
    4. Ejecutar simulacion Montecarlo (10k iteraciones)
    5. Generar visualizaciones y tabla Top 10
"""

import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from config import SimulationConfig
from src.data_loader import load_matches
from src.model import MatchPredictor
from src.simulation import run_simulation
from src.visualize import plot_convergence, build_top10_table, export_top10, export_group_stage_predictions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def ensure_data() -> str:
    """Verifica que los datos historicos existan, si no los descarga."""
    csv_path = Path("data/matches.csv")
    if csv_path.exists():
        log.info("Dataset encontrado en %s", csv_path)
        return str(csv_path)

    log.info("Dataset no encontrado. Intentando descarga...")
    from data.download_data import download_matches
    if download_matches():
        return str(csv_path)

    log.warning("No se pudo descargar el dataset. Verifica conexion a internet.")
    log.warning("La simulacion usara solo proxy por ranking FIFA (resultados limitados).")
    return ""


def load_teams_data() -> pd.DataFrame:
    """Carga el archivo de selecciones como DataFrame."""
    with open("data/teams.json", "r") as f:
        data = json.load(f)
    return pd.DataFrame(data["teams"])


def main() -> int:
    """Ejecuta el pipeline completo de la simulacion."""

    log.info("=" * 60)
    log.info("MUNDIAL 2026 -- SIMULACION MONTECARLO")
    log.info("=" * 60)

    # 0. Configuracion
    config = SimulationConfig()
    log.info("Configuracion: %d iteraciones, seed=%d, decay_window=%d años",
             config.ITERATIONS, config.SEED, config.DECAY_WINDOW)

    # 1. Datos
    data_path = ensure_data()
    teams_df = load_teams_data()
    log.info("Selecciones cargadas: %d equipos en %d grupos",
             len(teams_df), teams_df["group"].nunique())

    # 2. Cargar y procesar datos
    t0 = time.time()
    if data_path:
        matches = load_matches(data_path, config)
        log.info("Partidos historicos cargados: %d (ventana %d-%d)",
                 len(matches), config.YEAR_MIN, config.YEAR_MAX)
    else:
        log.warning("Usando datos minimos (solo ranking FIFA)")
        matches = pd.DataFrame(columns=[
            "date", "home_team", "away_team", "home_score",
            "away_score", "tournament", "neutral", "country",
        ])

    # 3. Modelo estadistico
    predictor = MatchPredictor(matches, config, teams_df)
    log.info("Matriz de fuerza construida con %d pares de equipos",
             len(predictor.strength_matrix))
    log.info("Tiempo de preparacion: %.2f seg", time.time() - t0)

    # 4. Simulacion Montecarlo
    log.info("Iniciando simulacion de %d mundiales...", config.ITERATIONS)
    t1 = time.time()
    rng = np.random.default_rng(config.SEED)
    winner_counts, snapshots, match_score_counts = run_simulation(predictor, config, rng)
    elapsed = time.time() - t1
    log.info("Simulacion completada en %.2f seg (%.2f iter/seg)",
             elapsed, config.ITERATIONS / elapsed)

    # 4b. Predicciones de fase de grupos (desde Monte Carlo)
    log.info("Procesando predicciones de fase de grupos desde Monte Carlo...")
    group_rows = []
    for (group, home, away), scores in match_score_counts.items():
        most_frequent = max(scores, key=scores.get)
        g_home, g_away = most_frequent.split("-")
        row = {
            "group": group,
            "home": home,
            "away": away,
            "predicted_home_goals": int(g_home),
            "predicted_away_goals": int(g_away),
            "samples": sum(scores.values()),
        }
        group_rows.append(row)

    group_preds_df = pd.DataFrame(group_rows)
    export_group_stage_predictions(group_preds_df, "results/group_stage_predictions.csv")
    log.info("Predicciones generadas para %d partidos de grupo desde Monte Carlo", len(group_preds_df))

    # 5. Resultados
    champion = max(winner_counts, key=winner_counts.get)
    champion_pct = winner_counts[champion] / config.ITERATIONS * 100
    log.info("Campeon mas frecuente: %s (%.1f%% de las simulaciones)",
             champion, champion_pct)

    top10 = build_top10_table(winner_counts, config.ITERATIONS)
    log.info("\n" + top10.to_string(index=False))

    # 6. Visualizaciones
    plot_convergence(snapshots, "results/convergence.png")
    export_top10(winner_counts, config.ITERATIONS, "results/top10.csv")

    log.info("=" * 60)
    log.info("SIMULACION COMPLETADA EXITOSAMENTE")
    log.info("Resultados en: results/convergence.png, results/top10.csv, results/group_stage_predictions.csv (Monte Carlo)")
    log.info("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
