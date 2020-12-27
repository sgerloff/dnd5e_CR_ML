import pandas as pd
import numpy as np
import json
import re
import spacy
import string
import pickle
import random


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

        self.spellcaster_level = re.compile(r"([0-9]{1,2})[a-z]{1,2}[\s-]level")
        self.spell_dc = re.compile(r"\{\@dc\s([0-9]*)\}")
        self.spell_hit = re.compile(r"\{@hit}\s([0-9]*)\}")

        with open("data/spell_dict.pkl", "rb") as handle:
            self.spell_dict = pickle.load(handle)

        self.spell_book = dict()
        self.spell_regex = re.compile(r"\{\@spell\s(.*?)\}")
        # speed, type
        # vulnerable, reaction, action, immune, spellcasting, trait, resist

    def read_json_files(self, list_of_files):
        list_of_dataframes = []
        for file in list_of_files:
            with open(file, "r", encoding='utf-8') as f:
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
        if isinstance(value, list):
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
        # Join all entries into one body of text
        # self.df = self.df.apply(lambda row: self.preprocess_text(row, key) if isinstance(row[key], list) else "", axis=1)
        self.df["processed_" + key] = self.df.apply(
            lambda x: self.preprocess_text(x[key], x["name"]) if isinstance(x[key], list) else "",
            axis=1)
        self.df[key] = self.df["processed_" + key]
        self.df.drop("processed_" + key, axis=1)

    def preprocess_text(self, input, name):
        # Join entries to single block of text:
        entries = [e if "entries" in d else '' for d in input for e in d["entries"]]
        entry_string = [i if isinstance(i, str) else '' for i in entries]
        text = "\n".join(entry_string)
        # Substitute dnd5e toolkit specific commands:
        dnd5e_tk_commands = re.compile(r"{@([^}\s]*)\s*([^}]*)}?")
        text = dnd5e_tk_commands.sub(r"dndtk_\1", text)
        # Substitute creatures names:
        remove_brackets = re.compile(r"\(.*\)")
        name_str = remove_brackets.sub("", name)
        name_words = name_str.split(" ")
        for n in name_words:
            if n.lower() not in ["of", "the"] and len(n) > 1:
                name_regex = re.compile(r"{}".format(n), re.IGNORECASE)
                text = name_regex.sub("name_string", text)
        # Create tokens from lmma with stop words
        doc = self.nlp(text)
        tokens = [token.lemma_ for token in doc if token.is_stop is False and token.text not in string.punctuation]
        return " ".join(tokens)


    def __clean_spellcasting(self):
        tmp = self.df["spellcasting"].apply( lambda x: pd.Series(self.extract_spell_information(x)) )
        self.df = self.df.merge(tmp, left_index=True, right_index=True)
        self.df.drop("spellcasting", axis=1, inplace=True)

    def extract_spell_information(self, value):
        self.spell_book["magic_spellcaster_level"] = 0
        self.spell_book["magic_spell_max_dc"] = 0
        self.spell_book["magic_spell_max_hit"] = 0
        for i in range(10):
            self.spell_book["magic_" + str(i)+"_spells"] = 0
            self.spell_book["magic_" + str(i)+"_slots"] = 0
            self.spell_book["magic_at_will_" + str(i)+"_spells"] = 0
        if isinstance(value, list):
            levels = [0]
            dcs = [0]
            hits = [0]
            for entry in value:
                if "headerEntries" in entry:
                    tmp_levels, tmp_dcs, tmp_hits = self.parse_headerEntries(entry["headerEntries"])
                    levels.extend(tmp_levels)
                    dcs.extend(tmp_dcs)
                    hits.extend(tmp_hits)
                if "footerEntries" in entry:
                    tmp_levels, tmp_dcs, tmp_hits = self.parse_headerEntries(entry["footerEntries"])
                    levels.extend(tmp_levels)
                    dcs.extend(tmp_dcs)
                    hits.extend(tmp_hits)
                if "will" in entry:
                    tmp = self.parse_spell_levels(entry["will"])
                    for spell in tmp:
                        self.spell_book["magic_at_will_" + str(spell)+"_spells"] += 1
                if "daily" in entry:
                    self.parse_daily(entry["daily"])
                if "spells" in entry:
                    self.parse_spellbook(entry["spells"])
            levels = [ int(level) for level in levels ]
            dcs = [ int(dc) for dc in dcs]
            hits = [ int(hit) for hit in hits]
            self.spell_book["magic_spellcaster_level"] = max(levels)
            self.spell_book["magic_spell_max_dc"] = max(dcs)
            self.spell_book["magic_spell_max_hit"] = max(hits)
        return self.spell_book


    def parse_headerEntries(self, value):
        levels = []
        dcs = []
        hits = []
        for element in value:
            levels.extend(self.spellcaster_level.findall(element))
            dcs.extend(self.spell_dc.findall(element))
            hits.extend(self.spell_hit.findall(element))
        return levels, dcs, hits

    def parse_spell_levels(self, value):
        spells = []
        spell_levels = []
        for spell in value:
            spells.extend(self.spell_regex.findall(spell))
        for spell in spells:
            spell = str.lower(spell)
            spell = spell.split("|")[0].strip()
            if spell in self.spell_dict:
                spell_levels.append(self.spell_dict[spell])
            else:
                print("UNKNOWN SPELL:", spell)
                print(value)
        return spell_levels

    def parse_daily(self, value):
        if "1e" in value:
            self.add_random_spells(self.parse_spell_levels(value["1e"]), 1)
        if "1" in value:
            self.add_random_spells(self.parse_spell_levels(value["1"]), 1)
        if "2e" in value:
            self.add_random_spells(self.parse_spell_levels(value["2e"]), 2)
        if "2" in value:
            self.add_random_spells(self.parse_spell_levels(value["2"]), 2)
        if "3e" in value:
            self.add_random_spells(self.parse_spell_levels(value["3e"]), 3)
        if "3" in value:
            self.add_random_spells(self.parse_spell_levels(value["3"]), 3)

    def add_random_spells(self, spell_list, number=1):
        random_spells = []
        for n in range(number):
            random_spells.append( random.choice(spell_list) )
        for spell in random_spells:
            self.spell_book["magic_" + str(spell)+"_slots"] += 1
            self.spell_book["magic_" + str(spell)+"_spells"] += 1

    def parse_spellbook(self, value):
        if "0" in value:
            self.spell_book["magic_at_will_0_spells"] += len(value["0"]["spells"])
        for i in range(9):
            if str(i+1) in value:
                if "slots" in value[str(i+1)]:
                    self.spell_book["magic_" + str(i+1)+"_slots"] += value[str(i+1)]["slots"]
                if "spells" in value[str(i+1)]:
                    self.spell_book["magic_" + str(i+1)+"_spells"] += len(value[str(i+1)]["spells"])

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
        clean_features.extend(["action", "reaction", "trait"])
        clean_features.extend(self.get_keys_starting_with("magic_"))
        return self.df[clean_features]

    def get_target(self):
        return self.df["cr"]
