import { render, screen, fireEvent } from '@testing-library/react';
import TaskItem from '@/components/TaskItem';

describe('TaskItem', () => {
  const mockTask = {
    id: 1,
    title: 'Test Task',
    description: 'Test Description',
    status: 'pending',
    created_at: '2024-01-01T00:00:00Z',
    completed_at: null,
  };

  const mockOnEdit = vi.fn();
  const mockOnDelete = vi.fn();
  const mockOnComplete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders task with title and description', () => {
    render(
      <TaskItem
        task={mockTask}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  it('renders task without description when not provided', () => {
    const taskWithoutDesc = { ...mockTask, description: null };

    render(
      <TaskItem
        task={taskWithoutDesc}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.queryByText('Test Description')).not.toBeInTheDocument();
  });

  it('shows pending icon for pending tasks', () => {
    render(
      <TaskItem
        task={mockTask}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText('○')).toBeInTheDocument();
  });

  it('shows completed icon and styling for completed tasks', () => {
    const completedTask = {
      ...mockTask,
      status: 'completed' as const,
      completed_at: '2024-01-01T12:00:00Z',
    };

    render(
      <TaskItem
        task={completedTask}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText('✓')).toBeInTheDocument();
    expect(screen.getByText('Test Task')).toHaveClass('text-decoration-line-through');
  });

  it('calls onComplete when complete button is clicked', () => {
    render(
      <TaskItem
        task={mockTask}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    fireEvent.click(screen.getByTitle('Mark as complete'));
    expect(mockOnComplete).toHaveBeenCalledWith(1);
  });

  it('calls onEdit when edit button is clicked', () => {
    render(
      <TaskItem
        task={mockTask}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    fireEvent.click(screen.getByTitle('Edit task'));
    expect(mockOnEdit).toHaveBeenCalledWith(mockTask);
  });

  it('calls onDelete when delete button is clicked', () => {
    render(
      <TaskItem
        task={mockTask}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    fireEvent.click(screen.getByTitle('Delete task'));
    expect(mockOnDelete).toHaveBeenCalledWith(1);
  });

  it('does not show complete button for completed tasks', () => {
    const completedTask = {
      ...mockTask,
      status: 'completed' as const,
      completed_at: '2024-01-01T12:00:00Z',
    };

    render(
      <TaskItem
        task={completedTask}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    expect(screen.queryByTitle('Mark as complete')).not.toBeInTheDocument();
  });

  it('displays created timestamp', () => {
    render(
      <TaskItem
        task={mockTask}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText(/created:/i)).toBeInTheDocument();
  });

  it('displays completed timestamp for completed tasks', () => {
    const completedTask = {
      ...mockTask,
      status: 'completed' as const,
      completed_at: '2024-01-01T12:00:00Z',
    };

    render(
      <TaskItem
        task={completedTask}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText(/completed:/i)).toBeInTheDocument();
  });
});
