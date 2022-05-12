import dataclasses

@dataclasses.dataclass(order=False, kw_only=True)
class Event:
    timestamp: int
    def __lt__(x, y):
        return x.timestamp < y.timestamp
    def __le__(x, y):
        return x.timestamp <= y.timestamp
    def __gt__(x, y):
        return x.timestamp > y.timestamp
    def __ge__(x, y):
        return x.timestamp >= y.timestamp
    def __eq__(x, y):
        return x.timestamp == y.timestamp
    def __ne__(x, y):
        return x.timestamp != y.timestamp
    def __call__(self, engine):
        return handle_event(self, engine)
    def asdict(self):
        return dataclasses.asdict(self)
    def type_str(self):
        return event_type_str[type(self)]

@dataclasses.dataclass
class HighEnergyScan(Event):
    user: str
    constellations: list

@dataclasses.dataclass
class HighEnergyScanAnnouncement(Event):
    user: str
    constellations: list

def handle_high_energy_scan(event: HighEnergyScan, engine):
    #TODO implement adding scan call and registering it to all players in the constellations
    if len(event.constellations) == 1:
        return (f"High Energy Scan Released, ships and structures in the constellation {event.constellations[0]} have received new valid destinations. Check /destinations", "broadcast", event.timestamp)
    if len(event.constellations) == 2:
        return (f"High Energy Scan Released, ships and structures in the constellations {event.constellations[0]} and {event.constellations[1]} have received new valid destinations. Check /destinations", "broadcast", event.timestamp)
    if len(event.constellations) >= 3:
        const_names = [const for const in (event.constellations[0:-1])]
        const_list = ", ".join(const_names)
        return (f"High Energy Scan Released, ships and structures in the constellations {const_list}, and {event.constellations[-1]} have received new valid destinations. Check /destinations", "broadcast", event.timestamp)

def handle_high_energy_scan_announcement(event: HighEnergyScanAnnouncement, engine):
    if len(event.constellations) == 1:
        return (f"Superluminal ultracapacitor charging detected in {event.constellations[0]}. All ships and structures in the affected systems will receive high energy scan returns when the scan is released.", "broadcast", event.timestamp)
    if len(event.constellations) == 2:
        return (f"Superluminal ultracapacitor charging detected in {event.constellations[0]} and {event.constellations[1]}. All ships and structures in the affected systems will receive high energy scan returns when the scan is released.", "broadcast", event.timestamp)
    if len(event.constellations) >= 3:
        const_names = [const for const in (event.constellations[0:-1])]
        const_list = ", ".join(const_names)
        return (f"Superluminal ultracapacitor charging detected in {const_list}, and {event.constellations[-1]}. All ships and structures in the affected systems will receive high energy scan returns when the scan is released.", "broadcast", event.timestamp)

event_type_str = {
    HighEnergyScan: "HighEnergyScan",
    HighEnergyScanAnnouncement: "HighEnergyScanAnnouncement"
}

event_types = {
    "HighEnergyScan": HighEnergyScan,
    "HighEnergyScanAnnouncement": HighEnergyScanAnnouncement
}

event_handlers = {
    HighEnergyScan: [handle_high_energy_scan],
    HighEnergyScanAnnouncement: [handle_high_energy_scan_announcement]
}

def handle_event(event: Event, engine):
    handlers = event_handlers[type(event)]
    return [handler(event, engine) for handler in handlers]
