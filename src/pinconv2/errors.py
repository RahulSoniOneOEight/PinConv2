"""Domain errors for PinConv2."""

from __future__ import annotations


class PinConvError(Exception):
    """Base error for PinConv2."""


class NotFoundError(PinConvError):
    """A project, revision or record does not exist."""


class InvalidTransitionError(PinConvError):
    """The project state does not allow this operation."""


class GateFailedError(PinConvError):
    """A validation, critique or approval gate refused the operation."""


class StoreError(PinConvError):
    """A record could not be written or would overwrite a different revision."""


class ApprovalRequiredError(PinConvError):
    """An operation needs a named human approval."""
