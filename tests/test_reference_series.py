import json
import unittest
from collections import Counter
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures" / "reference-series"


def load_fixture(name: str) -> dict:
    with (FIXTURES / name).open(encoding="utf-8") as fixture:
        return json.load(fixture)


class ReferenceSeriesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.series = load_fixture("lights-out-mx5-sprint-cup.series.json")
        cls.results = load_fixture("lights-out-mx5-sprint-cup.results.json")
        cls.expected = load_fixture("lights-out-mx5-sprint-cup.expected-standings.json")

    def test_definition_references_are_complete_and_unique(self) -> None:
        self.assertEqual("lights-out-series", self.series["format"])
        self.assertEqual(1, self.series["schemaVersion"])

        entrants = self.series["entrants"]
        entrant_ids = [entrant["id"] for entrant in entrants]
        self.assertEqual(12, len(entrant_ids))
        self.assertEqual(len(entrant_ids), len(set(entrant_ids)))
        self.assertEqual(1, sum(entrant["control"] == "player" for entrant in entrants))

        car_ids = {car["id"] for car in self.series["content"]["cars"]}
        self.assertTrue(all(entrant["carRef"] in car_ids for entrant in entrants))

        tracks = {track["id"]: track for track in self.series["content"]["tracks"]}
        events = self.series["calendar"]
        self.assertEqual([1, 2, 3, 4], [event["sequence"] for event in events])
        for event in events:
            self.assertIn(event["trackRef"], tracks)
            layouts = {layout["id"] for layout in tracks[event["trackRef"]]["layouts"]}
            self.assertIn(event["layoutRef"], layouts)
            self.assertEqual(["qualifying", "race"], [session["id"] for session in event["sessions"]])

    def test_results_cover_every_entrant_once_per_round(self) -> None:
        entrant_ids = {entrant["id"] for entrant in self.series["entrants"]}
        event_ids = {event["id"] for event in self.series["calendar"]}
        results = self.results["raceResults"]

        self.assertEqual(event_ids, {result["eventId"] for result in results})
        for result in results:
            classified_ids = [entry["entrantId"] for entry in result["classification"]]
            self.assertEqual(entrant_ids, set(classified_ids))
            self.assertEqual(len(classified_ids), len(set(classified_ids)))
            self.assertEqual(list(range(1, 13)), [entry["position"] for entry in result["classification"]])

    def test_expected_standings_follow_scoring_and_tie_breakers(self) -> None:
        entrant_ids = [entrant["id"] for entrant in self.series["entrants"]]
        points_table = self.series["championship"]["scoring"]["pointsByPosition"]
        totals = Counter({entrant_id: 0 for entrant_id in entrant_ids})
        finishes = {entrant_id: [] for entrant_id in entrant_ids}

        for result in self.results["raceResults"]:
            for entry in result["classification"]:
                entrant_id = entry["entrantId"]
                finishes[entrant_id].append(entry["position"] if entry["status"] == "classified" else 999)
                if entry["status"] == "classified" and entry["position"] <= len(points_table):
                    totals[entrant_id] += points_table[entry["position"] - 1]

        def standing_key(entrant_id: str) -> tuple:
            finish_counts = Counter(finishes[entrant_id])
            countback = tuple(-finish_counts[position] for position in range(1, len(entrant_ids) + 1))
            most_recent_results = tuple(reversed(finishes[entrant_id]))
            return (-totals[entrant_id], *countback, *most_recent_results)

        actual_order = sorted(entrant_ids, key=standing_key)
        expected_order = [entry["entrantId"] for entry in self.expected["standings"]]
        self.assertEqual(expected_order, actual_order)
        self.assertEqual(
            [entry["points"] for entry in self.expected["standings"]],
            [totals[entrant_id] for entrant_id in actual_order],
        )
        expected_wins = [entry["wins"] for entry in self.expected["standings"]]
        actual_wins = [Counter(finishes[entrant_id])[1] for entrant_id in actual_order]
        self.assertEqual(expected_wins, actual_wins)
        self.assertEqual(totals["maya-patel"], totals["theo-martin"])
        self.assertEqual(
            Counter(finishes["maya-patel"]),
            Counter(finishes["theo-martin"]),
        )
        self.assertLess(finishes["maya-patel"][-1], finishes["theo-martin"][-1])


if __name__ == "__main__":
    unittest.main()
