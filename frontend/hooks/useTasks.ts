'use client';

import { useState, useEffect, useCallback } from 'react';
import { taskApi } from '@/lib/api';
import { Task, TaskCreate } from '@/types/task';

/**
 * Custom hook for managing tasks state and operations
 */
export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch all tasks from API
   */
  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      const response = await taskApi.getAll();
      setTasks(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load tasks. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Add a new task
   */
  const addTask = useCallback(async (title: string, description?: string) => {
    const data: TaskCreate = { title, description };
    const response = await taskApi.create(data);
    setTasks((prev) => [...prev, response.data]);
    return response.data;
  }, []);

  /**
   * Update an existing task
   */
  const updateTask = useCallback(
    async (id: number, updates: { title?: string; description?: string }) => {
      const response = await taskApi.update(id, updates);
      setTasks((prev) => prev.map((t) => (t.id === id ? response.data : t)));
      return response.data;
    },
    []
  );

  /**
   * Delete a task
   */
  const deleteTask = useCallback(async (id: number) => {
    await taskApi.delete(id);
    setTasks((prev) => prev.filter((t) => t.id !== id));
  }, []);

  /**
   * Mark task as completed
   */
  const completeTask = useCallback(async (id: number) => {
    const response = await taskApi.complete(id);
    setTasks((prev) => prev.map((t) => (t.id === id ? response.data : t)));
    return response.data;
  }, []);

  // Fetch tasks on mount
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return {
    tasks,
    loading,
    error,
    addTask,
    updateTask,
    deleteTask,
    completeTask,
    refresh: fetchTasks,
  };
}
