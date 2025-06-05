import requests
import json
import xml.etree.ElementTree as ET # For XML parsing

BASE_URL = "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"

# Assumption: The API key is passed via the 'DB-Api-Key' header.
# An alternative is 'Authorization: Bearer <api_key>', which might be needed if this fails.
API_KEY_HEADER_NAME = "DB-Api-Key"

def find_station_eva_no(station_name: str, api_key: str) -> str | None:
    """
    Finds the EVA number for a given station name using the DB Timetables API.

    Args:
        station_name: The name of the station (e.g., "Berlin Hbf").
        api_key: The API key for authentication.

    Returns:
        The station's EVA number if found, otherwise None.
    """
    url = f"{BASE_URL}/station/{station_name}"
    headers = {
        API_KEY_HEADER_NAME: api_key,
        "Accept": "application/json, application/xml;q=0.9, */*;q=0.8" # Prefer JSON, accept XML
    }

    print(f"Attempting to find EVA number for '{station_name}' at URL: {url}")

    try:
        response = requests.get(url, headers=headers)
        print(f"Response status code: {response.status_code}")
        # print(f"Response headers: {response.headers}") # For debugging content type
        # print(f"Response text (first 500 chars): {response.text[:500]}") # For debugging raw response

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "").lower()

            # Print a snippet of the raw response
            print("\n--- Raw Response Snippet (find_station_eva_no) ---")
            print(response.text[:1000]) # Print first 1000 characters
            print("--- End Raw Response Snippet ---\n")

            eva_no = None

            if "application/json" in content_type:
                try:
                    data = response.json()
                    # Speculative parsing based on common structures:
                    # Assuming a list of stations, or a dictionary with a list.
                    if isinstance(data, list) and data:
                        station_data = data[0] # Take the first result
                    elif isinstance(data, dict) and "stations" in data and data["stations"]:
                        station_data = data["stations"][0]
                    elif isinstance(data, dict) and "station" in data: # e.g. if the URL directly returns THE station
                        station_data = data["station"]
                    elif isinstance(data, dict): # if the response itself is the station object
                         station_data = data
                    else:
                        station_data = None

                    if station_data:
                        if "evaNo" in station_data:
                            eva_no = station_data["evaNo"]
                        elif "number" in station_data: # Alternative key
                            eva_no = station_data["number"]
                        elif "id" in station_data: # Another alternative
                            eva_no = station_data["id"]
                        # Add more checks if other key names are discovered

                    if eva_no:
                         print(f"Parsed EVA number from JSON: {eva_no}")
                         return str(eva_no)
                    else:
                        print("Could not find 'evaNo', 'number', or 'id' in JSON response.")

                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON response: {e}")
                    # Fallback to XML if JSON decoding fails or if content type was ambiguous
                    if "application/xml" not in content_type: # only try XML if not already indicated as JSON
                        print("Attempting to parse as XML since JSON failed or content type was not explicit JSON.")
                        pass # Fall through to XML parsing
                    else: # If it was application/json and failed, then it's an error.
                        return None

            # XML Parsing (if content type indicated XML or JSON parsing failed)
            # This will be attempted if content_type is XML or if JSON parsing failed.
            if eva_no is None and ("application/xml" in content_type or "text/xml" in content_type or (not content_type and response.text.strip().startswith("<"))):
                print("Attempting to parse response as XML...")
                try:
                    root = ET.fromstring(response.text)
                    # Speculative XML parsing:
                    # Common structure: <stations><station evaNo="12345"></station></stations>
                    # Or: <station evaNo="12345"></station>
                    # Find the first 'station' element and get its 'evaNo' attribute.
                    station_element = root.find(".//station") # Finds first 'station' at any depth
                    if station_element is not None:
                        if "evaNo" in station_element.attrib:
                            eva_no = station_element.attrib["evaNo"]
                        elif "number" in station_element.attrib: # Alternative attribute
                            eva_no = station_element.attrib["number"]
                        elif "id" in station_element.attrib: # Another alternative
                            eva_no = station_element.attrib["id"]

                        if eva_no:
                            print(f"Parsed EVA number from XML: {eva_no}")
                            return str(eva_no)
                        else:
                            print("Could not find 'evaNo', 'number', or 'id' attribute in XML <station> element.")
                    else:
                        print("No <station> element found in XML response.")
                except ET.ParseError as e:
                    print(f"Failed to parse XML response: {e}")
                    return None

            if eva_no is None:
                 print(f"Could not determine EVA number for '{station_name}' from the response.")
                 return None

        else:
            print(f"Error finding station: HTTP {response.status_code}")
            print(f"Response content: {response.text[:500]}") # Print some of the error response
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed for {station_name}: {e}")
        return None


