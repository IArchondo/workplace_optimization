import typing as T

import pandas as pd
from scipy.spatial import distance


class ModelInput:
    def __init__(self, persons: pd.DataFrame, seats: pd.DataFrame):
        self.persons = persons
        self.seats = seats

    def __calculate_euclidian_distances(self, input_seat, seat_df):
        """Calculate distance from one seat to the rest."""
        seat_info = seat_df[seat_df["Seat"] == input_seat]
        rest_df = seat_df[seat_df["Seat"] != input_seat]

        seat_coor = (seat_info["x_coor"].iloc[0], seat_info["y_coor"].iloc[0])
        return {
            row["Seat"]: distance.euclidean(seat_coor, (row["x_coor"], row["y_coor"]))
            for i, row in rest_df.iterrows()
        }

    def teams_dicts(self, persons: pd.DataFrame) -> T.Dict[int, T.List[str]]:
        """Generate dictionary linking team to team members."""
        return persons.groupby(["Team"])["Name"].unique().to_dict()

    def seat_distance_dict(
        self, seats: pd.DataFrame
    ) -> T.Dict[str, T.Dict[str, float]]:
        return {
            seat: self.__calculate_euclidian_distances(seat, seats)
            for seat in self.seats["Seat"]
        }
