"""
Quick test to verify TravelAgent ReAct loop
"""
import asyncio
import sys
sys.path.insert(0, '/app/backend')

from agent import TravelAgent


async def test_agent():
    """Test agent with a simple flight search query"""
    print("🧪 Testing TravelAgent ReAct Loop...\n")
    
    # Create agent
    agent = TravelAgent(
        session_id="test_session_001",
        user_id="test_user_001",
        user_preferences={
            "budget": 1500,
            "seat_type": "economy",
            "dietary_restrictions": ["vegetarian"]
        }
    )
    
    # Test message
    test_query = "Find me cheap flights from New York to London departing next month"
    
    print(f"📝 User Query: {test_query}\n")
    print("=" * 60)
    
    # Process message
    async for event in agent.process_message(test_query):
        event_type = event.get("type")
        
        if event_type == "status":
            print(f"⚙️  STATUS: {event.get('message')}")
        
        elif event_type == "observation":
            skill = event.get("skill")
            output = event.get("output", {})
            print(f"🔍 OBSERVATION: Skill '{skill}' executed")
            print(f"   Status: {output.get('status')}")
            if output.get('status') == 'success':
                data = output.get('data', {})
                if 'flights' in data:
                    print(f"   Found {len(data['flights'])} flights")
                    for flight in data['flights'][:2]:  # Show first 2
                        print(f"      - {flight['airline']}: ${flight['price']} ({flight['origin']} → {flight['destination']})")
        
        elif event_type == "response":
            print(f"\n🤖 AGENT RESPONSE:\n{event.get('content')}\n")
        
        elif event_type == "interrupt":
            print(f"\n⏸️  HITL INTERRUPT: {event.get('status')}")
            print(f"   Booking ID: {event.get('data', {}).get('booking_id')}")
            print(f"   Message: {event.get('message')}")
        
        elif event_type == "error":
            print(f"\n❌ ERROR: {event.get('message')}")
        
        elif event_type == "complete":
            print(f"\n✅ COMPLETE: Session saved")
            snapshot = event.get('state_snapshot', {})
            print(f"   Messages: {len(snapshot.get('messages', []))}")
            print(f"   Reasoning steps: {len(snapshot.get('reasoning_history', []))}")
            print(f"   Tool calls: {len(snapshot.get('tool_outputs', []))}")
    
    print("=" * 60)
    print("\n✅ Agent test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_agent())
