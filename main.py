import json
import glob

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

# for mon in monsters:
#     if "_isCopy" in mon:
#         for x,y in mon.items():
#             print(x,y)
#         print("\n")

# class KeyInventory:
#     def __init__(self, list_of_dictionaries):
#         self.known = dict()
#         self.get_inventory(list_of_dictionaries)
#
#     def get_inventory(self, list_of_dictionaries):
#         for item in list_of_dictionaries:
#             for key, value in item.items():
#                 if type(value) == dict:
#                     for nested_key, nested_value in value.items():
#                         unique_key = "%s_%s" % (key, nested_key)
#                         self.add_unknown(unique_key, nested_value)
#                 else:
#                     self.add_unknown(key, value)
#
#     def add_unknown(self, key, value):
#         if not key in self.known:
#             self.known[str(key)] = str(value)
#
# inventory = KeyInventory(monsters)
# f = open("data/key_inventory.txt", "w")
# for x,y in inventory.known.items():
#     f.write("%s \t\t\t %s\n" % (x,y))
# f.close()

