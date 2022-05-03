from .event import GameEngineEvent
from .ship import ShipLibrary
from .universe import Universe
from .user import User
from .scan import Scanning


class TimeOutofBounds(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidSaveData(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MessageManager(object):
    valid_types = ['broadcast', 'debug', 'admin']
    container_order = ['time', 'mess_type', 'message']
    def __init__(self, message=None, mess_type=None, time=None):
        self.container = []
        if message == None or mess_type == None or time == None:
            return
        if mess_type not in self.valid_types:
            raise ValueError(f"MessageManager: passed an invalid message type: {mess_type}")
        if message != None and message != '':
            self.container.append([time, mess_type, message])

    def extend(self, messages):
        if type(messages) != type(self):
            raise ValueError(f"MessageManager.extend: passed a non-MessageManager object")
        self.container.extend(messages.container)

    def append(self, message, mess_type, time):
        if mess_type not in self.valid_types:
            raise ValueError(f"MessageManager.append: passed an invalid message type: {mess_type}")
        if message != None and message != '':
            self.container.append([time, mess_type, message])

    def append(self, engine_event, timestamp):
        if type(engine_event) != GameEngineEvent:
            raise ValueError(f"MessageManager.append: passed a non-engine_event")
        mess_type = engine_event.kw.get('message_type', 'broadcast')
        self.container.append([timestamp, mess_type, engine_event()])

    @staticmethod
    def human_time_diff(time):
        if time == 0:
            return ''
        suffix = "ago: "
        if time < 0:
            suffix = "in the future: "
            time = time * -1
        if time < 90:
            return f"{time}s {suffix}"
        if time < 90*60:
            return f"{int(time/60)}m {suffix}"
        if time < 36*60*60:
            return f"{int(time/60/60)}h {suffix}"
        else:
            return f"{int(time/60/60/24)}d {suffix}"

    def get_broadcasts_with_time_diff(self, time):
        messages = []
        for mes in self.container:
            if mes[1] != 'broadcast':
                continue
            time_diff = time - mes[0]
            temp = f"{self.human_time_diff(time_diff)}{mes[2]}"
            messages.append(temp)
        return messages

    @property
    def is_empty(self):
        if self.container == []:
            return True
        else:
            return False

    @property
    def broadcasts(self):
        messages = []
        for mes in self.container:
            if mes[1] == 'broadcast':
                messages.append(mes[2])
        return messages

    @property
    def debug(self):
        messages = [None] * len(self.container)
        for mes in self.container:
            temp = f"{mes[0]}: {mes[1]}: {mes[2]}"
            messages.append(temp)
        return messages

    @property
    def admin(self):
        messages = []
        for mes in self.container:
            if mes[1] == 'admin':
                temp = f"{mes[0]}: {mes[2]}"
                messages.append(temp)
        return messages

    @property
    def broadcasts_with_times(self):
        messages = []
        for mes in self.container:
            if mes[1] == 'broadcast':
                temp = f"{mes[0]}: {mes[2]}"
                messages.append(temp)
        return messages


class GameEngine(object):

    def __init__(self, universe_filename, library_filename, scanning_filename, savedata=None):
        self.users = {}
        self.current_channel_list = []
        self.universe = Universe(universe_filename)
        self.library = ShipLibrary(library_filename)
        self.scanning = Scanning(scanning_filename, self.library)

        # The current world_timestamp - only updated whenever the world
        # is updated by calling update_world with the current/latest
        # simulated timestamp. Starts at 0 to show no update_world calls
        # have occured yet
        self.world_timestamp = 0

        # this should be a dequeue and must be thread safe.
        self._engine_events = []

        self._load_save(savedata)

    def _load_save(self, savedata):
        """
        A quick and straight-forward way to force in previous
        Game Engine state from a safedata block.
        """
        if savedata == {}:
            return
        if savedata == None:
            return
        #TODO add validation
        self._engine_events = savedata['_engine_events']
        self.current_channel_list = set(savedata['current_channel_list'])
        for usrid, usersave in savedata['users'].items():
            usersave['starting_system'] = self.universe.systems[usersave['starting_system']]
            self.users[usrid] = User(0, 0, usersave) #TODO? clean this up: User's ugly constructor
        self.universe.load_savedata(savedata['universe'])
        self.world_timestamp = savedata['world_timestamp']

    def generate_savedata(self):
        usersave = {}
        for usrid, usr in self.users.items():
            usersave[usrid] = usr.generate_savedata()
        save = {
            '_engine_events': self._engine_events, #TODO may not work in the future
            'current_channel_list': list(self.current_channel_list),
            'users': usersave,
            'universe': self.universe.generate_savedata(),
            'world_timestamp': self.world_timestamp
        }
        return save

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

    def _can_construct_structure(self, user, system, structure):
        """
        verify that a user can construct a structure in a system
            structures can not be built multiple times in the same system
            highsec can have multiple users' structures
            low and null can only have one user's structures
            structures can only be built in order of tier unless their tiers are below 0
        """
        # verify user has enough resources
        if not user.can_afford(structure):
            return (False, "cost", f"{user.id} does not have enough resources")
        # for highsec systems the system can not be owned, the structures are
        # still limited to only one of each per user.
        if user.has_structure(system, structure):
            return (False, "duplicate", f"{user.id} already owns a {structure['name']} in {system.name}")
        if system.security != "High":
            # for low and nullsec systems the system must be owned
            if system.owned_by == None:
                # system can be conquered
                if structure['sov_structure']:
                    # conquering structure:
                    return (True, "")
            # if not sov granting structure:
            if system.owned_by != user.id:
                return (False, "unowned", f"{user.id} does not own the system {system.name}")
        # verify that structures are being built in order
        # structures of tier higher than 0 must be built in order
        if structure['structure_tier'] > 0:
            struct_list = system.structures[user.id]
            tier_list = []
            for struct in struct_list:
                if type(struct['structure_tier']) == int:
                    tier_list.append(struct['structure_tier'])
                for num in range(1,structure['structure_tier']):
                    if num not in tier_list:
                        return (False, "order" f"{user.id} does not have the prerequisite buildings in {system.name}")
        return (True, "")

    def _register_new_user(self, user_id, timestamp):
        rand = self.universe.rand
        starting_region = rand.choice(self.universe.highsec_regions)
        starting_constellation = rand.choice(starting_region.constellations)
        starting_system = rand.choice(starting_constellation.systems)
        self.users[user_id] = user = User(user_id, starting_system)
        can_build = self._can_construct_structure(user, starting_system, self.library.starting_structure)
        if not can_build[0]:
            raise ValueError(can_build[2])
        user.construct_starting_structure(self.library.starting_structure)
        structure = self.library.starting_structure
        system = starting_system
        # announce new user has entered the game
        message = f"{user.id} has constructed their first structure, an {structure['name']} in {system.name}. Their journey in the universe begins here."
        return MessageManager(message, 'broadcast', timestamp)
        # TODO: register user in control system to generate events

    def _construct_structure(self, user, system, structure):
        new_conquered_system = False
        can_build = self._can_construct_structure(user, system, structure)
        if can_build[0]:
            user.construct_citadel(system, structure)
        else:
            raise ValueError(can_build[2])
        message = ''
        if new_conquered_system:
            message = f"{system.name} has been conquered by {user.id} with the construction of a {structure['name']}"
        else:
            message = f"{user.id} has constructed a new {structure['name']} in {system.name}"
        return MessageManager(message, 'broadcast', timestamp)

    def _user_joined(self, user_id, timestamp):
        messages = MessageManager()
        if user_id not in self.users:
            # create a user if that user_id is never seen before.
            messages.extend(self._register_new_user(user_id, timestamp))

        self.users[user_id].join(timestamp)
        return messages

    def _user_left(self, user_id, timestamp):
        if user_id not in self.users:
            return MessageManager(f"{user_id} called _user_left without being added", 'debug', timestamp)
        self.users[user_id].leave(timestamp)
        return MessageManager()

    def _update_user_list(self, active_list, timestamp):
        messages = MessageManager()
        for member in self.current_channel_list:
            if member not in active_list:
                messages.extend(self._user_left(member, timestamp))
        for member in active_list:
            if member not in self.current_channel_list:
                messages.extend(self._user_joined(member, timestamp))

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
            return MessageManager()
        if timestamp < self.world_timestamp:
            # can't go back in time.
            raise TimeOutofBounds("already processed this timestamp")

        event_results = self._update_world(timestamp)
        # only update user list after we update the worldstate
        event_results.extend(self._update_user_list(active_list, timestamp))
        return event_results

    def _update_world(self, timestamp):
        event_results = MessageManager()

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
                event_results.append(engine_event, timestamp)
                self._engine_events.remove(engine_event)

        self.world_timestamp = timestamp
        return event_results
