import dataclasses


@dataclasses.dataclass(frozen=True)
class Entry:
    term: str
    score: float
