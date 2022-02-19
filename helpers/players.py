import random
import itertools
import pandas as pd
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

    def __len__(self):
        return len(self.roles)


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
        self.n_groups_to_create = self.set_player_roles()

        # Form players into groups
        self.form_groups()

    def add_players_from_excel(self, f):
        # Read the Config Excel file
        df = pd.read_excel(f)

        # Add players to the pool
        for _, x in df.iterrows():
            p = Player(name=x.Name, can_tank=x.Tank, can_dd=x.DD, can_heal=x.Healer)

            self.add_player(p)

    def form_groups(self):

        # Shuffle Team Names
        random.shuffle(potential_team_names)

        # Shuffle player list before picking by order.
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

    def set_player_roles(self):
        # Get roles (in order)
        player_roles = [p.roles for p in self.players]

        # Product
        all_role_combinations = list(itertools.product(*player_roles))

        # Container for search results
        all_role_combination_group_sizes = []

        for c in all_role_combinations:
            # Check how many groups we could create with this combination
            x = min(c.count('tank'), c.count('heal'), c.count('dd') // 2)

            all_role_combination_group_sizes.append(x)

        # This is the maximum size group we can create
        n_groups = max(all_role_combination_group_sizes)

        # Container for search results
        potential_roles = []

        for x, y in zip(all_role_combinations, all_role_combination_group_sizes):
            if y == n_groups:
                potential_roles.append(x)

        # Choose list of roles
        chosen_roles = random.choice(potential_roles)

        for player, role in zip(self.players, chosen_roles):
            # Tell Player that it is in roster
            player.reserve(role)

        # Verbose
        print(f"[INFO] Out of {len(player_roles)} players, we can create {len(all_role_combinations)} different role combinations.")
        print(f"[INFO] {len(potential_roles)}/{len(all_role_combinations)} combinations allow forming a group of {n_groups} including all required roles.")

        return n_groups
