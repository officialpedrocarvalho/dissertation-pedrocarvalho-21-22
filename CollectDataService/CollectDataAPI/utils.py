def split_by_character_in_position(string, character, position):
    string = string.split(character)
    return character.join(string[:position]) + character


def get_subsequences(main_sequence, length):
    """Returns the sub-sequences of the given length as tuples"""
    sequence = main_sequence[0:length]
    yield tuple(sequence)
    while length < len(main_sequence):
        sequence.pop(0)
        sequence.append(main_sequence[length])
        length += 1
        yield tuple(sequence)


def get_subsequences_gte(main_sequence, min_length):
    """Returns all sub-sequences >= the given length"""
    while min_length <= len(main_sequence):
        for subsequence in get_subsequences(main_sequence, min_length):
            yield subsequence
        min_length += 1
