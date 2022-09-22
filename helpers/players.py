import random
import itertools
import pandas as pd
from functools import reduce
from operator import mul
from .team_names import potential_team_names


class Player:
    def __init__(self, name, can_tank, can_dd, can_heal):
        self.name = name

        self.roles = []
        self.roles.append('tank') if can_tank else None
        self.roles.append('heal') if can_heal else None
        self.roles.append('dd') if can_dd else None

        # This role has been chosen
        self.chosen_role = None

        # Belongs to a group named
        self.group_membership = None

    def reserve(self, role):
        self.chosen_role = role

    def set_group(self, groupname):
        self.group_membership = groupname

    def __str__(self):
        return self.name


class Group:
    def __init__(self, name="Unnamed Group"):
        self.name = name
        self.tanks = []
        self.deedees = []
        self.healers = []

    def add_tank(self, p: Player):
        p.set_group(self.name)
        self.tanks.append(p)

    def add_dd(self, p: Player):
        p.set_group(self.name)
        self.deedees.append(p)

    def add_healer(self, p: Player):
        p.set_group(self.name)
        self.healers.append(p)

    def __str__(self):
        t_stringified = ", ".join([t.name for t in self.tanks])
        dd_stringified = ", ".join([t.name for t in self.deedees])
        h_stringified = ", ".join([t.name for t in self.healers])

        lines = [
            f"Team {self.name}",
            "=" * 10,
            f"Tank: {t_stringified}",
            f"DDs: {dd_stringified}",
            f"Healer: {h_stringified}",
            " "
        ]
        return "\n".join(lines)


class PlayerPool:
    def __init__(self, file_path: str, prefer_resignation_order=False, seed=None, n_groups=None):

        # Set static seed
        self.prefer_resignation_order = prefer_resignation_order
        random.seed(seed)

        # Containers for Players and Groups
        self.players = []
        self.groups = []

        # Populate players list
        self.add_players_from_excel(file_path)

        # Set player roles up to n groups
        self.n_groups_to_create = self.determine_group_number()

        # Shuffle players
        self.shuffle_players()

        # Set player roles
        self.set_player_roles()

        # Form players into groups
        self.form_groups()

    def add_players_from_excel(self, f: str):
        # Read the Config Excel file
        df = pd.read_excel(f)

        # Add players to the pool
        for _, x in df.iterrows():
            p = Player(name=x.Name, can_tank=x.Tank, can_dd=x.DD, can_heal=x.Healer)

            self.add_player(p)

    def shuffle_players(self):
        # Shuffle player list
        if self.prefer_resignation_order:
            # Split players into first n and others
            n = self.n_groups_to_create * 4
            a = self.players[:n]
            b = self.players[n:]

            # Shuffle a and b
            random.shuffle(a)
            random.shuffle(b)

            # Merge shuffled a and b into new players roster
            self.players = a + b
        elif not self.prefer_resignation_order:
            random.shuffle(self.players)

    def form_groups(self):

        # Shuffle Team Names
        random.shuffle(potential_team_names)

        tanks = self.get_players('tank')
        heals = self.get_players('heal')
        deedees = self.get_players('dd')

        for i in range(self.n_groups_to_create):
            g = Group(name=potential_team_names.pop(0))
            g.add_tank(tanks.pop(0))
            g.add_dd(deedees.pop(0))
            g.add_dd(deedees.pop(0))
            g.add_healer(heals.pop(0))

            self.groups.append(g)

    def add_player(self, p: Player):
        # Set of index and Player object
        self.players.append(p)

    def get_players(self, role=None):
        filtered_members = [p for p in self.players if p.chosen_role == role and not p.group_membership]

        return filtered_members

    def list_leftovers(self):
        filtered_members = [str(p) for p in self.players if not p.group_membership]

        p = ", ".join(filtered_members)
        print("[INFO] The leftovers are: ", p)

    def determine_group_number(self, cmax_early_stopping=10 ** 7):
        # Find out how many role combinations are possible
        n_combinations = reduce(mul, [len(p.roles) or 1 for p in self.players])

        # List of lists. Each list element contains one player's roles as strings.
        player_roles = [p.roles for p in self.players]

        # Store largest candidate found. Start value.
        n_groups = 0

        # Verbose
        print(f"[INFO] Out of {len(player_roles)} players, "
              f"we can create {n_combinations} different role combinations.")

        for i, c in enumerate(itertools.product(*player_roles)):

            # Check how many groups could we create of this role combination
            c_candidate = min(c.count('tank'), c.count('heal'), c.count('dd') // 2)

            # Store if highest known
            if n_groups < c_candidate:
                n_groups = c_candidate

            # Early stopping.
            if i > cmax_early_stopping:
                break



        return n_groups

    def set_player_roles(self, role_store_early_stopping=10 ** 5):

        # Container for potential role combinations
        potential_roles = []

        # Player roles.
        player_roles = [p.roles for p in self.players]

        for i, c in enumerate(itertools.product(*player_roles)):

            # Check how many groups could we create of this role combination
            c_candidate = min(c.count('tank'), c.count('heal'), c.count('dd') // 2)

            # Keep condition
            if c_candidate == self.n_groups_to_create:
                potential_roles.append(c)

            # Early stopping
            if len(potential_roles) > role_store_early_stopping:
                break

        # Choose list of roles
        chosen_roles = random.choice(potential_roles)

        for player, role in zip(self.players, chosen_roles):
            # Tell Player that it is in roster
            player.reserve(role)


