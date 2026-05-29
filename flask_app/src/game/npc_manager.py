import json

from src.game.npc import NPC


class NPCManager:
    def __init__(self, data_path: str) -> None:
        self.npcs: dict[str, NPC] = {}
        with open(data_path, encoding="utf-8") as f:
            for entry in json.load(f):
                npc = NPC(entry)
                self.npcs[npc.id] = npc

    def get(self, npc_id: str) -> NPC | None:
        return self.npcs.get(npc_id)

    def get_by_location(self, location: str) -> list[NPC]:
        return [n for n in self.npcs.values() if n.location == location]

    def tick_all(self, game_hour: int) -> None:
        for npc in self.npcs.values():
            npc.tick(game_hour)
