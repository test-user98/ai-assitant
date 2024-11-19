from datetime import datetime, timedelta

class SlotsManager:
    def __init__(self):
        self.slots_data = {
            datetime.now().strftime('%Y-%m-%d'): [
                "9:00 a.m.", "10:00 a.m.", "11:00 a.m.", "4:00 p.m."
            ],
            (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'): [
                "9:00 a.m.", "10:00 a.m."
            ]
        }

    def get_available_slots(self, date):
        return self.slots_data.get(date, [])

    def book_slot(self, date, time):
        available_slots = self.slots_data.get(date, [])
        if time in available_slots:
            available_slots.remove(time)
            return True
        return False
