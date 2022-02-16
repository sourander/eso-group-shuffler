from helpers.players import PlayerPool

# Settings
MAGIC_NUMBER = 123
FILE = 'data/20220218.xlsx'

# Instantiate the rosters of: Tanks, Healers and DDs
pool = PlayerPool(FILE, seed=MAGIC_NUMBER, prefer_resignation_order=True)

# Check who were left out Tanks, Healers and DDs rosters:
pool.list_leftovers()

# Shuffle the nominees
pool.shuffle_players()

# Form teams
pool.form_groups()

for group in pool.groups:
    print(group)