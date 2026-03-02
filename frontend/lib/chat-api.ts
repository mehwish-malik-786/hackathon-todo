import api from './api';
import { ChatRequest, ChatResponse, ConversationHistory } from '@/types/chat';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Chat API methods
export const chatApi = {
  /**
   * Send message to AI chatbot
   */
  sendMessage: (data: ChatRequest) => 
    api.post<ChatResponse>('/api/chat', data),

  /**
   * Get conversation history
   */
  getHistory: (sessionId: string) => 
    api.get<ConversationHistory>(`/api/chat/history/${sessionId}`),

  /**
   * Health check for chat service
   */
  health: () => 
    api.get('/api/chat/health'),
};

export default api;
