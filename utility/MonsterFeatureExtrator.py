

class MonsterFeatureExtractor:
    stats = {}
    input_data = {}

    def __init__(self, monster):
        self.input_data = monster.copy()

        self.reduce_attributes()
        self.reduce_skill()
        self.reduce_save()
        self.reduce_hp()

    def reduce_attributes(self):
        sum_of_attributes = 0
        attribute_list = list()
        for attribute in ["str", "dex", "con", "wis", "int", "cha"]:
            if attribute in self.input_data:
                sum_of_attributes += self.input_data[attribute]
                attribute_list.append(self.input_data[attribute])
            else:
                print("Missing attribute %s!" % attribute)
        self.stats["attribute_sum"] = sum_of_attributes
        self.stats["attribute_list"] = attribute_list

    def reduce_skill(self):
        if "skill" in self.input_data:
            skill_proficiencies = len(self.input_data["skill"])
            self.input_data.pop("skill")
            self.stats["skill_proficiencies"] = skill_proficiencies
        else:
            self.stats["skill_proficiencies"] = 0

    def reduce_save(self):
        if "save" in self.input_data:
            save_proficiencies = len(self.input_data["save"])
            self.input_data.pop("save")
            self.stats["save_proficiencies"] = save_proficiencies
        else:
            self.stats["save_proficiencies"] = 0

    def reduce_hp(self):
        if "hp" in self.input_data:
            if "average" in self.input_data["hp"]:
                self.stats["hp"] = self.input_data["hp"]["average"]
        else:
            print("no Hp", self.input_data["name"])

    def get_feature_list(self):
        features = list()
        # features.append(self.stats["attribute_sum"])
        features.extend(self.stats["attribute_list"])
        features.append(self.stats["skill_proficiencies"])
        features.append(self.stats["save_proficiencies"])
        features.append(self.stats["hp"])
        return features

    def reduce_attacks(self):
        number_of_attacks = 0
        if self.has_multiattack():
            number_of_attacks = self.get_number_of_attacks_from_multiattack()

        self.stats["number_of_attacks"] = number_of_attacks

    def has_multiattack(self):
        multiattack = False
        if "action" in self.input_data:
            for e in self.input_data["action"]:
                if e["name"] == "Multiattack":
                    multiattack = True
        return multiattack

    def get_number_of_attacks_from_multiattack(self):
        number_of_attacks = 0
        for e in self.input_data["action"]:
            if e["name"] == "Multiattack":
                if len(e["entries"]) == 1:
                    self.interpret_multiattack_description(e["entries"][0])
        return number_of_attacks

    def interpret_multiattack_description(self, description):
        number_of_attacks = -1
        list_of_indicating_words = [" one ", " two ", " three ", " four ", " five ", " six ", " seven ",
                                    " eight ", " nine ",
                                    " ten ", " eleven ", " twelve "]
        list_of_alternative_words = [" once ", " twice "]

        # Description formatted like "The dragon makes three attacks: one with its bite and two with its claws."
        if "." in description:
            description_parts = description.split(". ")
            for part in description_parts:
                if " attack" in part:
                    # print(part, description_parts)
                    break
        else:
            print(description)
            # for word in list_of_indicating_words:
            #     if word in description_parts[0]:
            #         number_of_attacks = list_of_indicating_words.index(word)+1
            # if number_of_attacks < 0:
            #     print("Unknown description: ", description)
        # elif ". " in description:
        #     description_parts = description.split(". ")
            # print(description_parts)