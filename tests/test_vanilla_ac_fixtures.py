import configparser
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parent
VANILLA = ROOT / "fixtures" / "assetto-corsa" / "vanilla"
REFERENCE = ROOT / "fixtures" / "reference-series"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fixture:
        return json.load(fixture)


class VanillaAssettoCorsaFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.installation = load_json(VANILLA / "observed-installation.json")
        cls.launch_plan = load_json(VANILLA / "round-1-launch-plan.json")
        cls.observed_result = load_json(VANILLA / "race-out-hotlap.observed.json")
        cls.observed_smoke_result = load_json(VANILLA / "race-out-smoke.observed.json")
        cls.launch_observations = load_json(VANILLA / "launch-observations.json")
        cls.series = load_json(REFERENCE / "lights-out-mx5-sprint-cup.series.json")
        cls.race_ini = configparser.ConfigParser(interpolation=None, strict=True)
        cls.race_ini.optionxform = str
        with (VANILLA / "round-1-race.ini").open(encoding="utf-8") as fixture:
            cls.race_ini.read_file(fixture)
        cls.smoke_ini = configparser.ConfigParser(interpolation=None, strict=True)
        cls.smoke_ini.optionxform = str
        with (VANILLA / "smoke-test-race.ini").open(encoding="utf-8") as fixture:
            cls.smoke_ini.read_file(fixture)

    def test_observed_content_maps_every_reference(self) -> None:
        mappings = self.installation["contentMappings"]
        car_refs = {mapping["logicalRef"] for mapping in mappings["cars"]}
        track_refs = {
            (mapping["logicalTrackRef"], mapping["logicalLayoutRef"])
            for mapping in mappings["tracks"]
        }
        livery_refs = {mapping["logicalRef"] for mapping in mappings["liveries"]}

        self.assertEqual(
            {entrant["carRef"] for entrant in self.series["entrants"]},
            car_refs,
        )
        self.assertEqual(
            {(event["trackRef"], event["layoutRef"]) for event in self.series["calendar"]},
            track_refs,
        )
        self.assertEqual(
            {entrant["liveryRef"] for entrant in self.series["entrants"]},
            livery_refs,
        )
        self.assertTrue(all(mapping["pitboxes"] >= len(self.series["entrants"]) for mapping in mappings["tracks"]))

    def test_round_one_ini_matches_launch_plan(self) -> None:
        values = self.launch_plan["simulatorValues"]
        self.assertEqual(values["model"], self.race_ini["RACE"]["MODEL"])
        self.assertEqual(values["track"], self.race_ini["RACE"]["TRACK"])
        self.assertEqual(values["configTrack"], self.race_ini["RACE"]["CONFIG_TRACK"])
        self.assertEqual(str(values["cars"]), self.race_ini["RACE"]["CARS"])
        self.assertEqual(values["weather"], self.race_ini["WEATHER"]["NAME"])
        self.assertEqual(str(values["sunAngle"]), self.race_ini["LIGHTING"]["SUN_ANGLE"])

        for session in values["sessions"]:
            section = self.race_ini[f"SESSION_{session['index']}"]
            self.assertEqual(str(session["type"]), section["TYPE"])
            self.assertEqual(session["name"], section["NAME"])
            self.assertEqual(session["spawnSet"], section["SPAWN_SET"])
            if "durationMinutes" in session:
                self.assertEqual(str(session["durationMinutes"]), section["DURATION_MINUTES"])
            if "laps" in session:
                self.assertEqual(str(session["laps"]), section["LAPS"])

    def test_round_one_ini_maps_every_entrant_in_order(self) -> None:
        liveries = {
            mapping["logicalRef"]: mapping["skin"]
            for mapping in self.installation["contentMappings"]["liveries"]
        }
        for index, entrant in enumerate(self.series["entrants"]):
            section = self.race_ini[f"CAR_{index}"]
            self.assertEqual(entrant["displayName"], section["DRIVER_NAME"])
            self.assertEqual(liveries[entrant["liveryRef"]], section["SKIN"])
            if entrant["control"] == "player":
                self.assertEqual("-", section["MODEL"])
            else:
                self.assertEqual("ks_mazda_mx5_cup", section["MODEL"])
                self.assertEqual(str(entrant["ai"]["skill"]), section["AI_LEVEL"])
                self.assertEqual(str(entrant["ai"]["aggression"]), section["AI_AGGRESSION"])

    def test_observed_result_preserves_vanilla_top_level_shape(self) -> None:
        self.assertEqual(
            {"track", "number_of_sessions", "players", "sessions", "extras"},
            set(self.observed_result),
        )
        self.assertEqual(self.observed_result["number_of_sessions"], len(self.observed_result["sessions"]))
        self.assertGreaterEqual(len(self.observed_result["players"]), 1)

    def test_smoke_fixture_is_short_and_uses_reference_content(self) -> None:
        self.assertEqual("ks_mazda_mx5_cup", self.smoke_ini["RACE"]["MODEL"])
        self.assertEqual("magione", self.smoke_ini["RACE"]["TRACK"])
        self.assertEqual("3", self.smoke_ini["RACE"]["CARS"])
        self.assertEqual("1", self.smoke_ini["SESSION_0"]["DURATION_MINUTES"])
        self.assertEqual("1", self.smoke_ini["SESSION_1"]["LAPS"])

    def test_failed_launch_observation_proves_safe_recovery(self) -> None:
        first_attempt = self.launch_observations["attempts"][0]
        self.assertEqual("redirected-to-vanilla-launcher", first_attempt["outcome"])
        self.assertIn(
            "The exact pre-attempt race.ini bytes were restored and hash-verified.",
            first_attempt["observations"],
        )
        second_attempt = self.launch_observations["attempts"][1]
        self.assertEqual("preflight-blocked-then-verified", second_attempt["outcome"])
        self.assertIn("The preflight stopped before staging or launching.", second_attempt["observations"])
        self.assertIn(
            "The exact pre-attempt race.ini bytes were restored and hash-verified.",
            second_attempt["observations"],
        )

    def test_observed_smoke_result_is_correlated_but_incomplete(self) -> None:
        result = self.observed_smoke_result
        self.assertEqual("magione", result["track"])
        self.assertEqual(2, result["number_of_sessions"])
        self.assertEqual([2, 3], [session["type"] for session in result["sessions"]])
        self.assertEqual(
            ["ks_mazda_mx5_cup"] * 3,
            [player["car"] for player in result["players"]],
        )
        race = result["sessions"][1]
        self.assertEqual([1, 2, 0], race["raceResult"])
        self.assertEqual([0, 0, 0], race["lapstotal"])
        self.assertEqual([], race["laps"])
        self.assertFalse(any(race["lapstotal"]))


if __name__ == "__main__":
    unittest.main()
