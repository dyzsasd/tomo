from tomo.utils.types import get_event_union

from .builtin import *
from .base import Event

EventUnion = get_event_union(Event)
