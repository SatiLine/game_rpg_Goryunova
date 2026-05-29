import logging

logger = logging.getLogger(__name__)

LOCATIONS: dict[str, dict[str, object]] = {
    "таверна":           {"description": "Шумный зал с очагом.",          "connected_to": ["рыночная площадь", "улица"]},
    "кузница":           {"description": "Жарко. Звон молота о наковальню.", "connected_to": ["рыночная площадь"]},
    "рыночная площадь":  {"description": "Центр города. Торговцы, шум.",  "connected_to": ["таверна", "кузница", "лавка торговца", "улица"]},
    "лавка торговца":    {"description": "Полки с товарами.",              "connected_to": ["рыночная площадь"]},
    "улица":             {"description": "Мощёная улица.",                 "connected_to": ["таверна", "рыночная площадь"]},
}


class World:
    def __init__(self) -> None:
        self.hour = 10
        self.day  = 1

    def advance_time(self, hours: int = 1) -> None:
        self.hour += hours
        if self.hour >= 24:
            self.hour -= 24
            self.day += 1

    def time_of_day(self) -> str:
        if 6  <= self.hour < 12: return "утро"
        if 12 <= self.hour < 17: return "день"
        if 17 <= self.hour < 21: return "вечер"
        return "ночь"

    def get_context(self) -> dict[str, object]:
        return {"hour": self.hour, "day": self.day, "time": f"{self.hour:02d}:00, {self.time_of_day()}, день {self.day}"}

    def get_location_info(self, location: str) -> dict[str, object]:
        return LOCATIONS.get(location, {"description": "Неизвестно", "connected_to": []})

    def get_state(self) -> dict[str, object]:
        return {"hour": self.hour, "day": self.day, "time_label": self.time_of_day()}