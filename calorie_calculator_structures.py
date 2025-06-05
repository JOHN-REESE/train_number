from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class FoodInfo:
    """
    Represents information about a food item, primarily its caloric content.
    """
    name: str  # Name of the food item (e.g., "Apple", "Chicken Breast")
    calories_per_100g: float  # Number of calories per 100 grams of the food.
                              # Could also be calories_per_serving if that's the primary unit from an API.
    serving_size_g: Optional[float] = None  # Serving size in grams, if applicable.
                                           # Useful if calories are given per serving instead of per 100g.
    source_api_id: Optional[str] = None  # An identifier from the source API,
                                         # e.g., a barcode (UPC/EAN) from OpenFoodFacts,
                                         # or a food ID from Edamam or USDA FoodData Central.

@dataclass
class ExerciseInfo:
    """
    Represents information about a physical exercise, focusing on its intensity.
    """
    name: str  # Name of the exercise (e.g., "Walking", "Running")
    mets: float # Metabolic Equivalent of Task. A measure of exercise intensity.
                # One MET is the energy expended while sitting at rest.

# Sample list of common exercises with placeholder METs values.
# Actual METs values can vary based on intensity (e.g., speed of walking/running).
# These values are illustrative.
SAMPLE_EXERCISES: List[ExerciseInfo] = [
    ExerciseInfo(name="Walking (moderate pace, 3 mph)", mets=3.5),
    ExerciseInfo(name="Running (moderate pace, 6 mph)", mets=9.8), # Adjusted for a more common value for 6mph
    ExerciseInfo(name="Cycling (leisurely, <10 mph)", mets=4.0), # Adjusted for leisurely pace
    ExerciseInfo(name="Swimming (freestyle, light/moderate effort)", mets=5.8),
    ExerciseInfo(name="Weightlifting (general, moderate effort)", mets=3.5),
]

if __name__ == "__main__":
    # Example usage (optional, just for demonstration if run directly)
    print("--- Sample FoodInfo ---")
    food1 = FoodInfo(name="Banana", calories_per_100g=89, serving_size_g=118, source_api_id="some_food_id_123")
    print(food1)

    food2 = FoodInfo(name="Almonds", calories_per_100g=579)
    print(food2)

    print("\n--- Sample Exercises (with METs) ---")
    for exercise in SAMPLE_EXERCISES:
        print(f"- {exercise.name}: {exercise.mets} METs")

    # Example of accessing fields
    if SAMPLE_EXERCISES:
        print(f"\nExample exercise: {SAMPLE_EXERCISES[0].name} has {SAMPLE_EXERCISES[0].mets} METs.")
