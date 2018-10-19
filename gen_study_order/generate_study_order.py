import json
from random import shuffle

import itertools

import math


def generate_study_order(file_path, nr_studies, nr_blocks, nr_thesis):
    # # latin squares III (3241-4320)
    # # http://www.math.montana.edu/jobo/st541/sec3c.pdf
    # possible_block_orders = [
    #     ["1", "2", "3", "4", "5", "6"],
    #     ["2", "1", "6", "5", "3", "4"],
    #     ["3", "6", "2", "1", "4", "5"],
    #     ["4", "3", "5", "2", "6", "1"],
    #     ["5", "4", "1", "6", "2", "3"],
    #     ["6", "5", "4", "3", "1", "2"]
    # ]

    # # latin square 7x7
    # # http://statpages.info/latinsq.html
    # possible_block_orders = [
    #     ["1", "2", "7", "3", "6", "4", "5"],
    #     ["2", "3", "1", "4", "7", "5", "6"],
    #     ["3", "4", "2", "5", "1", "6", "7"],
    #     ["4", "5", "3", "6", "2", "7", "1"],
    #     ["5", "6", "4", "7", "3", "1", "2"],
    #     ["6", "7", "5", "1", "4", "2", "3"],
    #     ["7", "1", "6", "2", "5", "3", "4"],
    #     ["5", "4", "6", "3", "7", "2", "1"],
    #     ["6", "5", "7", "4", "1", "3", "2"],
    #     ["7", "6", "1", "5", "2", "4", "3"],
    #     ["1", "7", "2", "6", "3", "5", "4"],
    #     ["2", "1", "3", "7", "4", "6", "5"],
    #     ["3", "2", "4", "1", "5", "7", "6"],
    #     ["4", "3", "5", "2", "6", "1", "7"]
    # ]

    # latin square 6x6
    # http://statpages.info/latinsq.html
    possible_block_orders = [
        ["1", "2", "6", "3", "5", "4"],
        ["2", "3", "1", "4", "6", "5"],
        ["3", "4", "2", "5", "1", "6"],
        ["4", "5", "3", "6", "2", "1"],
        ["5", "6", "4", "1", "3", "2"],
        ["6", "1", "5", "2", "4", "3"]
    ]

    if len(possible_block_orders) < nr_studies / 2:
        add_count = math.ceil((float(nr_studies) / 2 - len(possible_block_orders)) / len(possible_block_orders))
        new_list = possible_block_orders[:]
        for _ in range(int(add_count)):
            new_list.extend(possible_block_orders)
        possible_block_orders = new_list
    # shuffle(possible_block_orders)
    possible_block_orders = possible_block_orders[:nr_studies / 2]

    possible_thesis_order = list(itertools.permutations([str(i) for i in range(1, nr_thesis + 1)]))
    if len(possible_thesis_order) < nr_studies / 2:
        add_count = math.ceil((float(nr_studies) / 2 - len(possible_thesis_order)) / len(possible_thesis_order))
        new_list = possible_thesis_order[:]
        for _ in range(int(add_count)):
            new_list.extend(possible_thesis_order)
        possible_thesis_order = new_list
    shuffle(possible_thesis_order)
    possible_thesis_order = possible_thesis_order[:nr_studies / 2]

    study_orders = {}
    # Go through all possible studies.
    for i in range(nr_studies):
        study = {}
        # Save the training order.
        study['Training'] = ['Touch', 'Pointing'] if i % 2 == 0 else ['Pointing', 'Touch']
        # Save the explorations.
        study['Guided Exploration'] = possible_block_orders[i / 2]
        study['Free Exploration'] = possible_thesis_order[i / 2]

        study_orders[i] = study

    with open(file_path, 'wb') as f:
        json.dump(study_orders, f)


if __name__ == "__main__":
    nr_studies = 24
    nr_blocks = 6
    nr_thesis = 4

    generate_study_order("study_order.json", nr_studies, nr_blocks, nr_thesis)
