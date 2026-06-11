# Mundial 2026 -- Simulacion Montecarlo

Simulacion estadistica del Mundial EE.UU. 2026 usando el metodo de Montecarlo con
**10 000 iteraciones**. Cada iteracion simula el torneo completo (12 grupos de 4,
32 eliminatorias) usando un modelo Poisson basado en datos historicos de
enfrentamientos internacionales (2004-2026).

## Resultados esperados

- 📈 **Grafico de convergencia** del Montecarlo (`results/convergence.png`)
- 📊 **Tabla Top 10** con probabilidad (%) de ganar la copa
- ⚽ **Predicciones de fase de grupos** — resultados mas probables por partido
- 📁 CSV exportable con resultados completos (`results/top10.csv`, `results/group_stage_predictions.csv`)

## Stack

- Python >= 3.10
- NumPy, Pandas, Matplotlib, Seaborn, SciPy, Requests, tqdm, pytest

## Setup rapido

```bash
git clone https://github.com/rodrigovzq/mundial2026-montecarlo.git
cd mundial2026-montecarlo
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar simulacion

```bash
python run.py
```

La simulacion:
1. Descarga ~44k partidos historicos de GitHub (martj42/international-football-results)
2. Filtra por ventana 2004-2026 y calcula pesos temporales + por torneo
3. Construye matriz de fuerza historica entre los 48 equipos clasificados
4. Simula 10 000 mundiales (fase de grupos + eliminatorias)
5. Genera grafico de convergencia, tabla Top 10 y predicciones de grupo

## Parametros configurables

Todos los parametros se ajustan en `config.py`:

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| ITERATIONS | 10,000 | Numero de mundiales simulados |
| SEED | 42 | Semilla para reproducibilidad |
| LAMBDA_DECAY | 0.15 | Decaimiento temporal de partidos historicos |
| PENALTY_BIAS | 0.15 | Ventaja maxima del favorito en penales |
| YEAR_MIN | 2004 | Inicio ventana historica |
| YEAR_MAX | 2026 | Fin ventana historica |

## Tests

```bash
# Activar entorno virtual primero
python -m pytest tests/ -v

# Con cobertura
python -m pytest tests/ --cov=src --cov-report=term-missing
```

## Estructura del proyecto

```
mundial2026-montecarlo/
├── config.py        ← Parametros configurables
├── run.py           ← Entry point del pipeline
├── data/
│   ├── download_data.py  ← Script de descarga de datos historicos
│   ├── matches.csv       ← Dataset historico (generado)
│   └── teams.json        ← 48 selecciones clasificadas
├── src/
│   ├── data_loader.py    ← Carga, pesos, matriz de fuerza
│   ├── model.py          ← MatchPredictor (Poisson, ET, penales)
│   ├── tournament.py     ← Grupos, bracket, eliminatorias
│   ├── simulation.py     ← Motor Montecarlo
│   └── visualize.py      ← Graficos y tablas
├── tests/            ← Tests unitarios (74+ tests)
├── results/          ← Output de simulaciones (PNG, CSV)
├── SPEC.md           ← Especificacion completa
└── requirements.txt  ← Dependencias
```

## Licencia

MIT
