from difflib import SequenceMatcher


def split_by_character_in_position(string, character, position):
    string = string.split(character)
    return character.join(string[:position]) + character


def matching_ratio(item_1, item_2):
    matcher = SequenceMatcher(None, item_1, item_2)
    matcher.get_matching_blocks()
    return matcher.ratio()


def matching_ratio_largest_sub_tree(item_1, item_2):
    matcher = SequenceMatcher(None, item_1, item_2)
    size_1 = len(item_1)
    size_2 = len(item_2)
    longest = matcher.find_longest_match(0, size_1, 0, size_2)
    return 2 * longest.size / (size_1 + size_2)


def matching_ratio_tree_distance(item_1, item_2):
    matcher = SequenceMatcher(None, item_1, item_2)
    codes = list(filter(lambda opt: opt[0] != 'equal', matcher.get_opcodes()))
    similarity = 1 - len(codes) / (len(item_1) + len(item_2))
    return similarity
