
import datetime

# Base price for each room type
BASE_PRICES = {
    "Deluxe": 1000,
    "Standard": 3000,
    "Suite": 5000
}

# Seasonal multipliers (only 4 custom seasons)
SEASONAL_MULTIPLIERS = {
    "Holiday": 1.5,    # 50% increase for holiday seasons (e.g., Christmas, New Year)
    "Offseason": 0.8,   # 20% discount for offseason (e.g., quieter periods)
    "Festive": 1.6,     # 60% increase during festive seasons (e.g., Easter, local festivals)
    "Peak": 1.4,        # 40% increase during peak tourist seasons (e.g., July-August)
}

def get_season(date):
    """Determine the season based on the date."""
    month = date.month
    if month in [12, 1, 2]:
        return "Holiday"  # Holiday season for Christmas and New Year
    elif month in [3, 4, 5]:
        return "Offseason"  # Offseason for quieter months
    elif month in [6, 7, 8]:
        return "Peak"  # Peak tourist season
    else:
        return "Festive"  # Festive season for events like Easter

def calculate_dynamic_price(room_type, date):
    """
    Calculate the dynamic price for a room based on season and base price.
    """
    # Get base price for the room type
    base_price = BASE_PRICES.get(room_type, 1000)  # Default to $1000 if room type not found

    # Get seasonal multiplier
    season = get_season(date)
    seasonal_multiplier = SEASONAL_MULTIPLIERS.get(season, 1.0)

    # Calculate final price
    final_price = base_price * seasonal_multiplier
    return round(final_price, 2)

# ANSI escape codes for colors
def print_colored(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

# Example usage with different colors
if __name__ == "__main__":
    room_type = "Deluxe"
    date = datetime.date(2025, 12, 25)  # Christmas Day
    price = calculate_dynamic_price(room_type, date)
    print(print_colored(f"Dynamic price for {room_type} on {date}: ${price}", "33"))  # Yellow text

    room_type = "Standard"
    date = datetime.date(2025, 7, 15)  # Summer (Peak season)
    price = calculate_dynamic_price(room_type, date)
    print(print_colored(f"Dynamic price for {room_type} on {date}: ${price}", "36"))  # Cyan text

    room_type = "Suite"
    date = datetime.date(2025, 4, 19)  # April 19, 2023 (Offseason)
    price = calculate_dynamic_price(room_type, date)
    print(print_colored(f"Dynamic price for {room_type} on {date}: ${price}", "35"))  # Magenta text
