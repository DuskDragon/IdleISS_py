from .event import event_types, HighEnergyScan, HighEnergyScanAnnouncement
from .ship import ShipLibrary
from .universe import Universe
from .universe import SolarSystem
from .user import User
from .scan import Scanning
import bisect

#bisect tools
def bisect_index(a, x):
    'Locate the leftmost value in sorted list a exactly equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    return None

def bisect_is_present(a, x):
    'Return if sorted list a contains x'
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return True
    return False

def human_time_diff(duration_in_seconds):
    if duration_in_seconds == 0:
        return 'just now'
    suffix = "ago"
    if duration_in_seconds < 0:
        suffix = "in the future"
        duration_in_seconds = duration_in_seconds * -1
    if duration_in_seconds < 90:
        return f"{duration_in_seconds}s {suffix}"
    if duration_in_seconds < 90*60:
        return f"{int(duration_in_seconds/60)}m {suffix}"
    if duration_in_seconds < 36*60*60:
        return f"{int(duration_in_seconds/60/60)}h {suffix}"
    else:
        return f"{int(duration_in_seconds/60/60/24)}d {suffix}"

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
    valid_types = ['broadcast', 'debug', 'admin', 'major_event']
    container_order = ['time', 'mess_type', 'message']
    def __init__(self, message=None, mess_type=None, time=None):
        self.container = []
        ## this allows creation an empty array that can easily be extended
        if message == None or mess_type == None or time == None:
            return
        ## if not called using MessageManager() then validate entered node
        if mess_type not in self.valid_types:
            raise ValueError(f"MessageManager: passed an invalid message type: {mess_type}")
        if message == None or message == '':
            raise ValueError(f"MessageManager: passed an empty message. {time}, {mess_type}")
        if time < 0:
            raise ValueError(f"MessageManager: passed a negative timestamp {mess_type}, {message}")
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
        self.current_channel_list = set()
        self.universe = Universe(universe_filename)
        self.library = ShipLibrary(library_filename)
        self.scanning = Scanning(scanning_filename, self.library)

        # The current world_timestamp - only updated whenever the world
        # is updated by calling update_world with the current/latest
        # simulated timestamp. Starts at 0 to show no update_world calls
        # have occured yet
        self.world_timestamp = 0

        # this should be a bisect managed sorted list and must be thread safe.
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

        ## load _engine_events from save file. Dump current events:
        self._engine_events = []
        ## load each event in order, this ensures they are in order now
        for event in savedata['_engine_events']:
            prepared_event = event_types[event[0]](**event[1])
            bisect.insort(self._engine_events, prepared_event)
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
        events_save = [(event.type_str(), event.asdict()) for event in self._engine_events]
        sav_current_channel_list = list(self.current_channel_list)
        sav_current_channel_list.sort()
        save = {
            '_engine_events': events_save,
            'current_channel_list': sav_current_channel_list,
            'users': usersave,
            'universe': self.universe.generate_savedata(),
            'world_timestamp': self.world_timestamp
        }
        return save

    def _add_event(self, event):
        event.timestamp = max(event.timestamp, self.world_timestamp)
        bisect.insort(self._engine_events, event)

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

    def _construct_structure(self, now, user, system, structure):
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
        return MessageManager(message, 'broadcast', now)

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

    def _prune_destinations(self, destination_data):
        #prune destinations for users
        for user_id, user in self.users.items():
            user.destinations = list(
                filter( # drop only exact matches for fields 0, 1, and 2
                    lambda dest: not (dest[0] == destination_data[0] and
                                      dest[1] == destination_data[1] and
                                      dest[2] == destination_data[2])
                    , user.destinations)
            )
        #TODO: prune_destiations for fleets

    def inspect_user(self, username):
        if username not in self.users:
            return "error: no such user"
        return self.users[username].inspect()

    def info_system(self, system_name):
        temp = self.universe.master_dict.get(system_name, None)
        if type(temp) != SolarSystem:
            return "error: no such system"
        else:
            return temp.inspect()

    def user_destinations(self, now, username, max_length, max_messages):
        if username not in self.users:
            return "error: no such user"
        destinations = self.users[username].destinations
        formatted_strings = [""]
        counter = 1
        for destination in destinations:
            dest_type = destination[0]
            if dest_type == "SiteInstance":
                dest_sys = self.universe.systems[destination[2]]
                dest_site = None
                for site in dest_sys.sites:
                    if site.site_id == destination[1]:
                        dest_site = site
                        break
                if dest_site == None:
                    raise RuntimeError(f"IdleISS.core.user_destinations could not find SiteInstance id {destination[1]} on system {dest_sys.name}")
                site_info = self.scanning.site_data[site.name].initial_description
                if len(destination) == 3:
                    new_dest_str = f"{counter}. System: {dest_sys.name}, Type: Scanned Site, Information: {site_info}\n"
                elif len(destination) == 5:
                    new_dest_str = f"{counter}. System: {dest_sys.name}, Type: Scanned Site, Information: {site_info} Source: {destination[3]} {human_time_diff(now-destination[4])}\n"
                else:
                    raise RuntimeError(f"IdleISS.core.user_destinations SiteInstance has a length ({len(destination)}) with an unsupported data-to-string conversion")
            else:
                raise RuntimeError(f"IdleISS.core.user_destinations found invalid destination type for user: {username}. Destination was a '{dest_type}'")
            #check if composed destination string is too long
            if len(new_dest_str) > max_length:
                raise RuntimeError(f"IdleISS.core.user_destinations new destination string is longer than max_length, cannot send destination information")
            #check if composed destinations message is too long
            if (len(formatted_strings[-1]) + len(new_dest_str)) > max_length:
                #check if we are at messages limit
                if len(formatted_strings)+1 == max_messages:
                    #if at message limit add note that we have too many messages and eject
                    formatted_strings.append("You have access to addtional destinations, but they cannot be listed due to length limitations.\n")
                    return formatted_strings
                formatted_strings.append("")
            formatted_strings[-1] += new_dest_str
            counter += 1
        #end destinations loop
        if len(formatted_strings[0]) == 0:
            formatted_strings[0] += "No destinations are available at this time. Hint: One way to find destinations is by using the scanning menu.\n"
        for x in range(len(formatted_strings)): #since we only need the index this is slightly faster than enumerate
            formatted_strings[x] = formatted_strings[x].rstrip()
        return formatted_strings

    def _highenergyscan(self, constellations, timestamp):
        #collect all scannables
        scannables = []
        players = []
        lookup = self.scanning
        for constellation_name in constellations:
            constellation = self.universe.master_dict[constellation_name]
            for system in constellation.systems:
                #check for players using structures
                for user_id, structure in system.structures.items():
                    if self.users[user_id] not in players:
                        players.append(self.users[user_id])
                #TODO: check for players using fleets
                # for user_id, fleet in system.fleets.items():
                    # if self.users[user_id] not in players:
                        # players.append(self.users[user_id])
                for site in system.sites:
                    if site.is_scannable(timestamp, lookup):
                        if site not in scannables:
                            #the random check to determine if site is scanned
                            #occurs here because only the player scanning initially
                            #detects all the sites, everyone else just gets the results
                            #for free. If scanning power changes per player it would
                            #need to be updated, but for now we will just do the
                            #check once here and not in the lower loop where sites
                            #are added to each player's destinations
                            #
                            #we use the main uni random here since it is a global dispatched
                            #event and not a transient application-side interaction
                            if self.universe.rand.random() < lookup.site_data[site.name].high_chance:
                                scannables.append(site)
        for player in players:
            for site in scannables:
                site_data = ["SiteInstance", site.site_id, site.system_id, "High Energy Scan", timestamp]
                present = False
                for destination in player.destinations:
                    if (site_data[0] == destination[0] and
                        site_data[1] == destination[1] and
                        site_data[2] == destination[2]):
                        present = True
                        break
                if not present:
                    player.destinations.append(site_data)

    def scan(self, rand, now, username, scan_type, grid_pack=None):
        if username not in self.users:
            return ("error: no such user", None)
        #this if/else block returns early with an error if cooldowns are not ready
        if scan_type == "high" or scan_type == "h":
            if self.users[username].last_high_scan == None:
                pass # avoid None errors for math below
            elif now < (self.users[username].last_high_scan +
                      self.scanning.settings.high_recharge
            ):
                return ("You are scanning too soon since your last scan of this type, please try again later.", None)
        elif scan_type == "focus" or scan_type == "f":
            if grid_pack == None:
                raise RuntimeError(f"IdleISS.core.scan of focus type called by {username} with no grid_pack selected at {now}.")
            elif grid_pack[0] < 0 or grid_pack[0] > (
                self.scanning.settings.focus_width_max *
                self.scanning.settings.focus_height_max
            ):
                raise RuntimeError(f"IdleISS.core.scan of focus type called by {username} with out of range at {now}.")
            if self.users[username].last_focus_scan == None:
                pass # avoid None errors for math below
            elif now < (self.users[username].last_focus_scan +
                      self.scanning.settings.focus_recharge
            ):
                return ("You are scanning too soon since your last scan of this type, please try again later.", None)
        elif scan_type == "low" or scan_type == "l":
            if self.users[username].last_low_scan == None:
                pass # avoid None errors for math below
            elif now < (self.users[username].last_low_scan +
                      self.scanning.settings.low_recharge
            ):
                return ("You are scanning too soon since your last scan of this type, please try again later.", None)
        else:
            raise RuntimeError(f"IdleISS.core.scan called with invalid scan type: {scan_type} by {username}")
        #after continuing past this block we are clear to execute scan as far as cooldowns are concerned
        constellation_list = []
        #collect constellations with an owned structure
        for sys_name, structure in self.users[username].resources.structures.items():
            const_name = self.universe.master_dict[sys_name].constellation
            const = self.universe.master_dict[const_name]
            if const not in constellation_list:
                constellation_list.append(const)
        lookup = self.scanning
        #collect scannables, we only need to do this for low and focus
        #in the future speed can be increased for non-high scans here
        scannables = []
        for constellation in constellation_list:
            for system in constellation.systems:
                for site in system.sites:
                    if site.is_scannable(now, lookup):
                        scannables.append(site)
        scanned = []
        if scan_type == "high" or scan_type == "h":
            ## update user info for high scan
            self.users[username].last_high_scan = now
            ## register future high scan global event
            const_names = [const.name for cost in constellation_list]
            self._add_event(HighEnergyScan(
                timestamp=now+1+self.scanning.settings.high_delay,
                user=username,
                constellations=const_names
            ))
            ## register high scan announcement now
            self._add_event(HighEnergyScanAnnouncement(
                timestamp=now+1,
                user=username,
                constellations=const_names
            ))
            return ("Charging ultracapacitors for wideband superluminal transmission. High energy scan pulse will be fired in approximately one hour. Please note this action will be extremely visible across the galaxy.", None)
        elif scan_type == "focus" or scan_type == "f":
            self.users[username].last_focus_scan = now
            scanned, grid = self.scanning.process_focus_sites(scannables, grid_pack[1], grid_pack[2], rand)
            site_text = ""
            for site in scanned:
                site_data = ["SiteInstance", site.site_id, site.system_id, "Focused Scan", now]
                present = False
                for destination in self.users[username].destinations:
                    if (site_data[0] == destination[0] and
                        site_data[1] == destination[1] and
                        site_data[2] == destination[2]):
                        present = True
                        break
                if not present:
                    self.users[username].destinations.append(site_data)
            if len(scanned) <= 0:
                return (f"Scan was successful, but it detected nothing notable at that frequency.", grid)
            elif len(scanned) <= 5:
                for i, v in enumerate(scanned):
                    site_test += f"{i+1}: {lookup.site_data[v.name].initial_description}\n"
                return (f"Scan was successful, results are as follows: \n{site_text}Dispatch fleets using the destinations menu.", grid)
            else:
                scanned.sort(reverse=True, key=lambda x: lookup.site_data[x.name].quality)
                for x in range(5):
                    site_text += f"{x+1}: {lookup.site_data[site[x].name].initial_description}\n"
                return (f"Scan was successful with {len(scanned)} results. Top five results are: \n{site_text}\nRemaining sites are accessable using the destinations menu.", grid)
        elif scan_type == "low" or scan_type == "l":
            self.users[username].last_low_scan = now
            for site in scannables:
                if rand.random() < lookup.site_data[site.name].low_chance:
                    scanned.append(site)
            site_text = ""
            for site in scanned:
                site_data = ["SiteInstance", site.site_id, site.system_id, "Low Energy Scan", now]
                present = False
                for destination in self.users[username].destinations:
                    if (site_data[0] == destination[0] and
                        site_data[1] == destination[1] and
                        site_data[2] == destination[2]):
                        present = True
                        break
                if not present:
                    self.users[username].destinations.append(site_data)
            if len(scanned) <= 0:
                return (f"Scan was successful, but it detected nothing notable in range.", None)
            elif len(scanned) <= 5:
                for i, v in enumerate(scanned):
                    site_text += f"{i+1}: {lookup.site_data[v.name].initial_description}\n"
                return (f"Scan was successful, results are as follows: \n{site_text}Dispatch fleets using the destinations menu.", None)
            else:
                scanned.sort(reverse=True, key=lambda x: lookup.site_data[x.name].quality)
                for x in range(5):
                    site_text += f"{x+1}: {lookup.site_data[site[x].name].initial_description}\n"
                return (f"Scan was successful with {len(scanned)} results. Top five results are: \n{site_text}\nRemaining sites are accessable using the destinations menu.", None)
        else:
            raise RuntimeError(f"IdleISS.core.scan called with invalid scan type: {scan_type} by {username} at {now}")

    def _update_sites(self, timestamp):
        for constellation in self.universe.constellations:
            system_count = len(constellation.systems)
            scannables = [[] for x in range(system_count)]
            #collect scannables references:
            for x in range(system_count):
                scannables[x] = constellation.systems[x]
            #update sites in self.universe using their references:
            self.scanning.gen_constellation_scannables(
                self,
                scannables,
                timestamp,
                self.universe.rand
            )

    def update_world(self, active_list, timestamp):
        """
        update_world will be the the major point of intersection as far as data
        modification between this engine and the outside world. Some usage of
        user abilities such as scanning will be edited outside of this function
        but everything else including managing fleets, events, and the results
        of abilities will be managed here.
        Every tick (chosen by the controller program) the controller must
        send the current timestamp along with the current user list.
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
        # evaulate that event as if it happened at that timestamp if
        # it's between self.world_timestamp and our new eval target
        # only works if the _engine_events list is sorted
        while len(self._engine_events) > 0:
            # if event is in the past relative to timestamp rewind to catch it
            if self._engine_events[0].timestamp < timestamp:
                next_event_timestamp = self._engine_events[0].timestamp
                event_results.extend(self._update_world(next_event_timestamp))
            else:
                #if next event is future or current, don't back up time
                break

        #### For Each User:
        for user_id in self.users:
            #### Pay Resources for User and Update total_idle_time
            user = self.users[user_id]
            if not user.in_userlist:
                # skip offline users.
                continue
            user.update(timestamp)
            #### Produce Units for User

        #### For the Full Gamestate:
        #### Update Depleted Scanning Sites and Update User Destinations for Sites only
        self._update_sites(timestamp)
        #### Random Events
        #### Calculate Battles
        #### Other

        time_diff = timestamp - self.world_timestamp
        engine_events = self._engine_events.copy()
        for engine_event in engine_events:
            # we know the engine_events are sorted so as soon as we hit one in the future, eject
            if engine_event.timestamp > timestamp:
                break
            else: # if not a future event, process it
                results = engine_event(self)
                for result in results:
                    event_message, event_mess_type, event_timestamp = result
                    event_results.append(message=event_message, mess_type=event_mess_type, time=timestamp)
                self._engine_events.remove(engine_event)

        self.world_timestamp = timestamp
        return event_results
