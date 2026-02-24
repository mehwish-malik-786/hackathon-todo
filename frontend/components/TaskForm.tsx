'use client';

import { useState, useEffect } from 'react';
import { Task } from '@/types/task';

interface TaskFormProps {
  onAdd: (title: string, description?: string) => Promise<Task | void>;
  onUpdate: (id: number, updates: { title?: string; description?: string }) => Promise<Task | void>;
  editingTask: Task | null;
  onCancelEdit: () => void;
}

/**
 * Task form component for adding and editing tasks
 */
export default function TaskForm({ onAdd, onUpdate, editingTask, onCancelEdit }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Populate form when editing
  useEffect(() => {
    if (editingTask) {
      setTitle(editingTask.title);
      setDescription(editingTask.description || '');
    } else {
      setTitle('');
      setDescription('');
    }
  }, [editingTask]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim()) {
      return;
    }

    setIsSubmitting(true);
    try {
      if (editingTask) {
        await onUpdate(editingTask.id, { title: title.trim(), description: description.trim() || undefined });
      } else {
        await onAdd(title.trim(), description.trim() || undefined);
      }
      setTitle('');
      setDescription('');
    } catch (error) {
      console.error('Failed to save task:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setTitle('');
    setDescription('');
    onCancelEdit();
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <div className="mb-3">
        <input
          type="text"
          className="form-control form-control-lg"
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          disabled={isSubmitting}
        />
      </div>
      <div className="mb-3">
        <textarea
          className="form-control"
          placeholder="Add a description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          disabled={isSubmitting}
        />
      </div>
      <div className="d-flex gap-2">
        <button
          type="submit"
          className="btn btn-primary btn-lg"
          disabled={isSubmitting || !title.trim()}
        >
          {isSubmitting ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {editingTask ? 'Updating...' : 'Adding...'}
            </>
          ) : (
            <>{editingTask ? 'Update Task' : 'Add Task'}</>
          )}
        </button>
        {editingTask && (
          <button
            type="button"
            className="btn btn-secondary btn-lg"
            onClick={handleCancel}
            disabled={isSubmitting}
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
