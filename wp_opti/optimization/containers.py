from dataclasses import dataclass
import typing as T

import gurobipy as grb


@dataclass
class VariableContainer:
    seat_to_person_assignments: T.Dict[T.Tuple[str, str], grb.Var]
    seat_to_person_utility: T.Dict[T.Tuple[str, str], grb.Var]


@dataclass
class ConstraintContainer:
    one_person_per_seat: T.List[grb.LinExpr]
    one_seat_per_person: T.List[grb.LinExpr]
    utility_definition: T.List[grb.LinExpr]


@dataclass
class OutputContainer:
    assignments: T.List[T.Tuple[str, str]]
