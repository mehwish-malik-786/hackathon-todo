import axios from 'axios';
import { Task, TaskCreate, TaskUpdate } from '@/types/task';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create Axios instance with base configuration
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API methods for task operations
export const taskApi = {
  /**
   * Get all tasks
   */
  getAll: () => api.get<Task[]>('/tasks'),

  /**
   * Get task by ID
   */
  getById: (id: number) => api.get<Task>(`/tasks/${id}`),

  /**
   * Create a new task
   */
  create: (data: TaskCreate) => api.post<Task>('/tasks', data),

  /**
   * Update an existing task
   */
  update: (id: number, data: TaskUpdate) => api.put<Task>(`/tasks/${id}`, data),

  /**
   * Delete a task
   */
  delete: (id: number) => api.delete(`/tasks/${id}`),

  /**
   * Mark task as completed
   */
  complete: (id: number) => api.patch<Task>(`/tasks/${id}/complete`),
};

export default api;
