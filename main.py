import json
import glob

import pandas as pd
import matplotlib.pyplot as plt

list_of_bestiaries = glob.glob("data/bestiary/*.json")

monsters = []

for bestiary in list_of_bestiaries:
    with open(bestiary, "r") as f:
        data = json.loads(f.read())
    if "monster" in data:
        for mon in data.get("monster"):
            if "legendary" in mon:
                print("Omit legendary monster %s" % mon["name"])
            elif "mythic" in mon:
                print("Omit mythic monster %s" % mon["name"])
            elif "_copy" in mon:
                print("Omit copied monster %s" % mon["name"])
            elif "cr" in mon:
                if mon["cr"] == "Unknown":
                    print("Omit monster %s with unknown cr" % mon["name"])
                elif type(mon["cr"]) == dict:
                    tmp = mon["cr"]["cr"]
                    print(tmp)
                    mon["cr"] = tmp
                    monsters.append(mon)
                else:
                    monsters.append(mon)

print("I have read %d stat blocks of monsters!" % (len(monsters)))


def getUniqueEntries(list, string):
    used = []
    for element in list:
        if string in element:
            for sub_element in element[string]:
                if sub_element not in used:
                    used.append(sub_element)
    return used


#Plot Histogram:
# from utility.plot_monster_cr_histogram import plot_monster_cr_histogram
# plot_monster_cr_histogram(monsters, "data/cr_histogram.png")

# Extract features and write into X,y
from utility.MonsterFeatureExtrator import MonsterFeatureExtractor
import numpy as np

input_data = list()
input_target = list()
for mon in monsters:
    clean = MonsterFeatureExtractor(mon)
    input_data.append(clean.get_feature_list())
    input_target.append(mon["cr"])

X = np.array(input_data)
y = input_target

from models.logistic_regression import logistic_regression_model
model = logistic_regression_model(X,y)
model.plot_learning_curve( 'data/leaning_curve_logistic_regression_three_features.png' )

