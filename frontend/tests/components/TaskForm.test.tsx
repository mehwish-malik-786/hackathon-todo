import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TaskForm from '@/components/TaskForm';

describe('TaskForm', () => {
  const mockOnAdd = vi.fn();
  const mockOnUpdate = vi.fn();
  const mockOnCancelEdit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders form with title and description fields', () => {
    render(
      <TaskForm
        onAdd={mockOnAdd}
        onUpdate={mockOnUpdate}
        editingTask={null}
        onCancelEdit={mockOnCancelEdit}
      />
    );

    expect(screen.getByPlaceholderText(/what needs to be done/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/add a description/i)).toBeInTheDocument();
  });

  it('calls onAdd when form is submitted with title', async () => {
    render(
      <TaskForm
        onAdd={mockOnAdd}
        onUpdate={mockOnUpdate}
        editingTask={null}
        onCancelEdit={mockOnCancelEdit}
      />
    );

    const titleInput = screen.getByPlaceholderText(/what needs to be done/i);
    const submitButton = screen.getByText(/add task/i);

    fireEvent.change(titleInput, { target: { value: 'Test Task' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnAdd).toHaveBeenCalledWith('Test Task', undefined);
    });
  });

  it('calls onAdd with description when provided', async () => {
    render(
      <TaskForm
        onAdd={mockOnAdd}
        onUpdate={mockOnUpdate}
        editingTask={null}
        onCancelEdit={mockOnCancelEdit}
      />
    );

    const titleInput = screen.getByPlaceholderText(/what needs to be done/i);
    const descInput = screen.getByPlaceholderText(/add a description/i);
    const submitButton = screen.getByText(/add task/i);

    fireEvent.change(titleInput, { target: { value: 'Test Task' } });
    fireEvent.change(descInput, { target: { value: 'Test Description' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnAdd).toHaveBeenCalledWith('Test Task', 'Test Description');
    });
  });

  it('does not submit when title is empty', () => {
    render(
      <TaskForm
        onAdd={mockOnAdd}
        onUpdate={mockOnUpdate}
        editingTask={null}
        onCancelEdit={mockOnCancelEdit}
      />
    );

    const submitButton = screen.getByText(/add task/i);
    fireEvent.click(submitButton);

    expect(mockOnAdd).not.toHaveBeenCalled();
  });

  it('shows update mode when editingTask is provided', () => {
    const editingTask = {
      id: 1,
      title: 'Edit Me',
      description: 'Original Description',
      status: 'pending',
      created_at: '2024-01-01T00:00:00Z',
      completed_at: null,
    };

    render(
      <TaskForm
        onAdd={mockOnAdd}
        onUpdate={mockOnUpdate}
        editingTask={editingTask}
        onCancelEdit={mockOnCancelEdit}
      />
    );

    expect(screen.getByDisplayValue('Edit Me')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Original Description')).toBeInTheDocument();
    expect(screen.getByText(/update task/i)).toBeInTheDocument();
    expect(screen.getByText(/cancel/i)).toBeInTheDocument();
  });

  it('calls onCancelEdit when cancel button is clicked', () => {
    const editingTask = {
      id: 1,
      title: 'Edit Me',
      description: '',
      status: 'pending',
      created_at: '2024-01-01T00:00:00Z',
      completed_at: null,
    };

    render(
      <TaskForm
        onAdd={mockOnAdd}
        onUpdate={mockOnUpdate}
        editingTask={editingTask}
        onCancelEdit={mockOnCancelEdit}
      />
    );

    fireEvent.click(screen.getByText(/cancel/i));
    expect(mockOnCancelEdit).toHaveBeenCalled();
  });
});
