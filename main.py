from helpers.players import PlayerPool

# Settings
MAGIC_NUMBER = 18022022
FILE = 'data/20220218.xlsx'

# Instantiate the rosters of: Tanks, Healers and DDs
pool = PlayerPool(FILE, prefer_resignation_order=False, seed=MAGIC_NUMBER)

# Check who were left out Tanks, Healers and DDs rosters:
pool.list_leftovers()

for group in pool.groups:
    print(group)