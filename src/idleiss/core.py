from .event import GameEngineEvent
from .ship import ShipLibrary
from .universe import Universe
from .user import User


class TimeOutofBounds(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class GameEngine(object):

    def __init__(self, universe_filename, library_filename):
        self.users = {}
        self.current_channel_list = []
        self.universe = Universe(universe_filename)
        self.library = ShipLibrary(library_filename)

        # The current world_timestamp - only updated whenever the world
        # is updated by calling update_world with the current/latest
        # simulated timestamp. Starts at 0 to show no update_world calls
        # have occured yet
        self.world_timestamp = 0

        # this should be a dequeue and must be thread safe.
        self._engine_events = []

    def _add_event(self, event_type, **kw):
        # this is a bit of a magic as we assume that any keyword
        # arguments that are called `timestamp` relates to the
        # current time and not earlier.  We check that the engine hasn't
        # processed any timestamp older relative to world_timestamp.
        # If the timestamp is in the past then we force to world_timestamp
        kw["timestamp"] = max(kw.get("timestamp",0), self.world_timestamp)
        # this means that events can only occur between ticks and if an
        # event occurs past the next tick we can safely ignore it until
        # the tick where it would "occur". This is very useful since
        # it allows us to schedule future events by simpily placing them
        # into this queue. Hopefully this does not lead to a queue
        # which is overly large and stuffed full of future events

        self._engine_events.append(GameEngineEvent(event_type, **kw))
        self._sort_engine_events()

    def _global_message(self, msg, timestamp):
        return msg

    def _debug_message(self, msg, timestamp):
        pass

    def _register_new_user(self, user_id, timestamp):
        rand = self.universe.rand
        starting_region = rand.choice(self.universe.highsec_regions)
        starting_constellation = rand.choice(starting_region.constellations)
        starting_system = rand.choice(starting_constellation.systems)
        self.users[user_id] = user = User(user_id, starting_system)
        user.construct_starting_structure(self.library.starting_structure)
        structure = self.library.starting_structure
        system = starting_system
        # announce new user has entered the game
        message = f"{timestamp}: {user.id} has constructed their first structure, an {structure['name']} in {system.name}. Their journey in the universe begins here."
        return [message]
        # TODO: register user in control system to generate events

    def _construct_structure(self, user, system, structure):
        new_conquered_system = False
        # for highsec systems the system can not be owned, the structures are
        # still limited to only one of each per user.
        if user.has_structure(system, structure):
            raise ValueError(f"{user.id} already owns a {structure['name']} in {system.name}")
        if system.security != "High":
            # for low and nullsec systems the system must be owned
            if system.owned_by == None:
                # system can be conquered
                if structure['sov_structure']:
                    # conquering structure:
                    user.conquer_new_system(system, structure)
                    new_conquered_system = True
            # if not sov granting structure:
            if system.owned_by != user.id:
                raise ValueError(f"{user.id} does not own the system {system.name}")
        user.construct_citadel(system, structure)
        message = ''
        if new_conquered_system:
            message = f"{system.name} has been conquered by {user.id} with the construction of a {structure['name']}"
        else:
            message = f"{user.id} has constructed a new {structure['name']} in {system.name}"
        return [message]

    def _user_joined(self, user_id, timestamp):
        messages = []
        if user_id not in self.users:
            # create a user if that user_id is never seen before.
            messages.extend(self._register_new_user(user_id, timestamp))

        self.users[user_id].join(timestamp)
        return messages

    def _user_left(self, user_id, timestamp):
        messages = []
        if user_id not in self.users:
            return messages
        self.users[user_id].leave(timestamp)
        return messages

    def _update_user_list(self, active_list, timestamp):
        messages = []
        for member in self.current_channel_list:
            if member not in active_list:
                temp = self._user_left(member, timestamp)
                if temp != None and temp != []:
                    messages.extend(temp)
        for member in active_list:
            if member not in self.current_channel_list:
                temp = self._user_joined(member, timestamp)
                if temp != None and temp != []:
                    messages.extend(temp)

        self.current_channel_list = set(active_list)
        return messages

    def inspect_user(self, username):
        if username not in self.users:
            return "error: no such user"
        return self.users[username].inspect()

    def info_system(self, system_name):
        for system in self.universe.systems:
            if system_name == system.name:
                return system.inspect()
        return "error: no such system"

    def _sort_engine_events(self):
        self._engine_events.sort(key=(lambda x:(x.kw["timestamp"])))

    def update_world(self, active_list, timestamp):
        """
        update_world will be the one point of intersection as far as data
        modification between this engine and the outside world.
        Every tick (chosen by the controller program) the controller must
        send the current timestamp along with the current user list and any commands
        possible example: "fleet engage <enemy player>"
        (direct control by user may never be implemented, but may be automatic)
        """
        if timestamp == self.world_timestamp:
            return []
        if timestamp < self.world_timestamp:
            # can't go back in time.
            raise TimeOutofBounds("already processed this timestamp")

        event_results = self._update_world(timestamp)
        # only update user list after we update the worldstate
        event_results.extend(self._update_user_list(active_list, timestamp))
        return event_results

    def _update_world(self, timestamp):
        event_results = []

        # recursive magic to hit each event in the future as queued
        if len(self._engine_events) > 0:
            # evaulate that event as if it happened at that timestamp if
            # it's between self.world_timestamp and our new eval target
            while self._engine_events[0].kw["timestamp"] < timestamp:
                next_event_timestamp = self._engine_events[0].kw["timestamp"]
                event_results.extend(self._update_world(next_event_timestamp))

        #### Pay Resources and Update total_idle_time
        for user_id in self.users:
            user = self.users[user_id]
            if not user.in_userlist:
                # skip offline users.
                continue

            user.update(timestamp)

            #### Random Events
            #### Calculate Battles
            #### Produce Units
            #### Other Events?

        time_diff = timestamp - self.world_timestamp
        engine_events = self._engine_events.copy()
        for engine_event in engine_events:
            # we know the engine_events are sorted so as soon as we hit one in the future, eject
            if engine_event.kw["timestamp"] > timestamp:
                break
            else: # if not a future event, process it
                result = engine_event()
                if result != None and result != '':
                    event_results.append(f"{timestamp}: {result}")
                self._engine_events.remove(engine_event)

        self.world_timestamp = timestamp
        return event_results
