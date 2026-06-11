"""Tests para data/teams.json."""

import json
import pytest


def load_teams():
    with open("data/teams.json", "r") as f:
        return json.load(f)


class TestTeamsData:
    """Valida la estructura del archivo de selecciones (SPEC Section 5)."""

    def test_file_loads(self):
        """El archivo JSON debe cargarse sin errores."""
        data = load_teams()
        assert "teams" in data

    def test_exactly_48_teams(self):
        """Deben haber exactamente 48 selecciones (SPEC 5)."""
        data = load_teams()
        assert len(data["teams"]) == 48

    def test_all_teams_have_required_fields(self):
        """Cada seleccion debe tener name, group, fifa_rank."""
        data = load_teams()
        for team in data["teams"]:
            assert "name" in team
            assert "group" in team
            assert "fifa_rank" in team
            assert isinstance(team["fifa_rank"], int)
            assert 1 <= team["fifa_rank"] <= 48

    def test_twelve_groups_four_teams_each(self):
        """12 grupos de 4 equipos (SPEC 5.1)."""
        data = load_teams()
        groups: dict[str, list[str]] = {}
        for team in data["teams"]:
            g = team["group"]
            groups.setdefault(g, []).append(team["name"])

        assert len(groups) == 12
        for group_name, teams_in_group in groups.items():
            assert len(teams_in_group) == 4, \
                f"Group {group_name} has {len(teams_in_group)} teams"

    def test_no_duplicate_team_names(self):
        """No debe haber nombres duplicados."""
        data = load_teams()
        names = [t["name"] for t in data["teams"]]
        assert len(names) == len(set(names))

    def test_groups_are_A_to_L(self):
        """Los grupos deben ser A, B, C, ..., L."""
        data = load_teams()
        groups = {t["group"] for t in data["teams"]}
        expected = {chr(ord("A") + i) for i in range(12)}
        assert groups == expected

    def test_unique_fifa_ranks(self):
        """Los rankings FIFA deben ser unicos del 1 al 48."""
        data = load_teams()
        ranks = [t["fifa_rank"] for t in data["teams"]]
        assert sorted(ranks) == list(range(1, 49))
