import React from 'react';
import { MapPin, Star, DollarSign } from 'lucide-react';

const HotelResultCard = ({ hotel }) => {
  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden hover:shadow-lg transition" data-testid="hotel-card">
      <img src={hotel.image} alt={hotel.name} className="w-full h-48 object-cover" />
      
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h3 className="font-semibold text-gray-800 text-lg">{hotel.name}</h3>
            <div className="flex items-center gap-1 text-sm text-gray-600 mt-1">
              <MapPin className="w-3 h-3" />
              <span>{hotel.location}</span>
            </div>
          </div>
          <div className="flex items-center gap-1 bg-yellow-50 px-2 py-1 rounded">
            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            <span className="font-semibold text-sm">{hotel.rating}</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-1 mb-3">
          {hotel.amenities.slice(0, 4).map((amenity, idx) => (
            <span
              key={idx}
              className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
            >
              {amenity}
            </span>
          ))}
        </div>

        <div className="flex items-center justify-between pt-3 border-t">
          <div>
            <p className="text-xs text-gray-500">Per night</p>
            <p className="text-xl font-bold text-green-600">${hotel.price_per_night}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">{hotel.nights} nights</p>
            <p className="font-semibold text-gray-800">Total: ${hotel.total_price}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HotelResultCard;