def get_station_plan(eva_no: str, date_str: str, hour_str: str, api_key: str) -> list | None:
    """
    Gets the station plan (timetable/departures) for a given EVA number, date, and hour.

    Args:
        eva_no: The EVA number of the station.
        date_str: The date in YYYY-MM-DD format (e.g., "2024-03-15").
        hour_str: The hour in HH format (e.g., "09" for 9 AM).
        api_key: The API key for authentication.

    Returns:
        A list of train events/departures if found, otherwise None.
    """
    # The API documentation uses date and hour without hyphens or colons for path parameters.
    # Example: /plan/8011160/240314/10 (for 2024-03-14, 10:00)
    # We'll adapt our date_str and hour_str accordingly.
    formatted_date = date_str.replace("-", "")[2:] # YYMMDD
    formatted_hour = hour_str # HH

    url = f"{BASE_URL}/plan/{eva_no}/{formatted_date}/{formatted_hour}"
    headers = {
        API_KEY_HEADER_NAME: api_key,
        "Accept": "application/json, application/xml;q=0.9, */*;q=0.8"
    }

    print(f"Attempting to get station plan for EVA '{eva_no}' on {date_str} at {hour_str}h. URL: {url}")

    try:
        response = requests.get(url, headers=headers)
        print(f"Response status code: {response.status_code}")
        # print(f"Response text (first 500 chars): {response.text[:500]}")

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "").lower()

            print("\n--- Raw Response Snippet (get_station_plan) ---")
            print(response.text[:2000]) # Print first 2000 characters
            print("--- End Raw Response Snippet ---\n")

            departures = None

            if "application/json" in content_type:
                try:
                    data = response.json()
                    # Speculative parsing:
                    # Assuming a list of events/departures directly, or within a key like "timetable" or "departures".
                    if isinstance(data, list):
                        departures = data
                    elif isinstance(data, dict):
                        if "timetable" in data and isinstance(data["timetable"], list):
                            departures = data["timetable"]
                        elif "departures" in data and isinstance(data["departures"], list):
                            departures = data["departures"]
                        elif "plan" in data and isinstance(data["plan"], list): # Another common term
                            departures = data["plan"]
                        # Add more checks based on actual response structure.

                    if departures is not None: # Check if departures is not None before printing
                        print(f"Parsed {len(departures)} departures from JSON.")
                        return departures
                    else:
                        print("Could not find a list of departures in JSON response under expected keys.")

                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON response: {e}")
                    if "application/xml" not in content_type:
                         print("Attempting to parse as XML since JSON failed or content type was not explicit JSON.")
                         pass # Fall through
                    else:
                        return None


            if departures is None and ("application/xml" in content_type or "text/xml" in content_type or (not content_type and response.text.strip().startswith("<"))):
                print("Attempting to parse response as XML...")
                try:
                    root = ET.fromstring(response.text)
                    # Speculative XML: <timetable><event>...</event><event>...</event></timetable>
                    # Or <plan><departure>...</departure></plan>
                    # We'll look for repeating elements like 'event', 'departure', 'stop' etc.
                    event_elements = root.findall(".//event") # Common tag
                    if not event_elements:
                        event_elements = root.findall(".//departure")
                    if not event_elements:
                        event_elements = root.findall(".//stop") # In some HAFAS XML this is used.

                    if event_elements:
                        # For simplicity, returning a list of dictionaries representing elements
                        departures = []
                        for elem in event_elements:
                            # Extract some basic info, this needs heavy adjustment based on actual XML structure
                            event_data = {"tag": elem.tag, "attributes": elem.attrib}
                            # Try to get some common sub-elements or text
                            train_name_elem = elem.find(".//train/name") # Example path
                            if train_name_elem is not None:
                                event_data["train_name"] = train_name_elem.text
                            departure_time_elem = elem.find(".//time") # Example path
                            if departure_time_elem is not None :
                                event_data["time"] = departure_time_elem.text
                            departures.append(event_data)

                        print(f"Parsed {len(departures)} events/departures from XML.")
                        return departures
                    else:
                        print("No common departure-like elements ('event', 'departure', 'stop') found in XML.")
                except ET.ParseError as e:
                    print(f"Failed to parse XML response: {e}")
                    return None

            if departures is None:
                print("Could not parse departures from the response.")
                return None

        else:
            print(f"Error getting station plan: HTTP {response.status_code}")
            print(f"Response content: {response.text[:500]}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed for station plan (EVA: {eva_no}): {e}")
        return None

