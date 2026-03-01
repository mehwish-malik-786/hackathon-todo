/**
 * Chat types for AI Chatbot interface
 */

export interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at?: string;
  metadata?: {
    intent?: string;
    action?: string;
  };
}

export interface TaskData {
  id: number;
  title: string;
  description: string | null;
  status: string;
}

export interface ChatRequest {
  message: string;
  session_id: string;
}

export interface ChatResponse {
  response: string;
  action?: string;
  task?: TaskData;
  tasks?: TaskData[];
  conversation_id?: number;
  metadata?: {
    intent?: string;
    original_message?: string;
  };
}

export interface ConversationHistory {
  session_id: string;
  messages: ChatMessage[];
}
