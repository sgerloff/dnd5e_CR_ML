import glob
import json
import pandas as pd

list_of_spellbooks = glob.glob("data/spells/spells-*.json")
print(list_of_spellbooks)

list_of_dataframes = []
for file in list_of_spellbooks:
    with open(file, "r") as f:
        data = json.loads(f.read())
    if "spell" in data:
        list_of_dataframes.append(pd.json_normalize(data, "spell"))

df = pd.concat(list_of_dataframes, ignore_index=True)[["name", "level"]]
df.to_pickle("data/spell_database.pkl")