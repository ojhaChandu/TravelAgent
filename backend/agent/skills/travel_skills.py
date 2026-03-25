"""
Travel Skills - Modular tools for the agent
Each skill is a callable function that returns structured data
"""
import json
from typing import Dict, List, Optional
from ..utils.mock_data import generate_flights, generate_hotels, generate_itinerary


class FlightSearchSkill:
    """Search for flights between cities"""
    
    name = "flight_search"
    description = """Search for available flights between two cities.
    
    Parameters:
    - origin: Departure city (e.g., "New York", "LAX", "London")
    - destination: Arrival city (e.g., "Paris", "Tokyo", "SFO")  
    - date: Departure date in YYYY-MM-DD format
    - budget: Optional maximum price per ticket
    
    Returns: List of flight options with prices, times, and availability
    """
    
    def execute(self, origin: str, destination: str, date: str, budget: Optional[float] = None) -> Dict:
        """Execute flight search"""
        try:
            flights = generate_flights(origin, destination, date, budget)
            
            return {
                "status": "success",
                "skill": self.name,
                "data": {
                    "origin": origin,
                    "destination": destination,
                    "date": date,
                    "flights": flights,
                    "count": len(flights)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }


class HotelSearchSkill:
    """Search for hotels in a location"""
    
    name = "hotel_search"
    description = """Search for available hotels in a specific location.
    
    Parameters:
    - location: City or area (e.g., "Paris", "Manhattan", "Tokyo")
    - check_in: Check-in date in YYYY-MM-DD format
    - check_out: Check-out date in YYYY-MM-DD format
    - budget: Optional maximum total price for stay
    
    Returns: List of hotel options with ratings, prices, and amenities
    """
    
    def execute(self, location: str, check_in: str, check_out: str, budget: Optional[float] = None) -> Dict:
        """Execute hotel search"""
        try:
            hotels = generate_hotels(location, check_in, check_out, budget)
            
            return {
                "status": "success",
                "skill": self.name,
                "data": {
                    "location": location,
                    "check_in": check_in,
                    "check_out": check_out,
                    "hotels": hotels,
                    "count": len(hotels)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }


class ItineraryGeneratorSkill:
    """Generate complete itinerary from flight and hotel selections"""
    
    name = "itinerary_generator"
    description = """Combine selected flights and hotel into a structured travel itinerary.
    
    Parameters:
    - outbound_flight: Flight details for outbound journey
    - return_flight: Flight details for return journey
    - hotel: Hotel details for accommodation
    - user_preferences: Optional user preferences (dietary, seat type, etc.)
    
    Returns: Complete itinerary with total cost breakdown
    """
    
    def execute(self, outbound_flight: Dict, return_flight: Dict, hotel: Dict, 
                user_preferences: Optional[Dict] = None) -> Dict:
        """Generate itinerary"""
        try:
            itinerary = generate_itinerary(outbound_flight, return_flight, hotel, user_preferences)
            
            return {
                "status": "success",
                "skill": self.name,
                "data": itinerary
            }
        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }


class BookingDraftSkill:
    """Create booking draft and trigger HITL (Human-in-the-Loop) confirmation"""
    
    name = "booking_draft"
    description = """Create a booking draft for human confirmation. This PAUSES the agent.
    
    Parameters:
    - itinerary: Complete itinerary from itinerary_generator
    - user_id: User ID for the booking
    
    Returns: Booking draft with AWAITING_HUMAN_CONFIRMATION status
    
    CRITICAL: This skill returns a special status that triggers the UI to switch
    from chat mode to transaction mode. The agent MUST NOT continue after calling this.
    """
    
    def execute(self, itinerary: Dict, user_id: str) -> Dict:
        """Create booking draft and trigger HITL pause"""
        try:
            # This is the INTERRUPT SIGNAL that breaks the agent loop
            return {
                "status": "AWAITING_HUMAN_CONFIRMATION",  # ← Critical interrupt signal
                "skill": self.name,
                "data": {
                    "booking_id": f"DRAFT_{itinerary.get('id', 'UNKNOWN')}",
                    "user_id": user_id,
                    "itinerary": itinerary,
                    "total_cost": itinerary.get("total_cost", 0),
                    "currency": itinerary.get("currency", "USD"),
                    "requires_payment": True,
                    "message": "Please review and confirm your booking. You will be redirected to payment."
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "error": str(e)
            }


# Skill registry - maps skill names to instances
SKILL_REGISTRY = {
    "flight_search": FlightSearchSkill(),
    "hotel_search": HotelSearchSkill(),
    "itinerary_generator": ItineraryGeneratorSkill(),
    "booking_draft": BookingDraftSkill(),
}


def get_skill(skill_name: str):
    """Get skill instance by name"""
    return SKILL_REGISTRY.get(skill_name)


def get_all_skills_description() -> str:
    """Get formatted description of all available skills for agent prompt"""
    descriptions = []
    for skill_name, skill in SKILL_REGISTRY.items():
        descriptions.append(f"**{skill_name}**:\n{skill.description}\n")
    return "\n".join(descriptions)
