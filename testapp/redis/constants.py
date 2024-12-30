import enum
from typing import Hashable

JsonSerializable = dict[Hashable, Hashable] | list[Hashable] | Hashable
DEFAULT_TTL_SECONDS = 60 # 1 minute

class Namespace(enum.Enum):
    TEST = "test"
    RATE_LIMIT = "rate_limit"