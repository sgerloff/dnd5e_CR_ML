import json
import glob

from utility.KeyInventory import KeyInventory

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


inventory = KeyInventory(monsters)
f = open("data/key_inventory.txt", "w")
for x,y in inventory.known.items():
    f.write("%s \t\t\t %s\n" % (x,y))
f.close()