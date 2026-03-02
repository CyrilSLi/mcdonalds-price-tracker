# McDonald's® Price Tracker

Compare the prices of McDonald's menu items across different restaurants in your location

# Setup

- Install the required dependencies: `pip install -r requirements.txt`
- Fill out `env.json` with API request headers according to `env.json.template`
- Save the response of the latest login refresh request to `login_refresh_response.json`

# Usage

- `./fetch_menu.py <restaurant_id>`: Fetch the menu for a specific restaurant and save it to `menu_jsons/<restaurant_id>.json`
- `./process_menus.py <location_name>`: Process all menu JSON files in `menu_jsons/` (non-recursively) and save the processed data to `data/<location_name>/`
  - `<location_name>` is an arbitrary string which will get converted to title case, typically representing a city or region name
  - If `menu_jsons/` doesn't contain any JSON files it will look in `menu_jsons/<location_name>/` instead
- Serve the project root directory with any static website hosting tool