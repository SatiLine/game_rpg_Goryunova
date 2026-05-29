from enum import Enum


class NPCState(Enum):
    IDLE = "idle"
    WORKING = "working"
    SLEEPING = "sleeping"
    WANDERING = "wandering"
    TALKING = "talking"


class NPC:
    def __init__(self, data: dict[str, object]) -> None:
        self.id: str = str(data["id"])
        self.name: str = str(data["name"])
        self.role: str = str(data["role"])
        self.personality: str = str(data["personality"])
        self.schedule: dict[str, str] = dict(data["schedule"])  # type: ignore[call-overload]
        self.location: str = str(data["start_location"])
        self.long_term_memory: list[str] = list(data.get("long_term_memory", []))  # type: ignore[call-overload]
        self.state: NPCState = NPCState.IDLE
        self.memory: list[dict[str, str]] = []

    def tick(self, game_hour: int) -> None:
        if self.state == NPCState.TALKING:
            return
        for time_range, state_name in self.schedule.items():
            start, end = map(int, time_range.split("-"))
            in_range = (
                (game_hour >= start or game_hour < end)
                if start > end
                else (start <= game_hour < end)
            )
            if in_range:
                self.state = NPCState[state_name.upper()]
                return
        self.state = NPCState.IDLE

    def add_to_memory(self, role: str, content: str) -> None:
        self.memory.append({"role": role, "content": content})
        if len(self.memory) > 12:
            self.memory = self.memory[-12:]

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "location": self.location,
            "state": self.state.value,
        }
