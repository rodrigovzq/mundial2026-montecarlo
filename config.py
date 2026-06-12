"""Parametros configurables de la simulacion (SPEC Section 6.1)."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SimulationConfig:
    """Configuracion centralizada de la simulacion Montecarlo.

    Attributes:
        ITERATIONS: Numero de mundiales a simular (SPEC 6.1).
        SEED: Semilla para reproducibilidad (SPEC 9.1).
        LAMBDA_DECAY: Factor de decaimiento temporal (SPEC 4.1.1).
        MIN_MATCHES: Minimo de partidos historicos para usar datos directos (SPEC 4.3).
        YEAR_MIN: Inicio ventana temporal (SPEC 3.2).
        YEAR_MAX: Fin ventana temporal.
        DECAY_WINDOW: Ventana fija en anos para decaimiento lineal (SPEC 4.1.1).
        EXTRA_TIME_GOAL_FACTOR: Factor de reduccion de goles en alargue.
        PENALTY_BIAS: Sesgo maximo por diferencia de fuerza en penales (SPEC 4.2.4).
        TOURNAMENT_WEIGHTS: Pesos por tipo de torneo (SPEC 4.1.2).
        BASE_GOALS_PER_MATCH: Goles totales base por partido.
    """
    ITERATIONS: int = 100_000
    SEED: int = 42
    LAMBDA_DECAY: float = 0.15
    MIN_MATCHES: int = 3
    YEAR_MIN: int = 1872
    YEAR_MAX: int = 2026
    DECAY_WINDOW: int = 30
    EXTRA_TIME_GOAL_FACTOR: float = 0.3
    PENALTY_BIAS: float = 0.15
    BASE_GOALS_PER_MATCH: float = 2.5

    TOURNAMENT_WEIGHTS: dict[str, float] = field(default_factory=lambda: {
        "FIFA World Cup": 1.0,
        "FIFA World Cup qualification": 0.8,
        "Confederation Cup": 0.8,
        "African Cup of Nations": 0.8,
        "AFC Asian Cup": 0.8,
        "Copa America": 0.8,
        "CONCACAF Gold Cup": 0.8,
        "OFC Nations Cup": 0.8,
        "UEFA Euro": 0.8,
        "UEFA Euro qualification": 0.8,
        "Friendly": 0.4,
        "default": 0.5,
    })
