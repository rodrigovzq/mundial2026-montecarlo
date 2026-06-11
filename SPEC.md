# SPEC — Simulación Montecarlo Mundial EE.UU. 2026

## 1. Objetivo del Proyecto

Desarrollar un modelo estadístico que simule el Mundial de Fútbol EE.UU. 2026 mediante el método de Montecarlo con **10 000 iteraciones**, donde cada iteración representa una instancia completa del torneo (fase de grupos → eliminatorias → campeón). El entregable final es:

- Una **visualización de la evolución/convergencia** del Montecarlo.
- Una **tabla con el Top 10 de selecciones** y su **probabilidad (%) de ganar la copa**.

---

## 2. Lenguaje de Programación y Entorno

| Requisito | Detalle |
|-----------|---------|
| **Lenguaje** | Python ≥ 3.10 |
| **Entorno** | `venv` con `requirements.txt` |
| **Control de versiones** | Git + GitHub (`rodrigovzq/mundial2026-montecarlo`) |
| **Estructura recomendada** | Modular: separar datos, modelo, simulación, visualización |

### `requirements.txt` propuesto

```
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.10.0
requests>=2.31.0
tqdm>=4.65.0
```

---

## 3. Fuentes de Datos

### 3.1 Datos de partidos internacionales históricos

