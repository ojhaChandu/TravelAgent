# ✈️ TravelAgent AI: Autonomous Concierge Framework

**TravelAgent AI** is a state-of-the-art, autonomous travel assistant built on a custom Python-native implementation of the **OpenClaw** reasoning architecture. Designed for B2C travelers and B2B travel agencies, it leverages **Claude 3.5 Sonnet** to research, compare, and draft complex multi-leg itineraries with a focus on safety, budget optimization, and user intent.

---

## 🚀 Vision
Most travel platforms are static search engines. **TravelAgent AI** is an *active agent*. It doesn't just show you links; it reasons through your preferences, checks real-time fuzzed data, and prepares a ready-to-book itinerary while maintaining a strict **Human-in-the-Loop** (HITL) protocol for final financial authorization.

## 🏗️ Technical Architecture

### 1. The "Python-Claw" Engine
A lightweight, high-performance ReAct (Reasoning-Action) loop implemented natively in Python to ensure seamless integration with FastAPI.
- **ReAct Loop:** Thinking → Action → Observation → Repeat.
- **SOUL.md:** A personality and boundary configuration file that governs the agent’s "internal monologue" and ethical constraints.
- **State Reconciliation:** Every "thought" and tool output is snapshotted to **MongoDB**, allowing sessions to be resumed across devices without losing context.

### 2. The Tech Stack
- **Frontend:** React 19 (CRA), TailwindCSS, Shadcn/UI.
- **Backend:** FastAPI (Python 3.11+).
- **Agent Brain:** Claude 3.5 Sonnet (via `emergent-llm`).
- **Database:** MongoDB (Session & User Preference storage).
- **Payments:** Stripe (Integrated for per-itinerary and concierge fees).

---

## 🛠️ Feature Roadmap

| Feature | Status | Description |
| :--- | :--- | :--- |
| **Autonomous Search** | ✅ | Flights & Hotels via fuzzed mock-data skills. |
| **HITL Booking** | ✅ | Agent pauses and triggers `AWAITING_HUMAN_CONFIRMATION` for Stripe payments. |
| **Multi-Tenancy** | ✅ | Isolated sessions and persistent user profiles. |
| **Google Auth** | 🏗️ | In-progress: Social sign-on via Firebase/Supabase. |
| **Vector Memory** | 📅 | Planned: Long-term travel history recall via Pinecone. |

---

## 🔧 Installation & Setup

### 1. Clone & Environment
```bash
git clone [https://github.com/ojhaChandu/TravelAgent.git](https://github.com/ojhaChandu/TravelAgent.git)
cd TravelAgent
```

### 2. Backend Setup
Create a .env file in the /backend directory:
```bash
CLAUDE_API_KEY=your_key_here
MONGO_URI=mongodb://localhost:27017
STRIPE_SECRET_KEY=sk_test_...
```
Install dependencies and run:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```
