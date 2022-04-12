def split_by_character_in_position(string, character, position):
    string = string.split(character)
    return character.join(string[:position]) + character
