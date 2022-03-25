import codecs
import os
import sys

import sequence_comparison
import tree_edit_distance


def get_files(directory):
    result = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.split(".")[1] == "html":
                f = codecs.open(os.path.join(root, filename), 'r')
                result.append((f.read(), root))
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


def get_results(pages, offset, method):
    final_data = [0] * 14 * 4
    for i, first in enumerate(pages, start=1):
        for j, second in enumerate(pages, start=1):
            if j > i:
                result = method(first[0], second[0])
                aux = 0
                offset = 0.35
                for offset_count in range(14):
                    # TP
                    if result >= offset and first[1] == second[1]:
                        final_data[aux + 0] += 1
                    # TN
                    elif result < offset and first[1] != second[1]:
                        final_data[aux + 1] += 1
                    # FP
                    elif result >= offset and first[1] != second[1]:
                        final_data[aux + 2] += 1
                    # FN
                    elif result < offset and first[1] == second[1]:
                        final_data[aux + 3] += 1
                    aux += 4
                    offset += 0.05
    return final_data


if __name__ == '__main__':
    arguments = sys.argv[1:]
    path = arguments[0]
    offset = float(arguments[1])
    files = get_files(path)
    # fp, fn, tp, tn = get_results(files, offset, sequence_comparison.similarity_rate)
    # print("False Positives: " + str(fp) + "\n", "False Negatives: " + str(fn) + "\n",
    #      "True Positives: " + str(tp) + "\n", "True Negatives: " + str(tn))
    final_data = get_results(files, offset, tree_edit_distance.similarity_rate)
    print(final_data)
    print("THE END")
    # fp, fn, tp, tn = get_results(files, offset, tree_edit_distance.similarity_rate)
    # print("False Positives: " + str(fp) + "\n", "False Negatives: " + str(fn) + "\n",
    #      "True Positives: " + str(tp) + "\n", "True Negatives: " + str(tn))
