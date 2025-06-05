import openfoodfacts # The official Open Food Facts SDK
from calorie_calculator_structures import FoodInfo # Assuming this file is in the same directory
from typing import Optional
import re # For parsing serving size

# Standard energy conversion factor: 1 kcal = 4.184 kJ
KJ_TO_KCAL_CONVERSION_FACTOR = 4.184

def parse_serving_size_to_grams(serving_size_str: Optional[str]) -> Optional[float]:
    """
    Attempts to parse a serving size string (e.g., "30 g", "100ml") into grams.
    Currently handles simple cases like "X g".
    Returns None if parsing fails or unit is not grams.
    """
    if serving_size_str is None:
        return None

    # Regex to find a number followed by 'g' (case insensitive)
    # Allows for optional space, and captures the number.
    match = re.search(r"(\d+(\.\d+)?)\s*g\b", serving_size_str, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    # TODO: Could add conversions for 'ml' if density is known or assumed 1g/ml for some liquids
    return None

def search_food_by_name(food_name: str, user_agent: str = "CalorieCalculatorApp/1.0") -> Optional[FoodInfo]:
    """
    Searches for a food item by its name using the Open Food Facts API and returns
    structured FoodInfo if found and calorie data is available.

    Args:
        food_name: The name of the food item to search for (e.g., "apple", "Nutella").
        user_agent: The user agent string for the API request.

    Returns:
        A FoodInfo object if the food is found and has calorie data, otherwise None.
    """
    try:
        api = openfoodfacts.API(user_agent=user_agent)
        search_results = api.product.text_search(food_name)
    except Exception as e:
        print(f"Error during API request to Open Food Facts: {e}")
        return None

    if not search_results or not search_results.get("products") or len(search_results["products"]) == 0:
        print(f"No products found for '{food_name}' on Open Food Facts.")
        return None

    # Select the first product from the results
    product = search_results["products"][0]

    # --- Data Extraction ---
    product_name_en = product.get('product_name_en')
    product_name_generic = product.get('product_name')
    # Prefer English name, fallback to generic product name, then the original search term if none found
    name = product_name_en or product_name_generic or food_name

    nutriments = product.get('nutriments', {})
    calories_100g = None

    # 1. Try 'energy-kcal_100g' first (already in kcal)
    if 'energy-kcal_100g' in nutriments:
        try:
            calories_100g = float(nutriments['energy-kcal_100g'])
        except (ValueError, TypeError):
            print(f"Warning: 'energy-kcal_100g' for '{name}' is not a valid number: {nutriments['energy-kcal_100g']}")
            calories_100g = None

    # 2. If not found or invalid, try 'energy_100g' (might be in kJ)
    if calories_100g is None and 'energy_100g' in nutriments:
        try:
            energy_value_kj = float(nutriments['energy_100g'])
            # Assumption: If unit is not explicitly kcal, and value is high, it might be kJ.
            # Open Food Facts 'energy_100g' is typically kJ. 'energy-kcal_100g' is kcal.
            # For this example, we assume 'energy_100g' is kJ and convert.
            # A more robust solution would check 'energy-kcal_unit' or 'energy_unit' if available.
            calories_100g = energy_value_kj / KJ_TO_KCAL_CONVERSION_FACTOR
            print(f"Info: Converted 'energy_100g' ({energy_value_kj} kJ) to {calories_100g:.2f} kcal for '{name}'.")
        except (ValueError, TypeError):
            print(f"Warning: 'energy_100g' for '{name}' is not a valid number: {nutriments['energy_100g']}")
            calories_100g = None

    if calories_100g is None:
        print(f"Calorie information (energy-kcal_100g or energy_100g) not found or invalid for '{name}'.")
        # If product has "nova_group" it's likely a food, so missing calories is more significant.
        # If it doesn't, it might be a non-food item found by mistake.
        if 'nova_group' in product:
            print(f"Product '{name}' (ID: {product.get('code')}) seems to be a food item but lacks calorie data.")
        return None # Essential data missing

    # Get serving size (string, e.g., "30 g")
    serving_size_str = product.get('serving_size')
    serving_size_g = parse_serving_size_to_grams(serving_size_str)
    if serving_size_str and serving_size_g is None:
        print(f"Info: Serving size for '{name}' is '{serving_size_str}', which could not be parsed into grams.")


    # Get product ID (barcode)
    api_id = product.get('code') or product.get('_id')

    return FoodInfo(
        name=name,
        calories_per_100g=round(calories_100g, 2), # Round to 2 decimal places
        serving_size_g=serving_size_g,
        source_api_id=api_id
    )

if __name__ == "__main__":
    print("--- Testing Open Food Facts Client ---")

    test_foods = ["apple", "Nutella", "Coca-Cola Zero", "nonexistentfooditemxyz123", "water"]

    for food_item_name in test_foods:
        print(f"\nSearching for: '{food_item_name}'...")
        food_info = search_food_by_name(food_item_name)
        if food_info:
            print(f"Found: {food_info}")
        else:
            print(f"Could not retrieve or process valid FoodInfo for '{food_item_name}'.")
        print("-" * 30)

    # Example of a product that might have energy in kJ (e.g. some European products)
    # This depends on availability and specific product data on OpenFoodFacts
    print(f"\nSearching for a product that might primarily have kJ: 'Haribo Goldbären'...")
    food_info_kj = search_food_by_name("Haribo Goldbären") # Example, actual data varies
    if food_info_kj:
        print(f"Found: {food_info_kj}")
    else:
        print(f"Could not retrieve or process valid FoodInfo for 'Haribo Goldbären'.")
    print("-" * 30)

    print("\nNote: API responses and data availability from Open Food Facts can change.")
    print("The 'user_agent' helps identify your script to the API.")
