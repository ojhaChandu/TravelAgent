import React from 'react';
import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import InteractivePrompt from './InteractivePrompt';

const MessageList = ({ messages, onPromptResponse }) => {
  return (
    <div className="space-y-4">
      {messages.map((message, index) => {
        // Check if this is an interactive prompt from agent
        const hasInteractivePrompt = message.role === 'assistant' && message.interactive_prompt;

        return (
          <div key={index}>
            <div
              className={`flex gap-3 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
              data-testid={`message-${message.role}`}
            >
              {message.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}
              
              <div
                className={`max-w-2xl rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white shadow-md border border-gray-100'
                }`}
              >
                {message.role === 'assistant' ? (
                  <div className="prose prose-sm max-w-none prose-headings:text-gray-800 prose-p:text-gray-700 prose-strong:text-gray-900 prose-ul:text-gray-700 prose-li:text-gray-700">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap">{message.content}</p>
                )}
              </div>

              {message.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
            </div>

            {/* Interactive Prompt UI */}
            {hasInteractivePrompt && (
              <div className="ml-11 mt-2">
                <InteractivePrompt
                  prompt={message.interactive_prompt}
                  onSubmit={(value) => onPromptResponse(value)}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default MessageList;
