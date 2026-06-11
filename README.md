# Mundial 2026 — Simulación Montecarlo

Simulación estadística del Mundial EE.UU. 2026 usando el método de Montecarlo con **10 000 iteraciones**.

Cada iteración simula el torneo completo — fase de grupos y eliminatorias — usando un modelo basado en datos históricos de enfrentamientos internacionales ponderados por antigüedad y tipo de torneo.

## Resultado esperado

- 📈 **Gráfico de convergencia** del Montecarlo (evolución por cada 100 iteraciones)
- 📊 **Tabla Top 10** de selecciones con su probabilidad (%) de ganar la copa
- 📁 CSV exportable con resultados completos

## Stack

- Python ≥ 3.10
- NumPy, Pandas, Matplotlib, Seaborn, SciPy

## Setup rápido

```bash
git clone https://github.com/rodrigovzq/mundial2026-montecarlo.git
cd mundial2026-montecarlo
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar simulación

```bash
python run.py
```

Los parámetros (ITERATIONS, SEED, λ, etc.) se configuran en `config.py`.

## Estructura del proyecto

```
├── SPEC.md              ← Especificación completa del proyecto
├── data/                ← Datos históricos de partidos
├── src/                 ← Código fuente (modelo, simulación, visualización)
├── results/             ← Output de simulaciones
├── run.py               ← Entry point
└── config.py            ← Parámetros configurables
```

## Licencia

MIT
