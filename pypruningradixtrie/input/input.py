import dataclasses


@dataclasses.dataclass
class Input:
    query: str
    score: float
