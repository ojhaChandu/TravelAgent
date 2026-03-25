"""
ReAct Agent Core - Autonomous reasoning and action loop
Inspired by OpenClaw's architecture, built in Python
"""
import json
import os
import asyncio
from typing import Dict, List, Optional, AsyncGenerator
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage
from .soul import SYSTEM_MESSAGE
from .skills.travel_skills import SKILL_REGISTRY, get_all_skills_description
from dotenv import load_dotenv

load_dotenv()


class AgentState:
    """Manages agent state for persistence (claw_state_snapshot concept)"""
    
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.messages: List[Dict] = []
        self.reasoning_history: List[Dict] = []
        self.tool_outputs: List[Dict] = []
        self.user_preferences: Dict = {}
        self.current_context: Dict = {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def add_message(self, role: str, content: str):
        """Add message to history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow()
    
    def add_reasoning(self, thought: str, action: Optional[str] = None):
        """Track agent's reasoning process"""
        self.reasoning_history.append({
            "thought": thought,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow()
    
    def add_tool_output(self, skill_name: str, output: Dict):
        """Track tool execution results"""
        self.tool_outputs.append({
            "skill": skill_name,
            "output": output,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow()
    
    def to_snapshot(self) -> Dict:
        """Convert state to MongoDB-storable snapshot"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "messages": self.messages,
            "reasoning_history": self.reasoning_history,
            "tool_outputs": self.tool_outputs,
            "user_preferences": self.user_preferences,
            "current_context": self.current_context,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_snapshot(cls, snapshot: Dict) -> 'AgentState':
        """Restore state from MongoDB snapshot"""
        state = cls(snapshot["session_id"], snapshot["user_id"])
        state.messages = snapshot.get("messages", [])
        state.reasoning_history = snapshot.get("reasoning_history", [])
        state.tool_outputs = snapshot.get("tool_outputs", [])
        state.user_preferences = snapshot.get("user_preferences", {})
        state.current_context = snapshot.get("current_context", {})
        state.created_at = datetime.fromisoformat(snapshot["created_at"])
        state.updated_at = datetime.fromisoformat(snapshot["updated_at"])
        return state


class TravelAgent:
    """
    Autonomous travel assistant agent with ReAct loop
    
    Architecture:
    1. Receive user message
    2. Think: Reason about what action to take
    3. Act: Execute skill/tool or respond
    4. Observe: Process tool output
    5. Repeat until task complete or HITL trigger
    """
    
    def __init__(self, session_id: str, user_id: str, user_preferences: Dict = None):
        self.session_id = session_id
        self.user_id = user_id
        self.state = AgentState(session_id, user_id)
        
        if user_preferences:
            self.state.user_preferences = user_preferences
        
        # Initialize Claude Sonnet 4.5 via emergentintegrations
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        # Build enhanced system message with skills description
        enhanced_system = f"""{SYSTEM_MESSAGE}

## Available Skills:
{get_all_skills_description()}

## User Preferences (MUST RESPECT):
{json.dumps(user_preferences or {}, indent=2)}

## CRITICAL: Tool Call Format
When you need to use a skill, you MUST respond with ONLY the JSON object, nothing else:
{{"action": "use_skill", "skill": "skill_name", "parameters": {{"param1": "value1"}}}}

Do NOT include any conversational text before or after the JSON when making a tool call.

When you have a final answer for the user (after using tools or if no tools needed), respond in natural conversational text.

## Example Flow:
User: "Find flights from NYC to Paris"
You: {{"action": "use_skill", "skill": "flight_search", "parameters": {{"origin": "New York", "destination": "Paris", "date": "2026-04-15"}}}}
[System returns flight data]
You: "I found 5 great flights from NYC to Paris! Here are the top options: [explain results]"
"""
        
        self.llm = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=enhanced_system
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
    
    async def process_message(self, user_message: str) -> AsyncGenerator[Dict, None]:
        """
        Process user message with ReAct loop
        Yields status updates for streaming to frontend
        """
        # Add user message to state
        self.state.add_message("user", user_message)
        
        yield {
            "type": "status",
            "status": "thinking",
            "message": "🤔 Analyzing your request..."
        }
        
        # ReAct Loop (max 5 iterations to prevent infinite loops)
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # THINK: Get agent's reasoning
            try:
                response = await self.llm.send_message(UserMessage(text=user_message))
                agent_response = response.strip()
                
                self.state.add_message("assistant", agent_response)
                
                # Check if agent wants to use a skill (detect JSON action format)
                if self._is_tool_call(agent_response):
                    action = self._parse_tool_call(agent_response)
                    
                    if action:
                        skill_name = action["skill"]
                        parameters = action.get("parameters", {})
                        
                        yield {
                            "type": "status",
                            "status": "acting",
                            "message": f"🔧 Using {skill_name}..."
                        }
                        
                        # ACT: Execute skill
                        skill = SKILL_REGISTRY.get(skill_name)
                        if skill:
                            tool_output = skill.execute(**parameters)
                            self.state.add_tool_output(skill_name, tool_output)
                            
                            # CRITICAL: Check for HITL interrupt signal
                            if tool_output.get("status") == "AWAITING_HUMAN_CONFIRMATION":
                                yield {
                                    "type": "interrupt",
                                    "status": "AWAITING_HUMAN_CONFIRMATION",
                                    "data": tool_output.get("data"),
                                    "message": tool_output.get("data", {}).get("message", "Awaiting confirmation")
                                }
                                # STOP the loop - hand control to human
                                break
                            
                            # OBSERVE: Add tool output to context for next iteration
                            observation = f"Tool {skill_name} returned: {json.dumps(tool_output, indent=2)}"
                            user_message = f"Previous tool output:\n{observation}\n\nContinue with the user's original request."
                            
                            yield {
                                "type": "observation",
                                "skill": skill_name,
                                "output": tool_output
                            }
                        else:
                            yield {
                                "type": "error",
                                "message": f"Skill {skill_name} not found"
                            }
                            break
                else:
                    # Agent provided final text response
                    yield {
                        "type": "response",
                        "content": agent_response
                    }
                    break
                    
            except Exception as e:
                yield {
                    "type": "error",
                    "message": f"Agent error: {str(e)}"
                }
                break
        
        # Final state update
        yield {
            "type": "complete",
            "state_snapshot": self.state.to_snapshot()
        }
    
    def _is_tool_call(self, response: str) -> bool:
        """Check if response contains a tool call JSON"""
        parsed = self._parse_tool_call(response)
        return parsed is not None
    
    def _parse_tool_call(self, response: str) -> Optional[Dict]:
        """Extract tool call JSON from response (handles mixed text + JSON)"""
        # Find the first occurrence of {"action": "use_skill"
        import re
        
        # Try to find JSON object that contains action and use_skill
        # Strategy: Find first { and try to parse balanced braces
        start_idx = response.find('{')
        if start_idx == -1:
            return None
        
        # Count braces to find matching closing brace
        brace_count = 0
        for i in range(start_idx, len(response)):
            if response[i] == '{':
                brace_count += 1
            elif response[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Found matching closing brace
                    json_str = response[start_idx:i+1]
                    try:
                        parsed = json.loads(json_str)
                        if isinstance(parsed, dict) and parsed.get("action") == "use_skill":
                            return parsed
                    except:
                        pass
                    # Try next opening brace
                    next_start = response.find('{', i+1)
                    if next_start != -1:
                        return self._parse_tool_call(response[next_start:])
                    break
        
        return None
    
    def get_state_snapshot(self) -> Dict:
        """Get current state for MongoDB persistence"""
        return self.state.to_snapshot()
    
    @classmethod
    def from_state_snapshot(cls, snapshot: Dict) -> 'TravelAgent':
        """Restore agent from MongoDB snapshot"""
        agent = cls(
            session_id=snapshot["session_id"],
            user_id=snapshot["user_id"],
            user_preferences=snapshot.get("user_preferences", {})
        )
        agent.state = AgentState.from_snapshot(snapshot)
        return agent
