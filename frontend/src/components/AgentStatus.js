import React from 'react';
import { Loader2, Brain, Wrench, Eye } from 'lucide-react';

const AgentStatus = ({ status }) => {
  const getIcon = () => {
    switch (status.status) {
      case 'thinking':
        return <Brain className="w-4 h-4 animate-pulse" />;
      case 'acting':
        return <Wrench className="w-4 h-4" />;
      case 'observation':
        return <Eye className="w-4 h-4" />;
      default:
        return <Loader2 className="w-4 h-4 animate-spin" />;
    }
  };

  return (
    <div className="flex items-center gap-2 text-sm text-gray-600 animate-fade-in" data-testid="agent-status">
      <div className="flex items-center gap-2 bg-blue-50 px-3 py-2 rounded-full border border-blue-200">
        {getIcon()}
        <span>{status.message}</span>
      </div>
    </div>
  );
};

export default AgentStatus;