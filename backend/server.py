from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone

# Import agent
from agent import TravelAgent, AgentState


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Collections
users_collection = db.users
sessions_collection = db.sessions
bookings_collection = db.bookings

# Create the main app without a prefix
app = FastAPI(title="TripWise Travel Assistant API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ===========================
# Pydantic Models
# ===========================

class UserPreferences(BaseModel):
    """User travel preferences"""
    budget: Optional[float] = None
    seat_type: Optional[str] = "economy"  # economy, business, first
    dietary_restrictions: Optional[List[str]] = []
    preferred_airlines: Optional[List[str]] = []


class User(BaseModel):
    """User model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(BaseModel):
    """Create user request"""
    name: str
    email: str
    preferences: Optional[UserPreferences] = None


class UserUpdate(BaseModel):
    """Update user request"""
    name: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[UserPreferences] = None


class ChatMessage(BaseModel):
    """Chat message"""
    role: str  # user or assistant
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatRequest(BaseModel):
    """Agent chat request"""
    user_id: str
    message: str
    session_id: Optional[str] = None


class Session(BaseModel):
    """Agent session model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    messages: List[Dict] = Field(default_factory=list)
    claw_state_snapshot: Dict = Field(default_factory=dict)  # State reconciliation
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BookingDraft(BaseModel):
    """Booking draft for HITL confirmation"""
    id: str = Field(default_factory=lambda: f"DRAFT_{uuid.uuid4()}")
    user_id: str
    session_id: str
    itinerary: Dict
    total_cost: float
    currency: str = "USD"
    status: str = "draft"  # draft, confirmed, cancelled


class BookingConfirmRequest(BaseModel):
    """Confirm booking request"""
    booking_id: str
    stripe_payment_intent_id: Optional[str] = None


# ===========================
# User Management Endpoints
# ===========================

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    user = User(
        name=user_data.name,
        email=user_data.email,
        preferences=user_data.preferences or UserPreferences()
    )
    
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['preferences'] = user.preferences.model_dump()
    
    await users_collection.insert_one(doc)
    return user


@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID"""
    user_doc = await users_collection.find_one({"id": user_id}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    return User(**user_doc)


@api_router.patch("/users/{user_id}", response_model=User)
async def update_user(user_id: str, update_data: UserUpdate):
    """Update user preferences"""
    user_doc = await users_collection.find_one({"id": user_id}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_dict = update_data.model_dump(exclude_none=True)
    if update_dict:
        if 'preferences' in update_dict:
            update_dict['preferences'] = update_dict['preferences'].model_dump()
        
        await users_collection.update_one(
            {"id": user_id},
            {"$set": update_dict}
        )
    
    updated_doc = await users_collection.find_one({"id": user_id}, {"_id": 0})
    updated_doc['created_at'] = datetime.fromisoformat(updated_doc['created_at'])
    return User(**updated_doc)


# ===========================
# Agent Chat Endpoints
# ===========================

@api_router.post("/agent/chat")
async def agent_chat(request: ChatRequest):
    """
    Chat with travel agent - returns streaming response
    
    This endpoint:
    1. Loads/creates session
    2. Initializes agent with user preferences
    3. Processes message through ReAct loop
    4. Streams status updates back to frontend
    5. Saves state snapshot to MongoDB
    """
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    # Load user preferences
    user_doc = await users_collection.find_one({"id": request.user_id}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_preferences = user_doc.get('preferences', {})
    
    # Load existing session if available
    session_doc = await sessions_collection.find_one({"id": session_id}, {"_id": 0})
    
    if session_doc and session_doc.get('claw_state_snapshot'):
        # Restore agent from snapshot (state reconciliation)
        agent = TravelAgent.from_state_snapshot(session_doc['claw_state_snapshot'])
    else:
        # Create new agent
        agent = TravelAgent(
            session_id=session_id,
            user_id=request.user_id,
            user_preferences=user_preferences
        )
    
    async def event_stream():
        """Stream agent responses as Server-Sent Events"""
        try:
            async for event in agent.process_message(request.message):
                # Send event as JSON
                yield f"data: {json.dumps(event)}\n\n"
                
                # If we hit HITL interrupt, save booking draft
                if event.get("type") == "interrupt":
                    booking_data = event.get("data", {})
                    booking_draft = BookingDraft(
                        user_id=request.user_id,
                        session_id=session_id,
                        itinerary=booking_data.get("itinerary", {}),
                        total_cost=booking_data.get("total_cost", 0),
                        currency=booking_data.get("currency", "USD"),
                        status="draft"
                    )
                    
                    draft_doc = booking_draft.model_dump()
                    await bookings_collection.insert_one(draft_doc)
                    
                    # Send booking ID back to frontend
                    yield f"data: {json.dumps({'type': 'booking_draft_created', 'booking_id': booking_draft.id})}\n\n"
            
            # Save session state to MongoDB
            state_snapshot = agent.get_state_snapshot()
            
            session_doc = {
                "id": session_id,
                "user_id": request.user_id,
                "messages": state_snapshot.get("messages", []),
                "claw_state_snapshot": state_snapshot,  # Full state for reconciliation
                "created_at": state_snapshot.get("created_at"),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await sessions_collection.update_one(
                {"id": session_id},
                {"$set": session_doc},
                upsert=True
            )
            
            yield f"data: {json.dumps({'type': 'session_saved', 'session_id': session_id})}\n\n"
            
        except Exception as e:
            logging.error(f"Agent error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@api_router.get("/agent/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """Get all sessions for a user"""
    sessions = await sessions_collection.find(
        {"user_id": user_id},
        {"_id": 0, "claw_state_snapshot": 0}  # Exclude large snapshot from list
    ).sort("updated_at", -1).to_list(100)
    
    return {"sessions": sessions}


@api_router.get("/agent/sessions/{session_id}/detail")
async def get_session_detail(session_id: str):
    """Get full session detail including state snapshot"""
    session = await sessions_collection.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


# ===========================
# Booking & Payment Endpoints
# ===========================

@api_router.get("/bookings/draft/{booking_id}")
async def get_booking_draft(booking_id: str):
    """Get booking draft for review"""
    booking = await bookings_collection.find_one({"id": booking_id}, {"_id": 0})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return booking


@api_router.post("/bookings/confirm")
async def confirm_booking(request: BookingConfirmRequest):
    """
    Confirm booking after payment
    
    In production, this would:
    1. Verify Stripe payment
    2. Call actual travel APIs to book
    3. Send confirmation email
    
    For MVP, we just mark as confirmed
    """
    booking = await bookings_collection.find_one({"id": request.booking_id}, {"_id": 0})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Update booking status
    await bookings_collection.update_one(
        {"id": request.booking_id},
        {"$set": {
            "status": "confirmed",
            "stripe_payment_intent_id": request.stripe_payment_intent_id,
            "confirmed_at": datetime.utcnow().isoformat()
        }}
    )
    
    return {
        "status": "success",
        "message": "Booking confirmed successfully",
        "booking_id": request.booking_id
    }


@api_router.get("/bookings/user/{user_id}")
async def get_user_bookings(user_id: str):
    """Get all bookings for a user"""
    bookings = await bookings_collection.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {"bookings": bookings}


# ===========================
# Health Check
# ===========================

@api_router.get("/")
async def root():
    return {
        "message": "TripWise Travel Assistant API",
        "version": "1.0.0",
        "status": "operational"
    }


@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        await db.command("ping")
        return {
            "status": "healthy",
            "mongodb": "connected",
            "agent": "ready"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
