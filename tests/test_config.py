"""Tests para config.py."""

import pytest
from config import SimulationConfig


class TestSimulationConfig:
    """Prueba los valores por defecto y la creacion de config."""

    def test_default_values(self):
        """Verifica valores por defecto segun SPEC Section 6.1."""
        cfg = SimulationConfig()
        assert cfg.ITERATIONS == 100_000
        assert cfg.SEED == 42
        assert cfg.LAMBDA_DECAY == 0.15
        assert cfg.DECAY_WINDOW == 30

    def test_tournament_weights_contain_key_categories(self):
        """Verifica que existan pesos para las categorias principales (SPEC 4.1.2)."""
        cfg = SimulationConfig()
        required = {"FIFA World Cup", "Friendly", "FIFA World Cup qualification"}
        for key in required:
            assert key in cfg.TOURNAMENT_WEIGHTS

    def test_world_cup_weight_is_highest(self):
        """El peso del Mundial debe ser el mas alto (1.0 segun SPEC 4.1.2)."""
        cfg = SimulationConfig()
        assert cfg.TOURNAMENT_WEIGHTS["FIFA World Cup"] == 1.0
        for category, weight in cfg.TOURNAMENT_WEIGHTS.items():
            if category != "FIFA World Cup":
                assert weight <= 1.0

    def test_custom_values(self):
        """Se pueden sobreescribir parametros."""
        cfg = SimulationConfig(ITERATIONS=100, SEED=123)
        assert cfg.ITERATIONS == 100
        assert cfg.SEED == 123

    def test_config_is_frozen(self):
        """SimulationConfig debe ser inmutable (frozen dataclass)."""
        cfg = SimulationConfig()
        with pytest.raises(AttributeError):
            cfg.ITERATIONS = 5
