import requests

BASE_URL = "https://v6.db.transport.rest/"

def find_station_id(station_name: str) -> str | None:
    """
    Finds the station ID for a given station name.

    Args:
        station_name: The name of the station.

    Returns:
        The station ID if found, otherwise None.
    """
    try:
        response = requests.get(
            BASE_URL + "locations",
            params={"query": station_name, "results": 1, "language": "de"},
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        locations = response.json()
        if locations and isinstance(locations, list) and len(locations) > 0 and "id" in locations[0]:
            return locations[0]["id"]
        else:
            print(f"No station found for '{station_name}'.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error finding station ID for '{station_name}': {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Error parsing response for '{station_name}': {e}")
        return None

def find_journeys(from_id: str, to_id: str, departure_date: str) -> list | None:
    """
    Finds journeys between two stations for a given departure date.

    Args:
        from_id: The ID of the departure station.
        to_id: The ID of the arrival station.
        departure_date: The departure date in ISO 8601 format.

    Returns:
        A list of journeys if found, otherwise None.
    """
    try:
        response = requests.get(
            BASE_URL + "journeys",
            params={
                "from": from_id,
                "to": to_id,
                "departure": departure_date,
                "results": 5,
                "language": "de",
            },
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        journeys_data = response.json()
        if journeys_data and "journeys" in journeys_data:
            return journeys_data["journeys"]
        else:
            print(f"No journeys found from '{from_id}' to '{to_id}' for '{departure_date}'.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error finding journeys from '{from_id}' to '{to_id}': {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Error parsing response for journeys from '{from_id}' to '{to_id}': {e}")
        return None

if __name__ == "__main__":
    # Test find_station_id
    station_name_1 = "Berlin Hbf"
    station_id_1 = find_station_id(station_name_1)

    if station_id_1:
        print(f"Successfully found station ID for {station_name_1}: {station_id_1}")

        station_name_2 = "München Hbf"
        station_id_2 = find_station_id(station_name_2)

        if station_id_2:
            print(f"Successfully found station ID for {station_name_2}: {station_id_2}")

            # Test find_journeys
            # Using a future date to ensure there are likely journeys
            import datetime
            #departure_datetime = datetime.datetime.now() + datetime.timedelta(days=7)
            #departure_date_iso = departure_datetime.isoformat()
            # A fixed future date for more consistent testing if API allows past dates for structural tests
            departure_date_iso = "2024-09-15T10:00:00+02:00"


            journeys = find_journeys(station_id_1, station_id_2, departure_date_iso)

            if journeys:
                print(f"\nFound {len(journeys)} journeys from {station_name_1} to {station_name_2} on {departure_date_iso}:")
                for i, journey in enumerate(journeys):
                    print(f"\nJourney {i+1}:")
                    if "legs" in journey and journey["legs"]:
                        first_leg = journey["legs"][0]
                        last_leg = journey["legs"][-1]
                        departure_time = first_leg.get("departure", "N/A")
                        arrival_time = last_leg.get("arrival", "N/A")
                        origin_name = first_leg.get("origin", {}).get("name", "N/A")
                        destination_name = last_leg.get("destination", {}).get("name", "N/A")
                        print(f"  Origin: {origin_name}, Departure: {departure_time}")
                        print(f"  Destination: {destination_name}, Arrival: {arrival_time}")
                        # You can print more details about each leg or the journey itself here
                    else:
                        print("  Journey details (legs) not available.")
            else:
                print(f"Could not find journeys from {station_name_1} to {station_name_2} on {departure_date_iso}.")
        else:
            print(f"Could not find station ID for {station_name_2}, cannot test find_journeys.")
    else:
        print(f"Could not find station ID for {station_name_1}, cannot test find_journeys.")
