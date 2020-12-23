import glob
import json
import pandas as pd
import re
import pickle

list_of_spellbooks = glob.glob("data/spells/spells-*.json")
print(list_of_spellbooks)

list_of_dataframes = []
for file in list_of_spellbooks:
    with open(file, "r") as f:
        data = json.loads(f.read())
    if "spell" in data:
        list_of_dataframes.append(pd.json_normalize(data, "spell"))

df = pd.concat(list_of_dataframes, ignore_index=True)[["name", "level"]]
# df["name"] = df["name"].apply(str.lower)
# df.to_pickle("data/spell_database.pkl")

ua_re = re.compile(r"\s\(UA\)")

spell_dict = dict()
for index, row in df.iterrows():
    spell_name = row["name"]
    spell_name = re.sub(r"\s\(UA\)", "", spell_name)
    spell_dict[spell_name.lower()] = row["level"]

with open("data/spell_dict.pkl", "wb") as handle:
    pickle.dump(spell_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)