from datetime import datetime
import logging

import gurobipy as grb

from wp_opti.optimization.containers import (
    VariableContainer,
    ConstraintContainer,
    OutputContainer,
)

LOGGER = logging.getLogger(__name__)

TEAMMATE_PLUS = 50


class WorkplaceModel:
    def __init__(self, model_input):
        self.input = model_input

        self.model = grb.Model(
            name="subtype_model" + datetime.now().strftime("%d-%b-%Y_%H:%M:%S")
        )

    def build_model(self):
        """Build model's variables, constraints and objective function."""
        self.variables = self.create_variables()
        self.constraints = self.create_constraints()
        self.set_objective()

    def create_variables(self):
        """Build variables for the model."""
        return VariableContainer(
            seat_to_person_assignments=self.build_seat_to_person_assignments(),
            seat_to_person_utility=self.build_seat_to_person_utility(),
        )

    def build_seat_to_person_assignments(self):
        """Build variables mapping seats to persons."""
        indexes = [
            (seat, person) for seat in self.input.seats for person in self.input.persons
        ]
        return self.model.addVars(
            indexes, vtype=grb.GRB.BINARY, name="seat_to_person_assignment"
        )

    def build_seat_to_person_utility(self):
        """Build variables mapping an utility to a seat-person combination."""
        indexes = [
            (seat, person) for seat in self.input.seats for person in self.input.persons
        ]
        return self.model.addVars(
            indexes, vtype=grb.GRB.CONTINUOUS, name="seat_to_person_utility"
        )

    def create_constraints(self):
        """Build constraints for the model."""
        seat_to_person_assignments = self.variables.seat_to_person_assignments
        return ConstraintContainer(
            one_person_per_seat=self.build_one_person_per_seat(
                seat_to_person_assignments
            ),
            one_seat_per_person=self.build_one_seat_per_person(
                seat_to_person_assignments
            ),
            utility_definition=self.build_utility_definition(
                seat_to_person_assignments, self.variables.seat_to_person_utility
            ),
        )

    def build_one_person_per_seat(self, seat_to_person_assignments):
        """Build constraint making sure that a person only seats in one seat."""
        return self.model.addConstrs(
            (
                (
                    grb.quicksum(
                        seat_to_person_assignments[(seat, person)]
                        for seat in self.input.seats
                    )
                    == 1
                )
                for person in self.input.persons
            ),
            name="one_person_per_seat",
        )

    def build_one_seat_per_person(self, seat_to_person_assignments):
        """Build constraint making sure that only one person seats in each seat."""
        return self.model.addConstrs(
            (
                (
                    grb.quicksum(
                        seat_to_person_assignments[(seat, person)]
                        for person in self.input.persons
                    )
                    == 1
                )
                for seat in self.input.seats
            ),
            name="one_seat_per_person",
        )

    def build_utility_definition(
        self, seat_to_person_assignments, seat_to_person_utility
    ):
        """Build constraint linking a utility to a person-seat combination."""
        return self.model.addConstrs(
            (
                (
                    seat_to_person_utility[(seat, person)]
                    == self.input.seat_utility_dict[seat]
                    + grb.quicksum(
                        seat_to_person_assignments[(teammate_seat, teammate)]
                        * (1 / self.input.seat_distance_dict[seat][teammate_seat])
                        * TEAMMATE_PLUS
                        for teammate_seat in self.input.seats
                        if teammate_seat != seat
                        for teammate in self.input.team_dict[
                            self.input.person_team_dict[person]
                        ]
                        if teammate != person
                    )
                )
                for seat in self.input.seats
                for person in self.input.persons
            ),
            name="utility_definition",
        )

    def set_objective(self):
        """Set the model's objective function."""
        self.model.setObjective(
            grb.quicksum(
                self.variables.seat_to_person_assignments[key]
                * self.variables.seat_to_person_utility[key]
                for key in self.variables.seat_to_person_assignments
            ),
            grb.GRB.MAXIMIZE,
        )

    def solve_model(self):
        """Solve a Gurobi model, specifying the stopping criteria."""
        LOGGER.info("Start solving model")
        self.model.optimize()

        if self.model.status == grb.GRB.LOADED:
            raise ValueError(
                "No solution exists. Increase time limit and consider changing MIP focus"
            )
        if self.model.status in [
            grb.GRB.INFEASIBLE,
            grb.GRB.INF_OR_UNBD,
            grb.GRB.UNBOUNDED,
        ]:
            self.model.computeIIS()
            self.model.write("model_iis.ilp")
            raise ValueError(
                "WARNING! The model is infeasible - see model_iis.ilp for infeasibility set"
            )

        self.model.printQuality()
        return self.get_output()

    def get_output(self):
        return OutputContainer(
            assignments=[
                key
                for key, value in self.variables.seat_to_person_assignments.items()
                if value.x > 0.8
            ]
        )
