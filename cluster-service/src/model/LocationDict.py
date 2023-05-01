import copy
from collections import abc
from dataclasses import asdict

class LocationDict(abc.Collection):
    def __init__(self, location_dict):
        """
        Initializes the wrapper for the dictionary of locations.
        :param location_dict: Dictionary of locations keyed by their uuid.
        """
        self.locations = copy.deepcopy(location_dict)

    def set_label(self, key: str, label: int):
        """
        Set the location's label representing cluster-membership
        :param key: uuid of the location
        :param label: cluster-membership
        """
        self.locations[key].label = label

    def json_list(self) -> list[dict]:
        """
        Returns a json serializable list of the dictionary.
        :return: list of dict objects that correspond the runyourdinner specification
        """
        return [{id: asdict(loc)} for id, loc in self.locations.items()]

    def __getitem__(self, key: str):
        return self.locations[key]

    def __len__(self):
        return len(self.locations)

    def __contains__(self, item):
        return item in self.locations.keys()

    def __iter__(self):
        return iter(self.locations)

