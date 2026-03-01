# Built-in modules
import json
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



if __name__ == "__main__":
    # Example
    with open(relpath("menus_json/7094.json")) as f:
        print(list(menu_items(json.load(f))))