import React, { useState } from 'react';
import { X, CreditCard, Plane, Hotel, Calendar, DollarSign } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { useToast } from '../hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Test Stripe publishable key (replace with actual key)
const stripePromise = loadStripe('pk_test_51QdwEtP3CEOqPjANaDdGWDf3NNRCq4aeHMUJACLiTlL6gV9TSwlJ0E1KvKqUb2w9Aq5fgY8U9QNHwj1iBQTkAcmu00a7RiJVRp');

const PaymentForm = ({ booking, onSuccess }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!stripe || !elements) return;

    setIsProcessing(true);

    try {
      // In production, create payment intent on backend
      // For MVP, simulate successful payment
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Confirm booking
      const response = await fetch(`${API}/bookings/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          booking_id: booking.booking_id,
          stripe_payment_intent_id: 'pi_test_' + Date.now()
        })
      });

      if (response.ok) {
        toast({
          title: 'Success!',
          description: 'Your booking has been confirmed',
        });
        onSuccess();
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Payment failed. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="bg-gray-50 p-4 rounded-lg">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Card Information
        </label>
        <div className="bg-white p-3 rounded border border-gray-300">
          <CardElement
            options={{
              style: {
                base: {
                  fontSize: '16px',
                  color: '#424770',
                  '::placeholder': {
                    color: '#aab7c4',
                  },
                },
              },
            }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-2">
          🛡️ Test mode: Use 4242 4242 4242 4242 with any future date and CVC
        </p>
      </div>

      <Button
        type="submit"
        className="w-full"
        disabled={!stripe || isProcessing}
        data-testid="confirm-payment-button"
      >
        {isProcessing ? 'Processing...' : `Pay ${booking.currency} $${booking.total_cost.toFixed(2)}`}
      </Button>
    </form>
  );
};

const BookingModal = ({ booking, onClose, onConfirm }) => {
  const itinerary = booking.itinerary;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-800" data-testid="booking-modal-title">
                Review Your Booking
              </h2>
              <p className="text-sm text-gray-500">Please confirm the details before payment</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition"
              data-testid="close-modal-button"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Itinerary Details */}
          <div className="space-y-6 mb-6">
            {/* Outbound Flight */}
            {itinerary.outbound_flight && (
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-3">
                  <Plane className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-gray-800">Outbound Flight</h3>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Airline</p>
                    <p className="font-medium">{itinerary.outbound_flight.airline}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Route</p>
                    <p className="font-medium">
                      {itinerary.outbound_flight.origin} → {itinerary.outbound_flight.destination}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">Departure</p>
                    <p className="font-medium">{itinerary.outbound_flight.departure_time}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Price</p>
                    <p className="font-medium text-blue-600">${itinerary.outbound_flight.price}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Hotel */}
            {itinerary.hotel && (
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="flex items-center gap-2 mb-3">
                  <Hotel className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold text-gray-800">Accommodation</h3>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Hotel</p>
                    <p className="font-medium">{itinerary.hotel.name}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Location</p>
                    <p className="font-medium">{itinerary.hotel.location}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Nights</p>
                    <p className="font-medium">{itinerary.hotel.nights} nights</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Total</p>
                    <p className="font-medium text-green-600">${itinerary.hotel.total_price}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Return Flight */}
            {itinerary.return_flight && (
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-3">
                  <Plane className="w-5 h-5 text-blue-600 transform rotate-180" />
                  <h3 className="font-semibold text-gray-800">Return Flight</h3>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Airline</p>
                    <p className="font-medium">{itinerary.return_flight.airline}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Route</p>
                    <p className="font-medium">
                      {itinerary.return_flight.origin} → {itinerary.return_flight.destination}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">Departure</p>
                    <p className="font-medium">{itinerary.return_flight.departure_time}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Price</p>
                    <p className="font-medium text-blue-600">${itinerary.return_flight.price}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Total Cost */}
          <div className="bg-gradient-to-r from-blue-500 to-indigo-600 p-4 rounded-lg text-white mb-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">Total Cost</p>
                <p className="text-3xl font-bold" data-testid="total-cost">
                  ${booking.total_cost.toFixed(2)}
                </p>
              </div>
              <DollarSign className="w-12 h-12 opacity-30" />
            </div>
          </div>

          {/* Payment Form */}
          <Elements stripe={stripePromise}>
            <PaymentForm booking={booking} onSuccess={onConfirm} />
          </Elements>
        </div>
      </Card>
    </div>
  );
};

export default BookingModal;