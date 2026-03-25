import React, { useState, useEffect, useRef } from 'react';
import { Send, Plane, Hotel, Settings } from 'lucide-react';
import MessageList from './MessageList';
import AgentStatus from './AgentStatus';
import BookingModal from './BookingModal';
import UserPreferencesModal from './UserPreferencesModal';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { useToast } from '../hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatInterface = ({ user }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [agentStatus, setAgentStatus] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [currentBooking, setCurrentBooking] = useState(null);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const messagesEndRef = useRef(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    try {
      const response = await fetch(`${API}/agent/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          message: input,
          session_id: sessionId
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = {
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString()
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));

              if (event.type === 'status') {
                setAgentStatus(event);
              } else if (event.type === 'response') {
                assistantMessage.content = event.content;
                setMessages(prev => [...prev.filter(m => m.role !== 'assistant' || m.content), assistantMessage]);
              } else if (event.type === 'interrupt') {
                // HITL interrupt - switch to transaction mode
                setCurrentBooking(event.data);
                setShowBookingModal(true);
                assistantMessage.content = event.message;
                setMessages(prev => [...prev, assistantMessage]);
              } else if (event.type === 'booking_draft_created') {
                setCurrentBooking(prev => ({ ...prev, booking_id: event.booking_id }));
              } else if (event.type === 'session_saved') {
                setSessionId(event.session_id);
              } else if (event.type === 'error') {
                toast({
                  title: 'Error',
                  description: event.message,
                  variant: 'destructive'
                });
              }
            } catch (e) {
              console.error('Parse error:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      toast({
        title: 'Error',
        description: 'Failed to communicate with agent',
        variant: 'destructive'
      });
    } finally {
      setIsStreaming(false);
      setAgentStatus(null);
    }
  };

  const handleBookingConfirmed = () => {
    setShowBookingModal(false);
    setCurrentBooking(null);
    const confirmMessage = {
      role: 'assistant',
      content: '✅ Booking confirmed! You should receive a confirmation email shortly.',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, confirmMessage]);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-md border-b">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-2 rounded-lg">
              <Plane className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">TripWise</h1>
              <p className="text-sm text-gray-500">Your AI Travel Assistant</p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowPreferences(true)}
            data-testid="preferences-button"
          >
            <Settings className="w-4 h-4 mr-2" />
            Preferences
          </Button>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-hidden">
        <div className="max-w-6xl mx-auto h-full flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-6" data-testid="message-list">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="bg-white p-8 rounded-2xl shadow-lg max-w-md">
                  <Plane className="w-16 h-16 text-blue-500 mx-auto mb-4" />
                  <h2 className="text-2xl font-bold text-gray-800 mb-2">Ready to Travel?</h2>
                  <p className="text-gray-600 mb-6">
                    I'm your AI travel assistant. I can help you search for flights, hotels, and create amazing itineraries!
                  </p>
                  <div className="text-left space-y-2 text-sm text-gray-600">
                    <p>💬 Try asking:</p>
                    <ul className="list-disc list-inside space-y-1 ml-2">
                      <li>"Find me flights from NYC to Paris in June"</li>
                      <li>"Show me hotels in Tokyo under $150/night"</li>
                      <li>"Plan a 5-day trip to Bali"</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
            <MessageList messages={messages} />
            {agentStatus && <AgentStatus status={agentStatus} />}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="bg-white border-t shadow-lg">
            <div className="px-4 py-4">
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                  placeholder="Ask me anything about travel..."
                  disabled={isStreaming}
                  className="flex-1"
                  data-testid="chat-input"
                />
                <Button
                  onClick={sendMessage}
                  disabled={isStreaming || !input.trim()}
                  data-testid="send-button"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      {showBookingModal && currentBooking && (
        <BookingModal
          booking={currentBooking}
          onClose={() => setShowBookingModal(false)}
          onConfirm={handleBookingConfirmed}
        />
      )}

      {showPreferences && (
        <UserPreferencesModal
          user={user}
          onClose={() => setShowPreferences(false)}
        />
      )}
    </div>
  );
};

export default ChatInterface;