"""Level 2 domain errors."""

from __future__ import annotations

from ..errors import PinConvError


class Level2Error(PinConvError):
    """Base error for a Level 2 run."""


class HandoffHashError(Level2Error):
    """The approved handoff does not match the plan or approval hashes."""


class MethodMatrixError(Level2Error):
    """A truth class was paired with a method it does not allow."""


class RecipeError(Level2Error):
    """A processing recipe is invalid or would damage a protected region."""


class LicenceBlockedError(Level2Error):
    """A source or candidate may not be used for commercial output."""


class BudgetError(Level2Error):
    """The budget does not reconcile with the approved estimates."""


class FlowError(Level2Error):
    """The production graph is cyclic or out of order."""


class GateOrderError(Level2Error):
    """A gate was requested out of order or without its approval."""


class SpendNotAuthorisedError(Level2Error):
    """A paid call was attempted before Gate 2A approval."""
