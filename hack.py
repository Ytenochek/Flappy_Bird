from pickle import dump

with open("data/data.fbd", "wb") as f:
    dump((100, 500, "yellow", [True, False, False]), f)
