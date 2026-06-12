# BUILD — Mundial 2026 Montecarlo

## Requisitos

- Python >= 3.10
- pip y venv

## Setup

```bash
git clone https://github.com/rodrigovzq/mundial2026-montecarlo.git
cd mundial2026-montecarlo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar simulación

```bash
python run.py
```

La simulación:
1. Descarga automáticamente ~50k partidos históricos (si no existen)
2. Construye la matriz de fuerza histórica entre los 48 equipos
3. Ejecuta N iteraciones del torneo completo (fase de grupos → eliminatorias)
4. Exporta resultados a results/

## Tests

```bash
python -m pytest tests/ -v

# Con cobertura:
python -m pytest tests/ --cov=src --cov-report=term-missing
```

## Parámetros configurables (config.py)

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| ITERATIONS | 100,000 | Número de mundiales simulados |
| SEED | 42 | Semilla para reproducibilidad |
| DECAY_WINDOW | 30 | Ventana de decaimiento temporal (años) |
| YEAR_MIN | 1872 | Inicio ventana histórica |
| YEAR_MAX | 2026 | Fin ventana histórica |
| BASE_GOALS_PER_MATCH | 2.5 | Goles base por partido |
| PENALTY_BIAS | 0.15 | Ventaja del favorito en penales |
| EXTRA_TIME_GOAL_FACTOR | 0.3 | Factor de reducción de goles en alargue |

## Outputs

| Archivo | Contenido |
|---------|-----------|
| `results/top10.csv` | Top 10 selecciones con probabilidad de ganar |
| `results/group_stage_predictions.csv` | Resultados más probables de fase de grupos (desde Monte Carlo) |
| `results/convergence.png` | Gráfico de convergencia de la simulación |

## Modelo

- **Distribución**: Poisson para goles de cada equipo por partido
- **Fuerza**: Media ponderada de goles históricos contra cada rival
- **Pesos temporales**: Decaimiento lineal con 4 años de gracia y mínimo 0.2
- **Pesos por torneo**: Mundial ×1.0, Eliminatorias/Copas ×0.8, Amistosos ×0.4
- **Empates en KO**: Alargue con factor 0.3 + penales con sesgo por ranking
- **Proxy**: Ranking FIFA para enfrentamientos sin datos históricos
