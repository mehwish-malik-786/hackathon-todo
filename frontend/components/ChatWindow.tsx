'use client';

import React, { useState, useRef, useEffect } from 'react';
import { chatApi } from '@/lib/chat-api';
import { ChatMessage, ChatResponse } from '@/types/chat';

interface ChatWindowProps {
  sessionId: string;
}

/**
 * ChatWindow Component
 * 
 * Main chat interface for AI-powered task management
 */
export default function ChatWindow({ sessionId }: ChatWindowProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversation history on mount
  useEffect(() => {
    loadHistory();
  }, [sessionId]);

  const loadHistory = async () => {
    try {
      const response = await chatApi.getHistory(sessionId);
      if (response.data && response.data.messages) {
        setMessages(response.data.messages);
      }
    } catch (err) {
      console.log('No conversation history found');
    }
  };

  const sendMessage = async (e?: React.FormEvent) => {
    e?.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);
    setIsLoading(true);

    // Add user message to chat
    const newUserMessage: ChatMessage = {
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, newUserMessage]);

    try {
      // Send to AI chatbot
      const response = await chatApi.sendMessage({
        message: userMessage,
        session_id: sessionId,
      });

      // Add AI response to chat
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.response,
        created_at: new Date().toISOString(),
        metadata: response.data.metadata,
      };
      setMessages(prev => [...prev, aiMessage]);

    } catch (err: any) {
      console.error('Chat error:', err);
      setError(err.response?.data?.detail || 'Failed to send message. Please try again.');
      
      // Add error message
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-window d-flex flex-column" style={{ height: '600px' }}>
      {/* Messages Area */}
      <div 
        className="flex-grow-1 overflow-auto p-3 bg-white border rounded"
        style={{ minHeight: '400px' }}
      >
        {messages.length === 0 ? (
          <div className="text-center text-muted mt-5">
            <h5>👋 Welcome to AI Chatbot!</h5>
            <p className="mt-2">Try saying:</p>
            <ul className="list-unstyled">
              <li>• "Add task buy milk tomorrow"</li>
              <li>• "Show my tasks"</li>
              <li>• "Summarize my tasks"</li>
              <li>• "Mark task 1 as done"</li>
            </ul>
          </div>
        ) : (
          <div className="d-flex flex-column gap-2">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`p-3 rounded ${
                  msg.role === 'user'
                    ? 'bg-primary text-white ms-auto'
                    : 'bg-light text-dark me-auto'
                }`}
                style={{ maxWidth: '80%', alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start' }}
              >
                <div className="mb-1">
                  <small className={msg.role === 'user' ? 'text-light' : 'text-muted'}>
                    {msg.role === 'user' ? 'You' : 'AI Assistant'}
                  </small>
                </div>
                <div>{msg.content}</div>
                {msg.created_at && (
                  <div className="mt-1">
                    <small style={{ fontSize: '0.75rem' }}>
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </small>
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="typing-indicator bg-light p-3 rounded me-auto">
                <div className="d-flex gap-1">
                  <span className="dot">●</span>
                  <span className="dot">●</span>
                  <span className="dot">●</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="alert alert-danger mt-2 mb-0" role="alert">
          {error}
        </div>
      )}

      {/* Input Area */}
      <form onSubmit={sendMessage} className="mt-2 d-flex gap-2">
        <input
          type="text"
          className="form-control flex-grow-1"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>

      {/* Custom Styles */}
      <style jsx>{`
        .typing-indicator .dot {
          animation: typing 1.4s infinite;
          font-size: 1.5rem;
          line-height: 1rem;
          color: #6c757d;
        }
        .typing-indicator .dot:nth-child(2) {
          animation-delay: 0.2s;
        }
        .typing-indicator .dot:nth-child(3) {
          animation-delay: 0.4s;
        }
        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
          }
          30% {
            transform: translateY(-5px);
          }
        }
      `}</style>
    </div>
  );
}
