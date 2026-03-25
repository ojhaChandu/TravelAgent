import React from 'react';
import { Plane, Clock, DollarSign } from 'lucide-react';

const FlightResultCard = ({ flight }) => {
  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4 hover:shadow-lg transition" data-testid="flight-card">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <img src={flight.logo} alt={flight.airline} className="w-10 h-10 rounded" />
          <div>
            <p className="font-semibold text-gray-800">{flight.airline}</p>
            <p className="text-xs text-gray-500">{flight.aircraft}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-blue-600">${flight.price}</p>
          <p className="text-xs text-gray-500">{flight.currency}</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-3">
        <div>
          <p className="text-xs text-gray-500">From</p>
          <p className="font-semibold">{flight.origin}</p>
          <p className="text-sm text-gray-600">{flight.departure_time}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500">Duration</p>
          <Plane className="w-4 h-4 mx-auto text-gray-400 my-1" />
          <p className="text-sm text-gray-600">{flight.duration}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500">To</p>
          <p className="font-semibold">{flight.destination}</p>
          <p className="text-sm text-gray-600">{flight.arrival_time}</p>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-gray-600 pt-3 border-t">
        <span>{flight.stops === 0 ? 'Direct' : `${flight.stops} stop(s)`}</span>
        <span>{flight.available_seats} seats left</span>
      </div>
    </div>
  );
};

export default FlightResultCard;