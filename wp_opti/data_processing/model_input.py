import typing as T

import pandas as pd
from scipy.spatial import distance


class ModelInput:
    def __init__(self, persons: pd.DataFrame, seats: pd.DataFrame):
        self.persons_input = persons
        self.seats_input = seats

    def __calculate_euclidian_distances(self, input_seat, seat_df):
        """Calculate distance from one seat to the rest."""
        seat_info = seat_df[seat_df["Seat"] == input_seat]
        rest_df = seat_df[seat_df["Seat"] != input_seat]

        seat_coor = (seat_info["x_coor"].iloc[0], seat_info["y_coor"].iloc[0])
        return {
            row["Seat"]: distance.euclidean(seat_coor, (row["x_coor"], row["y_coor"]))
            for i, row in rest_df.iterrows()
        }

    def build_persons(self, persons):
        """Create list of person ids."""
        return list(persons["Name"])

    def build_seats(self, seats):
        """Create list of seat ids."""
        return list(seats["Seat"])

    def build_person_team_dict(self, persons: pd.DataFrame) -> T.Dict[str, int]:
        """Generate dictionary linking person to his team."""
        return dict(zip(persons["Name"], persons["Team"]))

    def build_teams_dicts(self, persons: pd.DataFrame) -> T.Dict[int, T.List[str]]:
        """Generate dictionary linking team to team members."""
        return persons.groupby(["Team"])["Name"].unique().to_dict()

    def build_seat_distance_dict(
        self, seats: pd.DataFrame
    ) -> T.Dict[str, T.Dict[str, float]]:
        """Generate dictionary with seat distances."""
        return {
            seat: self.__calculate_euclidian_distances(seat, seats)
            for seat in seats["Seat"]
        }

    def build_seat_utility_dict(self, seats: pd.DataFrame) -> T.Dict[str, float]:
        """Generate dictionary with seat utilities."""
        return dict(zip(seats["Seat"], seats["utility"]))

    def build_complete_input(self):
        """Build complete input for model."""
        self.persons = self.build_persons(self.persons_input)
        self.seats = self.build_seats(self.seats_input)
        self.team_dict = self.build_teams_dicts(self.persons_input)
        self.person_team_dict = self.build_person_team_dict(self.persons_input)
        self.seat_distance_dict = self.build_seat_distance_dict(self.seats_input)
        self.seat_utility_dict = self.build_seat_utility_dict(self.seats_input)
