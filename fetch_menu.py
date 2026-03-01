#!/usr/bin/env python3

# Built-in modules
import json, sys, uuid
from datetime import datetime
from os import path

# Third-party modules
import requests as r



def relpath(p):
    try:
        return path.join(path.dirname(__file__), p)
    except NameError:
        return p



with open(relpath("env.json")) as f:
    env = json.load(f)
with open(relpath("login_refresh_response.json")) as f:
    bearer = json.load(f)["response"]["accessToken"]



def mcd_headers():
    global bearer
    return dict(env["headers"], **{
        "Authorization": "Bearer " + bearer,
        "mcd-uuid": str(uuid.uuid4()).upper()
    })



def refresh_login():
    global bearer
    with open(relpath("login_refresh_response.json")) as f:
        old_resp = json.load(f)
        bearer = old_resp["response"]["accessToken"]

    res = r.post(
        "https://us-prod.api.mcd.com/exp/v1/customer/login/refresh",
        headers=mcd_headers(),
        json={
            "refreshToken": old_resp["response"]["refreshToken"]
        }
    )

    res.raise_for_status()
    res = res.json()
    bearer = res["response"]["accessToken"]
    with open(relpath("login_refresh_response.json"), "w") as f:
        json.dump(res, f, indent=4)



def fetch_menu(location_id, is_retry=False):
    res = r.get(
        f"https://us-prod.api.mcd.com/ca/gma/api/v1/restaurants/{location_id}/menus",
        headers=mcd_headers()
    )

    try:
        res.raise_for_status()
    except r.exceptions.HTTPError as e:
        if not is_retry and res.status_code == 401:
            print("Unauthorized, refreshing login...")
            refresh_login()
            return fetch_menu(location_id, is_retry=True)
        else:
            raise e

    with open(relpath(f"menus_json/{location_id}.json"), "w") as f:
        json.dump(res.json(), f, indent=1)

    res = r.get(
        f"https://us-prod.api.mcd.com/exp/v1/restaurant/{location_id}?filter=full&storeUniqueIdType=NSN",
        headers=mcd_headers()
    )

    res.raise_for_status()
    with open(relpath("addresses.json")) as f:
        addresses = json.load(f)
    addresses[location_id] = {
        "addr": res.json()["response"]["restaurant"]["address"]["addressLine1"].strip(),
        "updated": datetime.now().strftime("%Y-%m-%d")
    }
    with open(relpath("addresses.json"), "w") as f:
        # Sort integer keys numerically first, then string keys alphabetically
        sorted_dict = {k: addresses[k] for k in sorted(addresses.keys(), key=lambda x: (False, int(x)) if x.isdigit() else (True, x))}
        json.dump(sorted_dict, f, indent=1)



if __name__ == "__main__":
    fetch_menu(sys.argv[1])