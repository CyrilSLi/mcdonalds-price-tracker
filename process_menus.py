#!/usr/bin/env python3

# Built-in modules
from itertools import zip_longest
import json, os



def relpath(p):
    try:
        return path.join(path.dirname(__file__), p)
    except NameError:
        return p



def menu_items(json_input):
    if isinstance(json_input, dict):
        if "ID" in json_input and "price" in json_input and isinstance(json_input["ID"], int) and isinstance(json_input["price"], int):
            yield json_input
        else:
            for item in json_input.values():
                yield from menu_items(item)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from menu_items(item)



def main():
    l10n_strings = {
        "en-CA": [],
        "fr-CA": []
    }

    for restaurant_id in os.listdir(relpath("menus_json")):
        with open(relpath("menus_json/" + restaurant_id)) as f:
            menu = json.load(f)
            strings = lambda lang: menu["channelMenus"]["localizations"][lang]["strings"]
            l10n_strings["en-CA"].append(strings("en-CA"))
            l10n_strings["fr-CA"].append(strings("fr-CA"))

    mismatches = 0
    for lang, strings in l10n_strings.items():
        for item in zip_longest(*strings):
            if len(set(item)) > 1:
                print(f"Mismatch in {lang}: {item}")
                mismatches += 1

    print("Total localization mismatches among restaurants:", mismatches)
    if mismatches != 0:
        return

    l10n_strings["en-CA"] = l10n_strings["en-CA"][0]
    l10n_strings["fr-CA"] = l10n_strings["fr-CA"][0]

    with open(relpath("localization_en-CA.txt"), "w") as f:
        f.write("\n".join(l10n_strings["en-CA"]))
    with open(relpath("localization_fr-CA.txt"), "w") as f:
        f.write("\n".join(l10n_strings["fr-CA"]))

    for menu_file in os.listdir(relpath("menus_json")):
        with open(relpath("menus_json/" + menu_file)) as f:
            menu = json.load(f)

        for lang in ("en-CA", "fr-CA"):
            lookup = menu["channelMenus"]["localizations"][lang]["lookup"]
            prices = [""] * len(l10n_strings[lang])

            for item in menu_items(menu): # Get localization index for each menu item
                prices[lookup[str(item["ID"])][2]] = str(item["price"])

            with open(relpath(f'prices/{menu_file.rstrip(".json")}_{lang}.txt'), "w") as f:
                f.write("\n".join(prices))

    print("Localization and prices files generated successfully.")



if __name__ == "__main__":
    main()