if __name__ == "__main__":
    # IMPORTANT: Replace "YOUR_DB_API_KEY_HERE" with your actual Deutsche Bahn API key.
    # Without a valid key, these tests will fail (likely with 401 Unauthorized).
    TEST_API_KEY = "YOUR_DB_API_KEY_HERE"

    print("--- Testing find_station_eva_no ---")
    # Check if the API key has been replaced
    if TEST_API_KEY == "YOUR_DB_API_KEY_HERE":
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! PLEASE REPLACE 'YOUR_DB_API_KEY_HERE' with your actual DB API key      !!!")
        print("!!! in the script before running. Otherwise, API calls will fail.          !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

    station_name_to_test = "Berlin Hbf"
    eva_no = find_station_eva_no(station_name_to_test, TEST_API_KEY)

    if eva_no:
        print(f"\nSuccessfully found EVA number for '{station_name_to_test}': {eva_no}")

        print("\n--- Testing get_station_plan ---")
        # Get tomorrow's date for testing
        import datetime
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        date_to_test = tomorrow.strftime("%Y-%m-%d") # YYYY-MM-DD
        hour_to_test = "10" # 10 AM (HH format)

        plan = get_station_plan(eva_no, date_to_test, hour_to_test, TEST_API_KEY)

        if plan:
            print(f"\nSuccessfully retrieved station plan for EVA {eva_no} on {date_to_test} at {hour_to_test}:00.")
            print(f"Found {len(plan)} entries.")
            # Print details of the first few entries as an example
            for i, entry in enumerate(plan[:3]): # Print first 3 entries
                print(f"\nEntry {i+1}:")
                # This part is highly speculative as we don't know the structure.
                # We'll just dump the entry.
                if isinstance(entry, dict):
                    for key, value in entry.items():
                        print(f"  {key}: {value}")
                else: # If it's not a dict (e.g. string from basic XML parsing)
                    print(f"  {entry}")
        else:
            print(f"\nCould not retrieve station plan for EVA {eva_no} on {date_to_test} at {hour_to_test}:00.")
    else:
        print(f"\nCould not find EVA number for '{station_name_to_test}'. Cannot test get_station_plan.")

    print("\n--- Assumptions Made ---")
    print(f"1. API Key Header: Used '{API_KEY_HEADER_NAME}: <api_key>'. If this fails, 'Authorization: Bearer <api_key>' might be needed.")
    print("2. Station Lookup URL: Assumed '/station/{station_name}'. The API might use '/station?name={station_name}' or similar.")
    print("3. Station Lookup Response: Attempted to parse as JSON first, then XML. Speculated on common keys like 'evaNo', 'number', 'id'.")
    print("4. Timetable URL: Assumed '/plan/{eva_no}/{YYMMDD}/{HH}'. Date/hour format might differ.")
    print("5. Timetable Response: Attempted to parse as JSON first, then XML. Speculated on list structures or keys like 'timetable', 'departures', 'plan' for JSON, and elements like 'event', 'departure', 'stop' for XML.")
    print("6. XML parsing is very basic and tries to find common element names. Real XML structure will require more specific parsing logic.")
    print("--- End of Script ---")
