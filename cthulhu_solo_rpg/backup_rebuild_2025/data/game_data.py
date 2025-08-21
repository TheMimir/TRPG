"""
Game Data definitions and constants

Contains game rules, tables, and reference data.
"""

# Cthulhu TRPG Skills
DEFAULT_SKILLS = {
    'accounting': 10,
    'anthropology': 1,
    'appraise': 5,
    'archaeology': 1,
    'art_craft': 5,
    'charm': 15,
    'climb': 40,
    'computer_use': 20,
    'credit_rating': 15,
    'cthulhu_mythos': 0,
    'disguise': 1,
    'dodge': 30,
    'drive_auto': 20,
    'electrical_repair': 10,
    'fast_talk': 5,
    'first_aid': 30,
    'history': 20,
    'intimidate': 15,
    'jump': 25,
    'language_own': 80,
    'law': 5,
    'library_use': 25,
    'listen': 25,
    'locksmith': 1,
    'mechanical_repair': 20,
    'medicine': 5,
    'natural_world': 10,
    'navigate': 10,
    'occult': 5,
    'operate_heavy_machinery': 1,
    'persuade': 15,
    'pilot': 1,
    'psychology': 5,
    'psychoanalysis': 1,
    'ride': 5,
    'science': 1,
    'sleight_of_hand': 10,
    'spot_hidden': 25,
    'stealth': 10,
    'survival': 10,
    'swim': 25,
    'throw': 25,
    'track': 10
}

# Sanity loss tables
SANITY_LOSS_TABLE = {
    'minor_horror': (0, 1),
    'moderate_horror': (1, 4),
    'major_horror': (1, 8),
    'extreme_horror': (1, 10),
    'mythos_entity': (1, 20)
}

# Difficulty modifiers
DIFFICULTY_MODIFIERS = {
    'automatic': 999,
    'trivial': 40,
    'easy': 20,
    'regular': 0,
    'hard': -20,
    'extreme': -40,
    'impossible': -999
}