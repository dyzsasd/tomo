from tomo.utils.types import get_sub_classes_union

from .builtin import *
from .flight_exchange import *
from .flight_fare_rules import *
from .weather import FindWeather

ActionUnion = get_sub_classes_union(Action)
