# ESO Group Shuffler

This is a helper tool for organizing Elder Scrolls Online guild group dungeon events. In those events, groups consisting of 4 players will enter a dungeon. That group should always have 1 tank, 2 DDs and 1 Healer.

A single player can master multiple roles, so they may register to the event using a fluid role. Example below:

* Player A: tank/heal
* Player B: tank/dd/heal
* Player C: dd
* Player Z: Any combination of tank/dd/heal

## Usage
Write the registered persons and their roles to `data/<date>.xlsx` using Excel or similar. Use the `data/example.xlsx` as a template.

After this, modify the settings in the `main.py` (code snippet shown below). The magic number will be used as the seed of randomness when shuffling the group. Depending how you choose the magic number, it can be used for validating the randomization process.
```python
# Settings
MAGIC_NUMBER = 123
FILE = 'data/20220218.xlsx'
```

Now you should be able to run the `main.py` succesfully.

The PlayerPool tries to automatically determine the number of groups you want to create. If needed, you can provide it the correct answer using the keyword argument `n_groups` (example below). There are some cases where the automatic n_groups definition will fail.

The PlayerPool does not shuffle the players before adding them to the tank/dd/healer roster. Thus, it will prefer those who are first in order in the Excel. If this is not desired, you can change the `prefer_resignation_order` to False.

```python
# Instantiate the rosters of: Tanks, Healers and DDs
pool = PlayerPool(FILE, seed=MAGIC_NUMBER, prefer_resignation_order=False, n_groups=2)
```
