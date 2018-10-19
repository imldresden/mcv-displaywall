import json
from collections import OrderedDict


class StudyHandler(object):
    def __init__(self, study_order_file, block_question_file, session_id):
        """

        :param study_order_file: The path to the file with all study orders.
        :type study_order_file: str
        :param block_question_file: The path to the file with all the block questions.
        :type block_question_file: str
        :param session_id: The session this study handler should start.
        :type session_id: int
        """
        with open(study_order_file, 'rb') as sof, open(block_question_file, 'rb') as bqf:
            self.__study_order = json.load(sof)
            self.__tasks = json.load(bqf)

        self.__session_id = unicode(session_id)
        self.__current_phase_name = ""
        self.__current_block_name = ""
        self.__block_counter = 0

        # key -> block name     value -> list of tasks
        self.__block_mapper = OrderedDict()
        self.__phase_order = [
            "Training " + self.__study_order[self.__session_id]['Training'][0],
            "Training " + self.__study_order[self.__session_id]['Training'][1],
            "Guided Exploration",
            "Free Exploration"
        ]
        self.go_to_phase(self.__phase_order[0])

    @property
    def active_session(self):
        """
        :return: The active study nr. -1 if no study is active.
        :rtype: int
        """
        return int(self.__session_id)

    @property
    def phases(self):
        """
        :rtype: list[str]
        """
        return self.__phase_order

    @property
    def current_phase(self):
        """
        :rtype: str
        """
        return self.__current_phase_name

    @property
    def current_block_name(self):
        """
        :rtype: str
        """
        return self.__current_block_name

    @property
    def current_tasks(self):
        """
        :rtype: list[str]
        """
        return self.__block_mapper[self.__current_block_name]

    def go_to_phase(self, phase_name):
        """
        Go to the phase with the given name. If no phase with this name was found the phase will not be changed.

        :param phase_name: The name of the phase to change to.
        :type phase_name: str
        """
        if phase_name not in self.__phase_order:
            return

        self.__current_phase_name = phase_name

        self.__block_mapper.clear()
        if "Training" in phase_name:
            self.__block_mapper = OrderedDict(sorted([(k, v) for k, v in self.__tasks["Training"].iteritems()], key=lambda val: val[0]))
        else:
            for index in self.__study_order[self.__session_id][phase_name]:
                name = ("Block " if "Guided" in phase_name else "Thesis ") + index
                self.__block_mapper[name] = self.__tasks[phase_name][index]

        self.__block_counter = 0
        self.__current_block_name = self.__block_mapper.keys()[0]

    def go_to_neighbor_block(self, direction):
        """
        Go to the next or previous block. If there is no block the block will be the same as before.

        :param direction: In which direction should be change take place. -1 for previous, 1 for next.
        :type direction: int
        """
        if not 0 <= self.__block_counter + direction < len(self.__block_mapper):
            return

        self.__block_counter += direction
        self.__current_block_name = self.__block_mapper.keys()[self.__block_counter]
