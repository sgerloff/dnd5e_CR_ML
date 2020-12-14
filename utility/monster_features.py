import pandas as pd
import numpy as np
import json


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
                         "miscTags", "damageTags", "actionTags", "senseTags", "traitTags", "senses"]

    def read_json_files(self, list_of_files):
        list_of_dataframes = []
        for file in list_of_files:
            with open(file, "r") as f:
                data = json.loads(f.read())
            if "monster" in data:
                list_of_dataframes.append(pd.json_normalize(data, "monster"))

        self.df = pd.concat(list_of_dataframes, ignore_index=True)

    def save(self, path):
        self.df.to_csv(path)

    def load(self, path):
        self.df = pd.read_csv(path)

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
            self.df = self.replace_column_with_one_hot(key)

    def __extract_number_of_skill_proficiencies(self):
        skill_keys = self.get_keys_starting_with("skill")
        self.df["skill.proficiencies"] = self.df[skill_keys].notnull().astype("int").sum(axis=1)
        self.df.drop(skill_keys, axis=1, inplace=True)

    def __extract_number_of_proficiencies(self, string):
        keys = self.get_keys_starting_with("string")
        self.df[string + ".proficiencies"] = self.df[keys].notnull().astype("int").sum(axis=1)
        self.df.drop(keys, axis=1, inplace=True)

    def replace_column_with_one_hot(self, key):
        try:
            return self.df.drop(key, axis=1).join(self.get_one_hot_columns(self.df[key]))
        except TypeError:
            print("TypeError: Could not convert column '{}' to one-hot columns.".format(key))

    @staticmethod
    def get_one_hot_columns(series):
        stacked_series = series.apply(pd.Series).stack(dropna=False).reset_index(1, drop=True)
        return pd.get_dummies(stacked_series, prefix=series.name, sparse=True).groupby(level=0).sum()

    def get_features(self):
        feature_keys = ["str", "dex", "con", "int", "wis", "cha", "skill.proficiencies", "save.proficiencies"]
        for key in self.tag_keys:
            feature_keys.extend( self.get_keys_starting_with(key + "_") )

        # tmp = self.df[feature_keys]
        # print(tmp.isnull().values.any())
        # for key in feature_keys:
        #     print(key, self.df[key].isnull().values.any())

        return np.array(self.df[feature_keys])

    def get_target(self):
        return np.array(self.df["cr"])


