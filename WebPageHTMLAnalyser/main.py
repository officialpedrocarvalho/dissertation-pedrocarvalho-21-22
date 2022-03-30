import codecs
import os
import sys

import sequence_comparison
import tree_edit_distance
from export import results_to_excel


def get_files(directory):
    result = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.split(".")[1] == "html":
                f = codecs.open(os.path.join(root, filename), 'r')
                result.append((f.read(), root, filename))
    return result


# def get_results(pages, offset, method):
#     fp = fn = tp = tn = 0
#     for i, first in enumerate(pages, start=1):
#         for j, second in enumerate(pages, start=1):
#             if j > i:
#                 result = method(first[0], second[0])
#                 if result >= offset and first[1] != second[1]:
#                     fp += 1
#                 elif result < offset and first[1] == second[1]:
#                     fn += 1
#                 elif result < offset and first[1] != second[1]:
#                     tn += 1
#                 elif result >= offset and first[1] == second[1]:
#                     tp += 1
#     return fp, fn, tp, tn


def get_results(pages, method):
    final_data = [0] * 21 * 4
    details = []
    for i, first in enumerate(pages, start=1):
        for j, second in enumerate(pages, start=1):
            if j > i:
                result = method(first[0], second[0])
                aux = 0
                offset = 0.0
                for offset_count in range(21):
                    # TP
                    if result >= offset and first[1] == second[1]:
                        final_data[aux + 0] += 1
                    # TN
                    elif result < offset and first[1] != second[1]:
                        final_data[aux + 1] += 1
                    # FP
                    elif result >= offset and first[1] != second[1]:
                        final_data[aux + 2] += 1
                        if offset >= 0.85:
                            details.append(("FP", offset, first[2], second[2]))
                    # FN
                    elif result < offset and first[1] == second[1]:
                        final_data[aux + 3] += 1
                        if 0.85 <= offset < 1:
                            details.append(("FN", offset, first[2], second[2]))
                    aux += 4
                    offset += 0.05
    return final_data, details


if __name__ == '__main__':
    arguments = sys.argv[1:]
    website = arguments[0]
    path = arguments[1]
    offset = float(arguments[2])
    files = get_files(path)
    final_data, details = get_results(files, sequence_comparison.similarity_rate)
    results_to_excel(final_data, details, 0, 0.05, 'LCS', website, len(files))
    final_data, details = get_results(files, tree_edit_distance.similarity_rate)
    results_to_excel(final_data, details, 0, 0.05, 'APTED', website, len(files))
    final_data, details = get_results(files, tree_edit_distance.similarity_rate_canonical)
    results_to_excel(final_data, details, 0, 0.05, 'X_APTED', website, len(files))
