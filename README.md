# Mundial 2026 — Simulación Montecarlo

Simulación estadística del Mundial EE.UU. 2026 usando el método de Montecarlo.

El modelo analiza **~50,000 partidos históricos** (1872–2026) y ejecuta **100,000
mundiales simulados** para calcular la probabilidad de cada selección.

## Resultados

### 🏆 Top 10 — Probabilidad de ganar la copa

| # | Selección | Probabilidad |
|---|-----------|:-----------:|
| 1 | Brazil | 16.8% |
| 2 | Spain | 14.8% |
| 3 | Argentina | 10.4% |
| 4 | England | 10.3% |
| 5 | Netherlands | 8.2% |
| 6 | France | 6.9% |
| 7 | Germany | 6.5% |
| 8 | Portugal | 3.5% |
| 9 | Uruguay | 2.2% |
| 10 | Croatia | 2.2% |

### ⚽ Predicciones de fase de grupos

Cada partido de la fase de grupos se simula 100,000 veces dentro del Monte Carlo.
El resultado reportado es el marcador más frecuente. Ver `results/group_stage_predictions.csv`.

### 📈 Gráfico de convergencia

`results/convergence.png` muestra cómo se estabilizan las probabilidades
del Top 10 a medida que aumentan las iteraciones.

## Stack

- Python ≥ 3.10
- NumPy, Pandas, Matplotlib, Requests, tqdm, SciPy
- pytest (79+ tests)

## Quick start

```bash
git clone https://github.com/rodrigovzq/mundial2026-montecarlo.git
cd mundial2026-montecarlo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Ver `BUILD.md` para documentación completa.

## Estructura

```
mundial2026-montecarlo/
├── config.py         ← Parámetros
├── run.py            ← Entry point
├── BUILD.md          ← Documentación
├── data/
│   ├── teams.json    ← 48 selecciones
│   └── matches.csv   ← ~50k partidos históricos
├── src/              ← 6 módulos del modelo
├── tests/            ← 79+ tests
├── results/          ← Outputs generados
└── requirements.txt  ← Dependencias
```

## Tests

```bash
python -m pytest tests/ -v
```

## Licencia

MIT
