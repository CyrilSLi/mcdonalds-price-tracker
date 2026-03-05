#!/usr/bin/env python3

# Built-in modules
import csv, json, os, sys
from datetime import datetime
from itertools import zip_longest
from pathlib import Path



def relpath(p):
    try:
        return path.join(path.dirname(__file__), p)
    except NameError:
        return p



def menu_items(json_input):
    if isinstance(json_input, dict):
        if "ID" in json_input and "price" in json_input:
            yield json_input # Menu item (e.g. hamburger)

        elif "ID" in json_input and json_input.get("type") == "QUANTITY" and "options" in json_input:
            for qty in json_input["options"]:
                if isinstance(qty, list) and qty[0] != 0:
                    yield {"ID": json_input["ID"], "price": qty[0]} # Add-on (e.g. lettuce)
                    break

        else:
            for item in json_input.values():
                yield from menu_items(item)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from menu_items(item)



def main(location, log_mismatches=True, check_menus_in_root_dir=True):
    l10n_strings = {
        "en-CA": [],
        "fr-CA": []
    }
    menu_files = None

    if check_menus_in_root_dir:
        menu_files = tuple (i for i in os.listdir(relpath("menus_json")) if i.endswith(".json"))
    if not (menu_files and check_menus_in_root_dir):
        menu_files = tuple (f"{location}/{i}" for i in os.listdir(relpath(f"menus_json/{location}")) if i.endswith(".json"))
        if not menu_files:
            print("No menu files found for location:", location)
            return

    for menu_file in menu_files:
        with open(relpath("menus_json/" + menu_file)) as f:
            menu = json.load(f)
            for lang in l10n_strings.keys():
                l10n_strings[lang].append(tuple(map(str.strip, menu["channelMenus"]["localizations"][lang]["strings"])))

    mismatches = 0
    for lang, strings in l10n_strings.items():
        for item in zip_longest(*strings):
            if len(set(item)) > 1:
                if log_mismatches:
                    print(f"Mismatch in {lang}: {item}")
                mismatches += 1

    print("Total localization mismatches among restaurants:", mismatches)
    if mismatches != 0:
        if log_mismatches:
            print(menu_files)
        return

    for lang in l10n_strings.keys():
        l10n_strings[lang] = l10n_strings[lang][0]

    if not os.path.exists(relpath(f"data/{location}")):
        os.makedirs(relpath(f"data/{location}"))

    with open(relpath(f"data/{location}/localization.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(l10n_strings.keys())
        writer.writerows(zip_longest(*l10n_strings.values(), fillvalue=""))

    for lang in l10n_strings.keys():
        all_prices = {}
        item_count, diff_price_count = 0, 0

        for menu_file in sorted(menu_files, key=lambda x: int(Path(x).stem)):
            with open(relpath("menus_json/" + menu_file)) as f:
                menu = json.load(f)
        
            lookup = menu["channelMenus"]["localizations"][lang]["lookup"]
            prices = [""] * len(l10n_strings[lang])

            for item in menu_items(menu["channelMenus"]["channels"]["GMA_PICKUP"]): # TODO: Add support for DELIVERY and EATIN channels
                localized = lookup[str(item["ID"])][2] # Get localization index for each menu item

                if prices[localized] not in ("", str(item["price"])): # Add-on with different prices depending on the main item
                    prices[localized] = "/".join(sorted(set(prices[localized].split("/") + [str(item["price"])]), key=int))
                    diff_price_count += 1
                else:
                    prices[localized] = str(item["price"])
                item_count += 1

            all_prices[Path(menu_file).stem] = prices
        assert all(len(prices) == len(l10n_strings[lang]) for prices in all_prices.values())
        print(f"{lang}: {item_count} items processed across {len(menu_files)} restaurants, {diff_price_count} items have different prices depending on the main item.")

        items_offered = [] # Items which at least one restaurant offers, to display as table column headers
        for item in zip(*all_prices.values()):
            items_offered.append("Y" if any(price != "" for price in item) else "")

        with open(relpath(f"data/{location}/prices_{lang}.csv"), "w") as f:
            writer = csv.writer(f)
            writer.writerow(("any", *all_prices.keys()))
            writer.writerows(zip(items_offered, *all_prices.values()))

    print("Localization and prices files generated successfully.")

    with open(relpath("addresses.json")) as f:
        addresses = json.load(f)
    addresses.setdefault("__locations__", {})[location] = {
        "updated": datetime.now().strftime("%Y-%m-%d")
    }
    addresses["__locations__"] = dict(sorted(addresses["__locations__"].items(), key=lambda x: x[0]))

    with open(relpath("addresses.json"), "w") as f:
        # Sort integer keys numerically first, then string keys alphabetically
        sorted_dict = {k: addresses[k] for k in sorted(addresses.keys(), key=lambda x: (False, int(x)) if x.isdigit() else (True, x))}
        json.dump(sorted_dict, f, indent=1)
    print(f"Location '{location}' added to addresses.json.")



if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1].title())
    else:
        locations = tuple (i for i in os.listdir(relpath("menus_json")) if os.path.isdir(relpath("menus_json/" + i)))
        for i, location in enumerate(locations, 1):
            print(f"Processing menus for {location} ({i}/{len(locations)})...")
            main(location, log_mismatches=False)