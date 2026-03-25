"""
Mock Travel Data with Fuzzing
Randomizes prices, times, and availability to test agent reasoning
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict

# Base mock data templates
AIRLINES = [
    {"code": "UA", "name": "United Airlines", "logo": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=100"},
    {"code": "AA", "name": "American Airlines", "logo": "https://images.unsplash.com/photo-1464037866556-6812c9d1c72e?w=100"},
    {"code": "DL", "name": "Delta Air Lines", "logo": "https://images.unsplash.com/photo-1583521214690-73421a1829a9?w=100"},
    {"code": "BA", "name": "British Airways", "logo": "https://images.unsplash.com/photo-1542296332-2e4473faf563?w=100"},
    {"code": "LH", "name": "Lufthansa", "logo": "https://images.unsplash.com/photo-1569629743817-70d8db6c323b?w=100"},
]

HOTELS = [
    {
        "name": "Grand Plaza Hotel",
        "rating": 4.5,
        "base_price": 150,
        "amenities": ["WiFi", "Pool", "Gym", "Spa", "Restaurant"],
        "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400"
    },
    {
        "name": "Comfort Inn Downtown",
        "rating": 4.0,
        "base_price": 89,
        "amenities": ["WiFi", "Breakfast", "Parking"],
        "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=400"
    },
    {
        "name": "Luxury Suites & Spa",
        "rating": 5.0,
        "base_price": 280,
        "amenities": ["WiFi", "Pool", "Gym", "Spa", "Restaurant", "Concierge", "Valet"],
        "image": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=400"
    },
    {
        "name": "Budget Stay Motel",
        "rating": 3.5,
        "base_price": 55,
        "amenities": ["WiFi", "Parking"],
        "image": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=400"
    },
    {
        "name": "Boutique City Hotel",
        "rating": 4.7,
        "base_price": 195,
        "amenities": ["WiFi", "Rooftop Bar", "Gym", "Restaurant"],
        "image": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=400"
    },
]


def fuzz_price(base_price: float, variance: float = 0.15) -> float:
    """Add ±variance% randomization to price"""
    factor = 1 + random.uniform(-variance, variance)
    return round(base_price * factor, 2)


def fuzz_time(base_time: str, max_minutes: int = 45) -> str:
    """Add ±max_minutes randomization to time"""
    hour, minute = map(int, base_time.split(':'))
    base = datetime(2000, 1, 1, hour, minute)
    offset = timedelta(minutes=random.randint(-max_minutes, max_minutes))
    new_time = base + offset
    return new_time.strftime('%H:%M')


def generate_flights(origin: str, destination: str, date: str, budget: float = None) -> List[Dict]:
    """Generate fuzzed flight search results"""
    base_flights = [
        {"base_price": 350, "base_departure": "08:30", "base_arrival": "14:45", "duration": "6h 15m", "stops": 0},
        {"base_price": 280, "base_departure": "13:15", "base_arrival": "21:30", "duration": "8h 15m", "stops": 1},
        {"base_price": 420, "base_departure": "06:00", "base_arrival": "12:00", "duration": "6h 00m", "stops": 0},
        {"base_price": 195, "base_departure": "22:45", "base_arrival": "09:20", "duration": "10h 35m", "stops": 2},
        {"base_price": 315, "base_departure": "16:30", "base_arrival": "22:50", "duration": "6h 20m", "stops": 0},
    ]
    
    flights = []
    for i, flight_template in enumerate(base_flights):
        airline = random.choice(AIRLINES)
        price = fuzz_price(flight_template["base_price"], variance=0.12)
        
        # Skip if over budget
        if budget and price > budget:
            continue
        
        departure = fuzz_time(flight_template["base_departure"], max_minutes=30)
        arrival = fuzz_time(flight_template["base_arrival"], max_minutes=30)
        
        flights.append({
            "id": f"FL{i+1}{random.randint(1000, 9999)}",
            "airline": airline["name"],
            "airline_code": airline["code"],
            "logo": airline["logo"],
            "origin": origin.upper(),
            "destination": destination.upper(),
            "departure_time": departure,
            "arrival_time": arrival,
            "date": date,
            "duration": flight_template["duration"],
            "stops": flight_template["stops"],
            "price": price,
            "currency": "USD",
            "available_seats": random.randint(3, 45),
            "aircraft": random.choice(["Boeing 737", "Airbus A320", "Boeing 787", "Airbus A350"])
        })
    
    # Sort by price (cheapest first)
    return sorted(flights, key=lambda x: x["price"])[:5]


def generate_hotels(location: str, check_in: str, check_out: str, budget: float = None) -> List[Dict]:
    """Generate fuzzed hotel search results"""
    # Calculate nights
    checkin_date = datetime.strptime(check_in, "%Y-%m-%d")
    checkout_date = datetime.strptime(check_out, "%Y-%m-%d")
    nights = (checkout_date - checkin_date).days
    
    hotels = []
    for i, hotel_template in enumerate(HOTELS):
        price_per_night = fuzz_price(hotel_template["base_price"], variance=0.18)
        total_price = price_per_night * nights
        
        # Skip if over budget
        if budget and total_price > budget:
            continue
        
        # Add slight rating variance
        rating = round(hotel_template["rating"] + random.uniform(-0.2, 0.2), 1)
        rating = max(3.0, min(5.0, rating))  # Clamp between 3.0-5.0
        
        hotels.append({
            "id": f"HT{i+1}{random.randint(1000, 9999)}",
            "name": hotel_template["name"],
            "location": location,
            "rating": rating,
            "price_per_night": price_per_night,
            "total_price": total_price,
            "nights": nights,
            "currency": "USD",
            "amenities": hotel_template["amenities"],
            "image": hotel_template["image"],
            "check_in": check_in,
            "check_out": check_out,
            "available_rooms": random.randint(2, 20),
            "room_type": random.choice(["Standard Room", "Deluxe Room", "Suite", "King Room"])
        })
    
    # Sort by rating (highest first), then price
    return sorted(hotels, key=lambda x: (-x["rating"], x["total_price"]))[:5]


def generate_itinerary(flight_out: Dict, flight_return: Dict, hotel: Dict, user_preferences: Dict = None) -> Dict:
    """Combine flight and hotel into structured itinerary"""
    total_cost = flight_out["price"] + flight_return["price"] + hotel["total_price"]
    
    return {
        "id": f"ITN{random.randint(10000, 99999)}",
        "outbound_flight": flight_out,
        "return_flight": flight_return,
        "hotel": hotel,
        "total_cost": round(total_cost, 2),
        "currency": "USD",
        "duration_days": hotel["nights"] + 1,
        "user_preferences": user_preferences or {},
        "created_at": datetime.utcnow().isoformat()
    }
