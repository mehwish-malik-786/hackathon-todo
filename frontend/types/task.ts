/**
 * Task interface matching backend TaskResponse schema
 */
export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: string;
  created_at: string;
  completed_at: string | null;
}

/**
 * Task creation request
 */
export interface TaskCreate {
  title: string;
  description?: string;
}

/**
 * Task update request
 */
export interface TaskUpdate {
  title?: string;
  description?: string;
}
