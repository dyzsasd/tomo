from tomo.utils.types import get_sub_classes_union

from .builtin import *
from .base import Event

EventUnion = get_sub_classes_union(Event)
