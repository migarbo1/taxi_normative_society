from enum import Enum

class Domain(Enum):
    SCHEDULE = 0
    QUEUE = 1

class Role(Enum):
    WORKING_DRIVER = 0
    RESTING_DRIVER = 1