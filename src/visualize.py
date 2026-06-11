"""Visualizaciones: grafico de convergencia y tabla Top 10 (SPEC Section 7)."""

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
    "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
]


def plot_convergence(
    snapshots: list[pd.DataFrame],
    save_path: str = "results/convergence.png",
) -> None:
    """Genera el grafico de convergencia del Montecarlo (SPEC 7.1)."""
    all_data = pd.concat(snapshots, ignore_index=True)
    final_top10 = snapshots[-1]["team"].tolist()

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(14, 8))

    for idx, team in enumerate(final_top10):
        team_data = all_data[all_data["team"] == team]
        if not team_data.empty:
            color = COLORS[idx % len(COLORS)]
            ax.plot(
                team_data["iteration"],
                team_data["probability"],
                label=team,
                color=color,
                linewidth=2,
                alpha=0.85,
            )

    ax.set_xlabel("Iteraciones", fontsize=12, color="white")
    ax.set_ylabel("Probabilidad acumulada (%)", fontsize=12, color="white")
    ax.set_title(
        "Convergencia de la Simulacion Montecarlo -- Mundial 2026",
        fontsize=14, color="white", pad=15,
    )
    ax.legend(
        bbox_to_anchor=(1.05, 1), loc="upper left",
        framealpha=0.8, fontsize=10,
    )
    ax.grid(True, alpha=0.2, color="gray")
    ax.set_facecolor("#1a1a2e")
    fig.patch.set_facecolor("#1a1a2e")
    ax.tick_params(colors="white")

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close(fig)

    log.info("Grafico de convergencia guardado en %s", save_path)


def build_top10_table(
    winner_counts: dict[str, int],
    total_iterations: int,
) -> pd.DataFrame:
    """Construye la tabla formateada del Top 10 (SPEC 7.2)."""
    sorted_teams = sorted(
        winner_counts.items(), key=lambda x: -x[1]
    )[:10]

    rows = []
    for i, (team, count) in enumerate(sorted_teams, 1):
        pct = count / total_iterations * 100
        rows.append({
            "#": i,
            "Seleccion": team,
            "Probabilidad de ganar": f"{pct:.1f}%",
        })

    df = pd.DataFrame(rows)
    log.info("\n" + df.to_string(index=False))
    return df


def export_top10(
    winner_counts: dict[str, int],
    total_iterations: int,
    output_path: str = "results/top10.csv",
) -> pd.DataFrame:
    """Exporta el Top 10 a CSV (SPEC 7.2)."""
    df = build_top10_table(winner_counts, total_iterations)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    log.info("Top 10 exportado a %s", output_path)
    return df


def build_group_stage_predictions_table(
    predictor,
    teams_df: pd.DataFrame,
    output_path: str = "results/group_stage_predictions.csv",
) -> pd.DataFrame:
    """Genera tabla de resultados mas probables de la fase de grupos.

    Para cada partido de la fase de grupos, calcula el marcador mas probable
    usando la moda de Poisson (sin aleatoriedad).
    """
    rows: list[dict] = []
    groups = teams_df.groupby("group")

    for group_name, group_teams in groups:
        team_list = group_teams["name"].tolist()
        for i in range(len(team_list)):
            for j in range(i + 1, len(team_list)):
                home, away = team_list[i], team_list[j]
                g_home, g_away = predictor.predict_most_likely(home, away)
                rows.append({
                    "Group": group_name,
                    "Home": home,
                    "Away": away,
                    "Predicted Home Goals": g_home,
                    "Predicted Away Goals": g_away,
                })

    df = pd.DataFrame(rows)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    log.info("Predicciones de fase de grupos guardadas en %s", output_path)

    print("\n" + "=" * 70)
    print("PREDICCIONES FASE DE GRUPOS - Resultados mas probables")
    print("=" * 70)
    for group_name, group_df in df.groupby("Group"):
        print(f"\nGrupo {group_name}:")
        print("-" * 40)
        for _, row in group_df.iterrows():
            print(f"  {row['Home']:<20} vs {row['Away']:<20}  ->  {int(row['Predicted Home Goals'])}-{int(row['Predicted Away Goals'])}")
    print("=" * 70)

    return df
