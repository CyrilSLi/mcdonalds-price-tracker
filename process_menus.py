#!/usr/bin/env python3

# Built-in modules
import csv, json, os, sys
from itertools import zip_longest



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



def main(location):
    l10n_strings = {
        "en-CA": [],
        "fr-CA": []
    }

    restaurant_ids = os.listdir(relpath("menus_json"))
    for restaurant_id in restaurant_ids:
        with open(relpath("menus_json/" + restaurant_id)) as f:
            menu = json.load(f)
            for lang in l10n_strings.keys():
                l10n_strings[lang].append(tuple(map(str.strip, menu["channelMenus"]["localizations"][lang]["strings"])))

    mismatches = 0
    for lang, strings in l10n_strings.items():
        for item in zip_longest(*strings):
            if len(set(item)) > 1:
                print(f"Mismatch in {lang}: {item}")
                mismatches += 1

    print("Total localization mismatches among restaurants:", mismatches)
    if mismatches != 0:
        print(restaurant_ids)
        return

    for lang in l10n_strings.keys():
        l10n_strings[lang] = l10n_strings[lang][0]

    with open(relpath(f"data/{location}/localization.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(l10n_strings.keys())
        writer.writerows(zip_longest(*l10n_strings.values(), fillvalue=""))

    for lang in l10n_strings.keys():
        all_prices = {}

        for restaurant_id in sorted((int(fn.rstrip(".json")) for fn in os.listdir(relpath("menus_json")))):
            with open(relpath(f"menus_json/{restaurant_id}.json")) as f:
                menu = json.load(f)
        
            lookup = menu["channelMenus"]["localizations"][lang]["lookup"]
            prices = [""] * len(l10n_strings[lang])

            for item in menu_items(menu): # Get localization index for each menu item
                prices[lookup[str(item["ID"])][2]] = str(item["price"])

            all_prices[restaurant_id] = prices
        assert all(len(prices) == len(l10n_strings[lang]) for prices in all_prices.values())

        items_offered = [] # Items which at least one restaurant offers, to display as table column headers
        for item in zip(*all_prices.values()):
            items_offered.append("Y" if any(price != "" for price in item) else "")

        with open(relpath(f"data/{location}/prices_{lang}.csv"), "w") as f:
            writer = csv.writer(f)
            writer.writerow(("any", *all_prices.keys()))
            writer.writerows(zip(items_offered, *all_prices.values()))

    print("Localization and prices files generated successfully.")



if __name__ == "__main__":
    main(sys.argv[1])