**Fuente primaria recomendada:** [martj42/international-football-results](https://github.com/martj42/international-football-results) (dataset en GitHub, ∼44 000 partidos internacionales desde 1872, actualizado periódicamente).

Alternativas:
- [openfootball/world-cup](https://github.com/openfootball/world-cup) — datos específicos de mundiales.
- [jfjelstul/worldcup](https://github.com/jfjelstul/worldcup) — base de datos SQLite detallada de todos los mundiales.
- API de [Football-Data.org](https://www.football-data.org/) (requiere API key gratuita).
- Rankings FIFA oficiales (CSV scrapeable desde Wikipedia o RSSSF).

### 3.2 Ventana temporal

- **Primera opción:** últimos **20 años** (2004–2024).
- **Fallback:** si alguna selección no tiene suficientes datos en esa ventana, extender hasta donde haya registros.

### 3.3 Datos requeridos por partido

| Campo | Descripción |
|-------|-------------|
| `date` | Fecha del partido |
| `home_team` | Selección local |
| `away_team` | Selección visitante |
| `home_score` | Goles del local |
| `away_score` | Goles del visitante |
| `tournament` | Torneo (amistoso, eliminatoria, mundial, copa continental, etc.) |
| `neutral` | Si fue en cancha neutral (bool) |

---

## 4. Modelo Estadístico

### 4.1 Variable aleatoria por selección

Para cada selección participante se construye una **variable aleatoria de "fuerza"** (`strength`) basada en su historial contra los rivales que enfrenta, con las siguientes características:

1. **Ponderación temporal:** los partidos más recientes pesan más.
   - Fórmula sugerida: peso exponencial `w = exp(-λ × años_desde_partido)` con `λ` configurable (default: `λ = 0.15` → un partido de hace 10 años pesa ~22% de uno actual).
   - Alternativa: decaimiento lineal con cutoff.

2. **Ponderación por tipo de torneo:**
   | Tipo de partido | Peso |
   |-----------------|------|
   | Mundial | 1.0 |
   | Eliminatoria mundialista / Copa continental | 0.8 |
   | Amistoso | 0.4 |

3. **Métrica de rendimiento:** para cada partido histórico se calcula un "rating de desempeño" considerando:
   - Diferencia de goles (con diminishing returns).
   - Resultado (W/L/D).
   - ¿Local/visitante/neutral?

4. **Agregación:** el `strength` de un equipo `A` contra un equipo `B` es la media ponderada de sus ratings históricos en enfrentamientos directos `A vs B`.

### 4.2 Simulación de un partido

Para simular un partido entre `A` y `B`:

1. Se calcula `strength_A` (fuerza de A contra B) y `strength_B` (fuerza de B contra A).
2. Se estima la probabilidad de gol de cada equipo con una distribución de Poisson donde `λ_A = f(strength_A, strength_B)` y `λ_B = f(strength_B, strength_A)`.
3. Se muestrean goles: `goles_A ~ Poisson(λ_A)`, `goles_B ~ Poisson(λ_B)`.
4. Si hay empate en fase eliminatoria: se simula alargue y/o penales con un modelo simplificado (binomial o 50/50 ajustado por ranking).

### 4.3 Datos sintéticos de respaldo

Si para un enfrentamiento **no hay datos históricos suficientes** (menos de 3 partidos), se debe usar un **proxy** basado en:
- Ranking FIFA / Elo rating relativo entre ambos equipos.
- Desempeño contra rivales de nivel similar (equipos con rating cercano).

---

## 5. Estructura del Torneo

El Mundial 2026 tiene **48 equipos** en **12 grupos de 4**. El formato oficial es:

1. **Fase de grupos:** 12 grupos × 4 equipos. Clasifican los 2 primeros de cada grupo (24 equipos) + los 8 mejores terceros (8 equipos) → **32 equipos a dieciseisavos**.
2. **Dieciseisavos de final** → **Octavos** → **Cuartos** → **Semifinal** → **Tercer puesto** → **Final**.

> **Nota importante:** si al momento del desarrollo la FIFA modifica el formato, usar el formato oficial vigente.

### Equipos participantes (48)

Los 48 equipos se deben obtener de la lista oficial de clasificados al momento de ejecutar la simulación. Si no están todos definidos, se puede usar una lista proyectada o permitir configuración vía archivo `teams.json`.

---

## 6. Simulación Montecarlo

### 6.1 Parámetros

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `ITERATIONS` | **10 000** | Cantidad de mundiales simulados |
| `SEED` | Configurable | Semilla para reproducibilidad |

### 6.2 Algoritmo de cada iteración

```
Para i en 1..10000:
    1. Cargar/actualizar ratings de los 48 equipos
    2. Simular fase de grupos (todos contra todos en cada grupo)
       - Calcular puntos (victoria=3, empate=1, derrota=0)
       - Desempate: diferencia de goles → goles a favor → resultado directo → sorteo
    3. Armar bracket de 32 equipos según reglas FIFA
    4. Simular eliminatorias (dieciseisavos → final)
    5. Registrar campeón
```

### 6.3 Seguimiento de convergencia

Cada 100 iteraciones, guardar un snapshot de las probabilidades acumuladas del Top 10 para graficar la evolución.

---

## 7. Visualizaciones Requeridas

### 7.1 Gráfico de convergencia del Montecarlo

- **Eje X:** número de iteraciones (0 a 10 000).
- **Eje Y:** probabilidad acumulada (%) de ganar.
- **Contenido:** una línea por cada equipo del Top 10 final, mostrando cómo se estabiliza su probabilidad a medida que avanzan las iteraciones.
- **Estilo:** fondo oscuro (dark theme), leyenda clara, líneas diferenciadas por color.

### 7.2 Tabla Top 10

Al final de la simulación, generar una tabla ordenada por probabilidad descendente:

| # | Selección | Probabilidad de ganar |
|---|-----------|----------------------|
| 1 | ... | XX.X% |
| 2 | ... | XX.X% |
| ... | ... | ... |
| 10 | ... | XX.X% |

Exportar también como CSV (`results/top10.csv`).

---

## 8. Entregables del Repositorio

```
mundial2026-montecarlo/
├── SPEC.md                 ← Este archivo
├── README.md               ← Setup, uso, resultados de ejemplo
├── requirements.txt        ← Dependencias Python
├── .gitignore              ← Ignorar __pycache__, .venv, resultados grandes
├── data/
│   ├── README.md           ← Cómo obtener/datos de partidos
│   └── matches.csv         ← Dataset histórico (o script para descargarlo)
├── src/
│   ├── __init__.py
│   ├── data_loader.py      ← Carga y preprocesamiento de datos
│   ├── model.py            ← Modelo estadístico (strength, ratings, Poisson)
│   ├── tournament.py       ← Lógica del torneo (grupos, bracket, reglas FIFA)
│   ├── simulation.py       ← Motor Montecarlo (loop de 10k iteraciones)
│   └── visualize.py        ← Gráficos de convergencia + tabla Top 10
├── results/                ← Output de simulaciones (gitignored excepto .gitkeep)
│   └── .gitkeep
├── run.py                  ← Script principal (ejecuta todo el pipeline)
└── config.py               ← Parámetros configurables (ITERATIONS, SEED, λ, etc.)
```

---

## 9. Constraints y Consideraciones

1. **Reproducibilidad:** fijar `SEED` por defecto para que dos ejecuciones idénticas den el mismo resultado.
2. **Performance:** 10 000 iteraciones × 48 equipos debe correr en < 5 minutos en hardware estándar. Usar vectorización con NumPy donde sea posible.
3. **Manejo de datos faltantes:** si una selección clasificada no tiene datos históricos suficientes, usar el sistema de proxy (Sección 4.3) sin crashear.
4. **Formato del torneo:** verificar el formato oficial al momento de desarrollar (la FIFA confirmó 12 grupos de 4 en marzo 2023, pero verificar si hay cambios).
5. **Idioma:** código y comentarios en español. Nombres de variables y funciones en inglés (convención estándar de programación).
6. **Tipado:** usar type hints de Python donde sea práctico.

---

## 10. Posibles Extensiones Futuras (fuera del MVP)

- Agregar lesiones/bajas de jugadores clave como factor.
- Modelar ventaja de localía para EE.UU., México y Canadá (co-anfitriones).
- Interfaz web simple con Streamlit para explorar resultados.
- Simulación de goleadores y tabla de posiciones completa.
- Exportación de brackets en formato visual.

---

> **Autor:** Rodrigo Vázquez (`rodrigovzq`)  
> **Repositorio:** https://github.com/rodrigovzq/mundial2026-montecarlo  
> **Fecha:** Junio 2026
