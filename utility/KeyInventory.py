class KeyInventory:
    def __init__(self, list_of_dictionaries):
        self.known = dict()
        self.get_inventory(list_of_dictionaries)

    def get_inventory(self, list_of_dictionaries):
        for item in list_of_dictionaries:
            for key, value in item.items():
                if type(value) == dict:
                    for nested_key, nested_value in value.items():
                        unique_key = "%s_%s" % (key, nested_key)
                        self.add_unknown(unique_key, nested_value)
                else:
                    self.add_unknown(key, value)

    def add_unknown(self, key, value):
        if not key in self.known:
            self.known[str(key)] = str(value)