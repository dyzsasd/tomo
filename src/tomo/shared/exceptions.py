from dataclasses import dataclass
import json
from packaging import version
from typing import Optional, Text

import jsonschema
from ruamel.yaml.error import (
    MarkedYAMLError,
    MarkedYAMLWarning,
    MarkedYAMLFutureWarning,
)

from .constants import MINIMUM_COMPATIBLE_VERSION


class TomoException(Exception):
    """Base exception class for all errors raised by Tomo.

    These exceptions result from invalid use cases and will be reported
    to the users, but will be ignored in telemetry.
    """


class TomoCoreException(TomoException):
    """Basic exception for errors raised by Tomo Core."""


class TomoFatalException(TomoCoreException):
    """Exception which cannot be recovered."""


class BadParameter(TomoFatalException):
    """Exception which cannot be recovered."""

