import pandas as pd
import numpy as np
import json
import re
import spacy
import string


class MonsterFeatures:

    def __init__(self):
        self.df = pd.DataFrame()
        self.unsupported_keys = ["legendary", "mythic"]
        self.trash_keys = ["dragonCastingColor", "environment", "alias", "_isCopy", "soundClip.path", "soundClip.type",
                           "altArt", "conditionInflictLegendary", "variant", "srd", "group", "otherSources",
                           "isNamedCreature", "familiar", "type.tags", "type.type", "languageTags", "isNpc",
                           "legendaryGroup.source", "legendaryGroup.name", "hasToken", "languages", "alignment", "type",
                           "page", "source"]  # Keep Name just for Debugging
        self.tag_keys = ["size", "conditionImmune", "conditionInflictSpell", "spellcastingTags", "conditionInflict",
                         "miscTags", "damageTags", "actionTags", "senseTags", "traitTags", "senses", "vulnerable",
                         "immune", "resist"]

        self.nlp = spacy.load("en_core_web_sm")
        # speed, type
        # vulnerable, reaction, action, immune, spellcasting, trait, resist

    def read_json_files(self, list_of_files):
        list_of_dataframes = []
        for file in list_of_files:
            with open(file, "r") as f:
                data = json.loads(f.read())
            if "monster" in data:
                list_of_dataframes.append(pd.json_normalize(data, "monster"))

        self.df = pd.concat(list_of_dataframes, ignore_index=True)

    def save(self, path):
        self.df.to_pickle(path + ".pkl")

    def load(self, path):
        self.df = pd.read_pickle(path + ".pkl")

    def clean_data(self):
        # Keep entries with proper CR
        self.__parse_valid_cr()
        # Remove unneeded or unsupported keys
        self.__remove_copy()
        self.__remove_unsupported_keys()
        self.__remove_trash_keys()
        # Remove all empty columns
        self.df.dropna(axis=1, how="all", inplace=True)
        # Convert tag keys to one-hot columns
        self.__convert_tag_keys()
        # Convert Skills:
        self.__extract_number_of_proficiencies("skill")
        self.__extract_number_of_proficiencies("save")
        # Clean up hp.average
        self.__clean_hp()
        # Join text data
        self.__clean_text_data("trait")
        self.__clean_text_data("action")
        self.__clean_text_data("reaction")
        # Clean spellcasting:
        self.__clean_spellcasting()
        # Clean Speeds
        self.__clean_speed()

    def __remove_copy(self):
        copy_keys = self.get_keys_starting_with("_copy")
        self.remove_rows_with_invalid_keys(copy_keys)

    def get_keys_starting_with(self, start):
        return [key for key in self.df.keys() if key.startswith(start)]

    def __remove_unsupported_keys(self):
        self.remove_rows_with_invalid_keys(self.unsupported_keys)

    def __remove_trash_keys(self):
        self.df.drop(self.trash_keys, axis=1, inplace=True)

    def remove_rows_with_invalid_keys(self, keys):
        rows_to_delete = self.df[keys].notnull().any(1)
        self.df.drop(self.df[rows_to_delete].index, inplace=True)

    def __parse_valid_cr(self):
        # Replace challenge ratings, if needed
        self.df["cr"] = np.where(self.df["cr"].isnull(), self.df["cr.cr"], self.df["cr"])
        # Drop entries without challenge rating
        self.df.dropna(subset=["cr"], inplace=True)
        # Drop entries with unknown challenge rating
        self.df.drop(self.df[self.df["cr"] == "Unknown"].index, inplace=True)
        # Drop alternative (unsupported) challenge ratings.
        self.df.drop(["cr.cr", "cr.lair", "cr.coven"], axis=1, inplace=True)

    def __convert_tag_keys(self):
        for key in self.tag_keys:
            self.df[key] = self.unwrap_category_lists(key)

    def __extract_number_of_skill_proficiencies(self):
        skill_keys = self.get_keys_starting_with("skill")
        self.df["skill.proficiencies"] = self.df[skill_keys].notnull().astype("int").sum(axis=1)
        self.df.drop(skill_keys, axis=1, inplace=True)

    def __extract_number_of_proficiencies(self, string):
        keys = self.get_keys_starting_with("string")
        self.df[string + ".proficiencies"] = self.df[keys].notnull().astype("int").sum(axis=1)
        self.df.drop(keys, axis=1, inplace=True)

    def __clean_hp(self):
        # Fill missing HP values with first number in hp.special:
        self.df["hp.average"].fillna(self.df["hp.special"].str.extract(r'(^\d*)').squeeze(), inplace=True)

    def unwrap_category_lists(self, key):
        return self.df[key].apply(lambda x: self.__extend_dicts(x, key))

    def __extend_dicts(self, value, key):
        tmp = []
        if isinstance(value,list):
            for e in value:
                if isinstance(e, dict):
                    if key in e:
                        tmp.extend(e[key])
                else:
                    tmp.append(e)
        if isinstance(value, str):
            return value
        else:
            return tmp

    def __clean_text_data(self, key):
        # Save number of different entries:
        self.df["number_of_" + key + "s"] = self.df[key].apply(lambda x: len(x) if isinstance(x, list) else 0)
        #Join all entries into one body of text
        # self.df = self.df.apply(lambda row: self.preprocess_text(row, key) if isinstance(row[key], list) else "", axis=1)
        self.df["processed_"+key] = self.df.apply(
            lambda x: self.preprocess_text(x[key], x["name"]) if isinstance(x[key], list) else "",
            axis=1)
        self.df[key] = self.df["processed_"+key]
        self.df.drop("processed_"+key, axis=1)
        # #Extract and substitute dnd5e-tk specific commands:
        # dnd5e_tk_commands = re.compile(r"{@([^}\s]*)\s*([^}]*)}?")
        # self.df[key] = self.df[key].apply(lambda x: dnd5e_tk_commands.sub(r"dndtk_\1", x))
        # for index, row in self.df.iterrows():
        #     action = row[key]
        #     names = row["name"].split(" ")
        #     for name in names:
        #         print(name)
        #         print(action)
        #         reg = re.compile(r"{}".format(name),re.IGNORECASE)
        #         action = reg.sub("name_string", action)
        #     row[key] = action

    def preprocess_text(self, input, name):
        #Join entries to single block of text:
        entries = [e if "entries" in d else '' for d in input for e in d["entries"]]
        entry_string = [i if isinstance(i, str) else '' for i in entries]
        text = "\n".join(entry_string)
        #Substitute dnd5e toolkit specific commands:
        dnd5e_tk_commands = re.compile(r"{@([^}\s]*)\s*([^}]*)}?")
        text = dnd5e_tk_commands.sub(r"dndtk_\1", text)
        #Substitute creatures names:
        remove_brackets = re.compile(r"\(.*\)")
        name_str = remove_brackets.sub("",name)
        name_words = name_str.split(" ")
        for n in name_words:
            if n.lower() not in ["of", "the"] and len(n) > 1:
                name_regex = re.compile(r"{}".format(n),re.IGNORECASE)
                text = name_regex.sub("name_string", text)
        #Create tokens from lmma with stop words
        doc = self.nlp(text)
        tokens = [ token.lemma_ for token in doc if token.is_stop is False and token.text not in string.punctuation]
        return " ".join(tokens)


        # entries = [e if "entries" in d else '' for d in value for e in d["entries"]]
        # entry_string = [i if isinstance(i, str) else '' for i in entries]
        # return "\n".join(entry_string)

    def __clean_spellcasting(self):
        # To begin with just track "innate" and normal spellcasting
        self.df["spellcasting"] = self.df["spellcasting"].apply(
            lambda x: self.extract_name(x) if isinstance(x, list) else "")
        # # Create one-hot columns:
        # self.df = self.replace_column_with_one_hot("spellcasting")

    @staticmethod
    def extract_name(value):
        names = [e["name"] for e in value if "name" in e]
        output = []
        for n in names:
            if n.startswith("Innate Spellcasting"):
                output.append("Innate-Spellcasting")
            elif n.startswith("Spellcasting"):
                output.append("Spellcasting")
        return output

    def __clean_speed(self):
        self.df["speed.walk"].fillna(0., inplace=True)
        self.df["speed.swim"].fillna(0., inplace=True)
        self.df["speed.climb"].fillna(0., inplace=True)
        self.df["speed.burrow"].fillna(0., inplace=True)
        self.df["speed.fly"].fillna(0., inplace=True)

        self.df.drop("speed.fly.number", axis=1, inplace=True)
        self.df.drop("speed.walk.number", axis=1, inplace=True)
        self.df.drop("speed.burrow.number", axis=1, inplace=True)
        self.df.drop("speed.climb.number", axis=1, inplace=True)

        self.df.drop("speed.fly.condition", axis=1, inplace=True)
        self.df.drop("speed.walk.condition", axis=1, inplace=True)
        self.df.drop("speed.burrow.condition", axis=1, inplace=True)
        self.df.drop("speed.climb.condition", axis=1, inplace=True)

        # convert canHover:
        self.df["speed.canHover"] = self.df["speed.canHover"].fillna(False).apply(int)

    def get_clean_features(self):
        clean_features = ["hp.average", "str", "dex", "con", "int", "wis", "cha"]
        clean_features.extend(self.get_keys_starting_with("speed."))
        clean_features.extend(["skill.proficiencies", "save.proficiencies"])
        clean_features.extend(self.get_keys_starting_with("number_of_"))
        clean_features.extend(self.tag_keys)
        clean_features.extend(["action","reaction","trait"])
        clean_features.extend(["spellcasting"])
        return self.df[clean_features]

    def get_target(self):
        return self.df["cr"]
