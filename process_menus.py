# Built-in modules
from itertools import zip_longest
import json, os

def relpath(p):
    try:
        return path.join(path.dirname(__file__), p)
    except NameError:
        return p



def main():
    en_CA_strings, fr_CA_strings = [], []
    for restaurant_id in os.listdir(relpath("menus_json")):
        with open(relpath("menus_json/" + restaurant_id)) as f:
            data = json.load(f)
            strings = lambda lang: data["channelMenus"]["localizations"][lang]["strings"]
            en_CA_strings.append(strings("en-CA"))
            fr_CA_strings.append(strings("fr-CA"))

    mismatches = 0
    for lang, strings in (("en_CA", en_CA_strings), ("fr_CA", fr_CA_strings)):
        for item in zip_longest(*strings):
            if len(set(item)) > 1:
                print(f"Mismatch in {lang}: {item}")
                mismatches += 1
    print("Total mismatches:", mismatches)

    if mismatches == 0:
        with open(relpath("localization_en-CA.txt"), "w") as f:
            f.write("\n".join(en_CA_strings[0]))
        with open(relpath("localization_fr-CA.txt"), "w") as f:
            f.write("\n".join(fr_CA_strings[0]))



if __name__ == "__main__":
    main()