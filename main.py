import json
import glob

import pandas as pd

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
                monsters.append(mon)

print("I have read %d stat blocks of monsters!" % (len(monsters)) )


class CleanMonsterData:
    data = {}
    def __init__(self, monster):
        self.data = monster.copy()

    def drop_insignificant_keys(self):
        for key in ["isNpc", "source", "page", "passive", "languages", "hasToken", "languageTags", "miscTags", "senses", "_isCopy", "familiar"]:
            self.data.pop(key, None)

    def reduce_attributes(self):
        sum_of_attributes = 0
        for attribute in ["str", "dex", "con", "wis", "int", "cha"]:
            if attribute in self.data:
                sum_of_attributes += self.data[attribute]
                self.data.pop(attribute)
            else:
                print("Missing attribute %s!" % attribute)
        self.data["attribute_sum"] = sum

    def reduce_skill(self):
        if "skill" in self.data:
            skill_proficiencies = len(self.data["skill"])
            self.data.pop("skill")
            self.data["skill_proficiencies"] = skill_proficiencies
        else:
            self.data["save_proficiencies"] = 0

    def reduce_save(self):
        if "save" in self.data:
            save_proficiencies = len(self.data["save"])
            self.data.pop("save")
            self.data["save_proficiencies"] = save_proficiencies
        else:
            self.data["save_proficiencies"] = 0

    def reduce_senseTags(self):
        if not "senseTags" in self.data:
            self.data["senseTags"] = []


def getUniqueEntries(list, string):
    used = []
    for element in list:
        if string in element:
            for sub_element in element[string]:
                if not sub_element in used:
                    used.append(sub_element)
    return used

# used = []
# for mon in monsters:
#     if "actionTags" in mon:
#         for x in mon["actionTags"]:
#             if not x in used:
#                 used.append(x)

print( getUniqueEntries(monsters, "senseTags") )

# data = CleanMonsterData(monsters[0])
# data.reduce_senses()
# print(data.data["senseTag1"])

# for i in monsters:
#     if not "senseTags" in i:
#         print(i["name"])
