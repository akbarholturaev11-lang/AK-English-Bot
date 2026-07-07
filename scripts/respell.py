# -*- coding: utf-8 -*-
"""Simple, learner-friendly English respellings (no IPA symbols).

Used to replace IPA in the pronunciation slot so learners see e.g.
"THANK-yoo" instead of "/ˈθæŋk juː/". Sentences get no respelling ("").
"""

RESPELL = {
    # L1
    "Hello": "huh-LOH", "Hi": "HY", "Good morning": "gud-MOR-ning", "Goodbye": "gud-BY",
    "Please": "PLEEZ", "Thank you": "THANK-yoo", "Sorry": "SOR-ee", "You're welcome": "yor-WEL-kum",
    # L2
    "name": "NAYM", "My name is": "MY-naym-iz", "What is your name?": "wots-yor-NAYM",
    "Nice to meet you": "nys-tu-MEET-yoo", "I am": "eye-AM", "you are": "yoo-AR",
    "this is": "THIS-iz", "friend": "FREND",
    # L3
    "one": "WUN", "two": "TOO", "three": "THREE", "four": "FOR", "five": "FYV", "ten": "TEN",
    "How old are you?": "how-OLD-ar-yoo", "years old": "YEERZ-old",
    # L4
    "family": "FAM-uh-lee", "mother": "MUH-thur", "father": "FAH-thur", "brother": "BRUH-thur",
    "sister": "SIS-tur", "he": "HEE", "she": "SHEE", "my": "MY",
    # L5
    "water": "WAW-tur", "tea": "TEE", "coffee": "KOF-ee", "food": "FOOD", "bread": "BRED",
    "eat": "EET", "drink": "DRINK", "I want": "eye-WONT",
    # L6
    "day": "DAY", "week": "WEEK", "today": "tu-DAY", "tomorrow": "tu-MOR-oh",
    "yesterday": "YES-tur-day", "Monday": "MUN-day", "weekend": "WEEK-end", "morning": "MOR-ning",
    # L7
    "color": "KUL-ur", "red": "RED", "blue": "BLOO", "green": "GREEN", "yellow": "YEL-oh",
    "black": "BLAK", "white": "WYT",
    # L8
    "go": "GOH", "come": "KUM", "see": "SEE", "read": "REED", "like": "LYK", "have": "HAV",
    "work": "WURK", "live": "LIV",
    # L9
    "home": "HOHM", "school": "SKOOL", "shop": "SHOP", "city": "SIT-ee", "here": "HEER",
    "there": "THAIR", "go to": "GOH-tu", "where": "WAIR",
    # L10
    "time": "TYM", "hour": "OWR", "now": "NOW", "early": "UR-lee", "late": "LAYT",
    "o'clock": "uh-KLOK", "What time": "wot-TYM", "minute": "MIN-it",
    # L11
    "weather": "WETH-ur", "hot": "HOT", "cold": "KOHLD", "warm": "WORM", "rain": "RAYN",
    "sunny": "SUN-ee", "wind": "WIND", "cloud": "KLOWD",
}


def respell(word):
    return RESPELL.get((word or "").strip(), "")
