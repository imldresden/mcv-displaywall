import time
from collections import namedtuple

from data_models.data_object import DataObject
from events.event_dispatcher import EventDispatcher
from selection_ctrl.utils.default_values import SelectionDataHolderDefaults

LastSelection = namedtuple('LastSelection', 'id single_selection time')


class SelectionDataHolder(EventDispatcher):
    __SELECTION_SET_ADDED = "selectionSetAdded"
    __SELECTION_SET_REMOVED = "selectionSetRemoved"

    __KEY_IDS = {}
    __LAST_CREATED_ID = ""

    def __init__(self, data_keys):
        """
        :param data_keys: The list of all data keys that this data holder observes.
        :type data_keys: list[str]
        """
        EventDispatcher.__init__(self)

        self.__data_keys = data_keys
        SelectionDataHolder.__KEY_IDS.update({key: -1 for key in self.__data_keys})

        # key -> selection set id     value -> selection set (list)
        self.__selection_sets = {}

        self._last_selection = LastSelection("", True, time.time())

    def __repr__(self):
        return "SDH : {}".format(self.__selection_sets)

    @property
    def data_keys(self):
        """
        :rtype: list[str]
        """
        return self.__data_keys

    @property
    def empty(self):
        """
        :rtype: bool
        """
        return len(self.__selection_sets) < 1

    @property
    def selection_sets(self):
        """
        :rtype: dict[str, list]
        """
        return self.__selection_sets

    @staticmethod
    def get_next_id(key):
        """
        Generates the next possible id for

        :param key: The key the id should be mapped to.
        :type key: str
        :return: The next free id for a key.
        :rtype: str
        """
        if key not in SelectionDataHolder.__KEY_IDS:
            return None

        SelectionDataHolder.__KEY_IDS[key] += 1
        SelectionDataHolder.__LAST_CREATED_ID = "{}|{}".format(key, SelectionDataHolder.__KEY_IDS[key])
        return SelectionDataHolder.__LAST_CREATED_ID

    @staticmethod
    def __remove_one_id(id):
        """
        Removes an id if its not needed. Only possible if its the last created one.

        :param id: The id that should be one removed from.
        :type id: str
        """
        if id != SelectionDataHolder.__LAST_CREATED_ID:
            return

        SelectionDataHolder.__KEY_IDS[id.split('|')[0]] -= 1

    @staticmethod
    def __same_key(id_a, id_b):
        """
        Checks if two ids have the same key.

        :param id_a: The first id.
        :type id_a: str
        :param id_b: The second id.
        :type id_b: str
        :return: Have both ids the same key.
        :rtype: bool
        """
        return id_a.split('|')[0] == id_b.split('|')[0]

    def check_if_selection_in_set(self, selection_set):
        """
        Checks if a selection set has elements that are already part of any selection set in this data holder.

        :param selection_set: The selection set to check for.
        :type selection_set: list
        :return: The list of ids of the selection set that contains elements in the given selection. None if no selection set was found.
        :rtype: list[str]
        """
        selection_set = self.__make_list_distinct(selection_set)

        ids = []
        for selection_set_id, current_selection_set in self.__selection_sets.iteritems():
            if len([sv for sv in selection_set if sv in current_selection_set]) > 0:
                ids.append(selection_set_id)

        return ids

    def get_selection_set(self, selection_set_id):
        """
        Looks for a selection set with the given id.
        
        :param selection_set_id: The id of the set that this methods is looking for.
        :type selection_set_id: str
        :return: The searched selection.
        :rtype: list
        """
        if selection_set_id not in self.__selection_sets:
            return []
        return self.__selection_sets[selection_set_id]

    def add_new_selection_set(self, selection_set, selection_set_id, single_selection=True):
        """
        Adds a complete new selection set with the given id.

        :param selection_set: The set of data that was selected.
        :type selection_set: list
        :param selection_set_id: The id for the selection set to add.
        :type selection_set_id: str
        :param single_selection: If this selection was a single one. If no other selection with the same flag can be
                                 added to this one in a specific time period.
        :type single_selection: bool
        :return: The id used for this selection and the change that has happened on the given selection set.
        :rtype: tuple[str, list]
        """
        if len(selection_set) < 1:
            return selection_set_id, []
        if selection_set_id in self.__selection_sets:
            return selection_set_id, []
        selection_set = self.__make_list_distinct(selection_set)

        now = time.time()
        added = False
        if not single_selection and not self._last_selection.single_selection and self._last_selection.id in self.__selection_sets:
            if now - self._last_selection.time <= SelectionDataHolderDefaults.TIME_BETWEEN_NOT_SINGLE_SELECTIONS / 1000:
                if SelectionDataHolder.__same_key(selection_set_id, self._last_selection.id):
                    added = True
                    SelectionDataHolder.__remove_one_id(selection_set_id)
                    selection_set_id = self._last_selection.id
                    self.__selection_sets[selection_set_id].extend(selection_set)

        if not added:
            self.__selection_sets[selection_set_id] = selection_set

        self._last_selection = LastSelection(selection_set_id, single_selection, now)
        self.dispatch(self.__SELECTION_SET_ADDED, sender=self, selection_set_id=selection_set_id, selection_diff=selection_set)
        return selection_set_id, selection_set

    def add_selection_to_set(self, selection_set, selection_set_id):
        """
        Adds a selection to a given selection set.

        :param selection_set: The set of data that was selected.
        :type selection_set: list
        :param selection_set_id: The id for the selection set to add.
        :type selection_set_id: str
        :return: The change that has happened on the given selection set.
        :rtype: list
        """
        if len(selection_set) < 1:
            return []
        if selection_set_id not in self.__selection_sets:
            return []
        selection_set = self.__make_list_distinct(selection_set)

        self.__selection_sets[selection_set_id].extend(selection_set)
        self.dispatch(self.__SELECTION_SET_ADDED, sender=self, selection_set_id=selection_set_id, selection_diff=selection_set)
        return selection_set

    def remove_selection_from_set(self, selection_set, selection_set_id):
        """
        Removes a selection from a given selection set.

        :param selection_set: The set of data that was selected.
        :type selection_set: list
        :param selection_set_id: The id for the selection set to remove.
        :type selection_set_id: str
        :return: The change that has happened on the given selection set.
        :rtype: list
        """
        if len(selection_set) < 1:
            return []
        if selection_set_id not in self.__selection_sets:
            return []
        selection_set = self.__make_list_distinct(selection_set)

        new_selection_set = [s for s in self.__selection_sets[selection_set_id] if s not in selection_set]
        # Remove the complete set if its empty.
        if len(new_selection_set) < 1:
            selection_diff = self.__selection_sets.pop(selection_set_id)
        else:
            selection_diff = [s for s in self.__selection_sets[selection_set_id] if s not in new_selection_set]
            self.__selection_sets[selection_set_id] = new_selection_set

        self.dispatch(self.__SELECTION_SET_REMOVED, sender=self, selection_set_id=selection_set_id, selection_diff=selection_set)
        return selection_diff

    def remove_all_selection_sets(self):
        """
        Deletes all selection sets of this data holder.

        :return: All removed sets and there ids.
        :rtype: dict[str, list]
        """
        selection_diffs = {}
        selection_ids = self.__selection_sets.keys()
        for selection_id in selection_ids:
            selection_diffs[selection_id] = self.__selection_sets[selection_id]

        self.__selection_sets.clear()
        for selection_set_id, selection_set in selection_diffs.iteritems():
            self.dispatch(self.__SELECTION_SET_REMOVED, sender=self, selection_set_id=selection_set_id, selection_diff=selection_set)
        return selection_diffs

    @staticmethod
    def __make_list_distinct(l):
        new_l = []
        for x in l:
            if x not in new_l:
                new_l.append(x)

        return new_l

    def start_listening(self, selection_set_added=None, selection_set_removed=None):
        """
        Registers a callback to listen to changes to this selection data holder. Listeners can register to any number of the provided
        events. For the required structure of the callbacks see below.

        :param selection_set_added: Called when a selection set was added.
        :type selection_set_added: function(sender:SelectionDataHolder, selection_set_id:str, selection_diff:list]
        :param selection_set_removed: Called when a selection set was removed.
        :type selection_set_added: function(sender:SelectionDataHolder, selection_set_id:str, selection_diff:list]
        """
        self.bind(self.__SELECTION_SET_ADDED, selection_set_added)
        self.bind(self.__SELECTION_SET_REMOVED, selection_set_removed)

    def stop_listening(self, selection_set_added=None,  selection_set_removed=None):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.

        :param selection_set_added: Called when a selection set was added.
        :type selection_set_added: function(sender:SelectionDataHolder, selection_set_id:str, selection_diff:list]
        :param selection_set_removed: Called when a selection set was removed.
        :type selection_set_added: function(sender:SelectionDataHolder, selection_set_id:str, selection_diff:list]
        """
        self.unbind(self.__SELECTION_SET_ADDED, selection_set_added)
        self.unbind(self.__SELECTION_SET_REMOVED, selection_set_removed)
