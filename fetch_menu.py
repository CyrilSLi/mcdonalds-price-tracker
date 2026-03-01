#!/usr/bin/env python3

# Built-in modules
import json, sys
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



def refresh_login():
    global bearer
    with open(relpath("login_refresh_response.json")) as f:
        old_resp = json.load(f)

    res = r.post(
        "https://us-prod.api.mcd.com/exp/v1/customer/login/refresh",
        headers=dict(
            env["headers"]["customer_login_refresh"],
            Authorization="Bearer " + old_resp["response"]["accessToken"]
        ),
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
        headers=dict(
            env["headers"]["restaurants_menus"],
            Authorization="Bearer " + bearer
        )
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
        json.dump(res.json(), f, indent=4)



if __name__ == "__main__":
    fetch_menu(sys.argv[1])