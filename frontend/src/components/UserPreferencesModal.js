import React, { useState } from 'react';
import { X, DollarSign, Armchair, UtensilsCrossed } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { useToast } from '../hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserPreferencesModal = ({ user, onClose }) => {
  const [preferences, setPreferences] = useState(user.preferences || {
    budget: 1000,
    seat_type: 'economy',
    dietary_restrictions: []
  });
  const [isSaving, setIsSaving] = useState(false);
  const { toast } = useToast();

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await fetch(`${API}/users/${user.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preferences })
      });

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Your preferences have been saved',
        });
        onClose();
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to save preferences',
        variant: 'destructive'
      });
    } finally {
      setIsSaving(false);
    }
  };

  const toggleDietary = (item) => {
    setPreferences(prev => ({
      ...prev,
      dietary_restrictions: prev.dietary_restrictions.includes(item)
        ? prev.dietary_restrictions.filter(i => i !== item)
        : [...prev.dietary_restrictions, item]
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="bg-white rounded-2xl shadow-2xl max-w-md w-full">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">Travel Preferences</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <div className="space-y-6">
            {/* Budget */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <DollarSign className="w-5 h-5 text-green-600" />
                <label className="font-medium text-gray-700">Budget (USD)</label>
              </div>
              <Input
                type="number"
                value={preferences.budget || ''}
                onChange={(e) => setPreferences(prev => ({ ...prev, budget: parseFloat(e.target.value) }))}
                placeholder="1000"
                data-testid="budget-input"
              />
              <p className="text-xs text-gray-500 mt-1">Maximum budget for your trips</p>
            </div>

            {/* Seat Type */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Armchair className="w-5 h-5 text-blue-600" />
                <label className="font-medium text-gray-700">Preferred Seat Type</label>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {['economy', 'business', 'first'].map((type) => (
                  <button
                    key={type}
                    onClick={() => setPreferences(prev => ({ ...prev, seat_type: type }))}
                    className={`px-4 py-2 rounded-lg border-2 transition capitalize ${
                      preferences.seat_type === type
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    data-testid={`seat-type-${type}`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            {/* Dietary Restrictions */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <UtensilsCrossed className="w-5 h-5 text-orange-600" />
                <label className="font-medium text-gray-700">Dietary Restrictions</label>
              </div>
              <div className="flex flex-wrap gap-2">
                {['vegetarian', 'vegan', 'gluten-free', 'halal', 'kosher'].map((diet) => (
                  <button
                    key={diet}
                    onClick={() => toggleDietary(diet)}
                    className={`px-3 py-1 rounded-full border-2 transition text-sm capitalize ${
                      preferences.dietary_restrictions?.includes(diet)
                        ? 'border-orange-500 bg-orange-50 text-orange-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    data-testid={`dietary-${diet}`}
                  >
                    {diet}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-6 flex gap-3">
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isSaving} className="flex-1" data-testid="save-preferences-button">
              {isSaving ? 'Saving...' : 'Save Preferences'}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default UserPreferencesModal;