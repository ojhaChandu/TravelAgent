import React, { useState, useEffect } from 'react';
import '@/App.css';
import ChatInterface from '@/components/ChatInterface';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Toaster } from '@/components/ui/toaster';
import { Plane, Sparkles } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    // Check if user exists in localStorage
    const savedUser = localStorage.getItem('tripwise_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
      setShowOnboarding(false);
    }
    setIsLoading(false);
  }, []);

  const createUser = async () => {
    if (!name || !email) return;

    try {
      const response = await axios.post(`${API}/users`, {
        name,
        email,
        preferences: {
          budget: 1000,
          seat_type: 'economy',
          dietary_restrictions: []
        }
      });

      const newUser = response.data;
      setUser(newUser);
      localStorage.setItem('tripwise_user', JSON.stringify(newUser));
      setShowOnboarding(false);
    } catch (error) {
      console.error('Failed to create user:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (showOnboarding) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-100 to-purple-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full p-8 bg-white shadow-2xl rounded-2xl">
          <div className="text-center mb-8">
            <div className="bg-gradient-to-br from-blue-500 to-indigo-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Plane className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome to TripWise</h1>
            <p className="text-gray-600">Your AI-powered travel assistant</p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <Input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                data-testid="name-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="john@example.com"
                data-testid="email-input"
              />
            </div>

            <Button
              onClick={createUser}
              disabled={!name || !email}
              className="w-full mt-6"
              data-testid="get-started-button"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Get Started
            </Button>
          </div>

          <div className="mt-8 pt-6 border-t">
            <p className="text-xs text-gray-500 text-center">
              By continuing, you agree to our Terms of Service and Privacy Policy
            </p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <>
      <ChatInterface user={user} />
      <Toaster />
    </>
  );
}

export default App;
