import React, { useState } from 'react';
import { Calendar as CalendarIcon, DollarSign, MapPin, Users } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Calendar } from './ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Slider } from './ui/slider';
import { format } from 'date-fns';

const InteractivePrompt = ({ prompt, onSubmit }) => {
  const [value, setValue] = useState(prompt.default || '');
  const [date, setDate] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = () => {
    setIsSubmitting(true);
    const finalValue = prompt.type === 'date' ? (date ? format(date, 'yyyy-MM-dd') : '') : value;
    onSubmit(finalValue);
  };

  const renderInput = () => {
    switch (prompt.type) {
      case 'date':
        return (
          <div className="space-y-3">
            <p className="text-sm text-gray-700">{prompt.label}</p>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-start text-left font-normal"
                  data-testid="date-picker-trigger"
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {date ? format(date, 'PPP') : <span>Pick a date</span>}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={date}
                  onSelect={setDate}
                  initialFocus
                  data-testid="date-calendar"
                />
              </PopoverContent>
            </Popover>
          </div>
        );

      case 'budget':
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-700">{prompt.label}</p>
              <div className="flex items-center gap-1 font-semibold text-green-600">
                <DollarSign className="w-4 h-4" />
                <span>{value || prompt.min}</span>
              </div>
            </div>
            <Slider
              value={[parseFloat(value) || prompt.min]}
              onValueChange={(val) => setValue(val[0])}
              min={prompt.min || 0}
              max={prompt.max || 10000}
              step={prompt.step || 50}
              className="w-full"
              data-testid="budget-slider"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>${prompt.min || 0}</span>
              <span>${prompt.max || 10000}</span>
            </div>
          </div>
        );

      case 'select':
        return (
          <div className="space-y-3">
            <p className="text-sm text-gray-700">{prompt.label}</p>
            <Select value={value} onValueChange={setValue}>
              <SelectTrigger className="w-full" data-testid="select-trigger">
                <SelectValue placeholder={prompt.placeholder || 'Select an option'} />
              </SelectTrigger>
              <SelectContent>
                {prompt.options.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        );

      case 'number':
        return (
          <div className="space-y-3">
            <p className="text-sm text-gray-700">{prompt.label}</p>
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-gray-400" />
              <Input
                type="number"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                min={prompt.min || 1}
                max={prompt.max || 20}
                placeholder={prompt.placeholder}
                data-testid="number-input"
              />
            </div>
          </div>
        );

      case 'text':
      default:
        return (
          <div className="space-y-3">
            <p className="text-sm text-gray-700">{prompt.label}</p>
            <div className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-gray-400" />
              <Input
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder={prompt.placeholder}
                data-testid="text-input"
              />
            </div>
          </div>
        );
    }
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border-2 border-blue-200 shadow-sm">
      {renderInput()}
      <Button
        onClick={handleSubmit}
        disabled={isSubmitting || (!value && !date)}
        className="w-full mt-4"
        data-testid="submit-prompt-button"
      >
        {isSubmitting ? 'Submitting...' : 'Continue'}
      </Button>
    </div>
  );
};

export default InteractivePrompt;
