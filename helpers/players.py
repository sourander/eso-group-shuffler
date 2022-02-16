import random
import pandas as pd
from .team_names import potential_team_names


class Player:
    def __init__(self, name, can_tank, can_dd, can_heal):
        self.name = name

        self.roles = []
        self.roles.append('tank') if can_tank else None
        self.roles.append('heal') if can_heal else None
        self.roles.append('dd') if can_dd else None

        # Has been nominated to roster
        self.is_in_roster = False

    def reserve(self):
        self.is_in_roster = True

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
        self.tanks.append(p)

    def add_dd(self, p: Player):
        self.deedees.append(p)

    def add_healer(self, p: Player):
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
    def __init__(self, file_path: str, seed=None, prefer_resignation_order=True, n_groups=None):

        # Set static seed
        random.seed(seed)

        # Containers for Players and Groups
        self.players = []
        self.tanks = []
        self.deedees = []
        self.healers = []
        self.groups = []

        self.add_players_from_excel(file_path)
        if not prefer_resignation_order:
            random.shuffle(self.players)

        # Find out how many groups to create
        self.n_groups_to_create = self.define_max_group_count() if not n_groups else n_groups

        # Populate Tanks, Deedees and Healers
        self.populate_all_ranks()

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

        for i in range(self.n_groups_to_create):
            t = self.tanks.pop()
            d1 = self.deedees.pop()
            d2 = self.deedees.pop()
            h = self.healers.pop()

            n = potential_team_names.pop(0)

            g = Group(name=n)
            g.add_tank(t)
            g.add_dd(d1)
            g.add_dd(d2)
            g.add_healer(h)

            self.groups.append(g)

    def shuffle_players(self):
        """Shuffle the chosen Tanks, Healers and DDs
        """
        random.shuffle(self.tanks)
        random.shuffle(self.deedees)
        random.shuffle(self.healers)

    def add_player(self, p: Player):
        # Set of index and Player object
        self.players.append(p)

    def get_players(self, role=None):
        filtered_members = [p for p in self.players if role in p.roles and not p.is_in_roster]

        return filtered_members

    def list_leftovers(self):
        filtered_members = [str(p) for p in self.players if not p.is_in_roster]

        p = ", ".join(filtered_members)
        print("[INFO] The leftovers are: ", p)

    def define_max_group_count(self) -> int:
        """Estimate how many groups can be formed using the Players pool.
        """
        # Fetch All Players
        ts = self.get_players(role='tank')
        dds = self.get_players(role='dd')
        hls = self.get_players(role='heal')

        # Turn to set.
        all_available_players = set(ts + dds + hls)
        all_available_tanks_healers = set(ts + hls)

        # MAXIMUMS
        n_groups_of_four = len(all_available_players) // 4
        n_tank_healer_pairs = len(all_available_tanks_healers) // 2
        n_tanks = len(ts)
        n_heals = len(hls)
        n_deedee_pairs = len(dds) // 2

        print(
            f"[DEBUG] Choosing minimum between {n_groups_of_four} and and {n_tank_healer_pairs} "
            f"and {n_tanks} and {n_heals} and {n_deedee_pairs}")

        return min(n_groups_of_four, n_tank_healer_pairs, n_tanks, n_heals, n_deedee_pairs)

    def populate(self, role, n):
        # List all members with the wanted role
        nominees = self.get_players(role=role)

        # Sort by length (n_roles) to prefer those who are suitable to ONLY this role
        nominees = sorted(nominees, key=len)

        # Pick the n Players
        chosen = nominees[:n]

        # Mark Player as reserved. It is no longer available for Tanks, Healers or DDs.
        for c in chosen:
            c.reserve()

        return chosen

    def populate_all_ranks(self):
        n = self.n_groups_to_create

        self.tanks = self.populate('tank', n)
        self.healers = self.populate('heal', n)
        self.deedees = self.populate('dd', n * 2)
