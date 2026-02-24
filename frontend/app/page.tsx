'use client';

import TaskList from '@/components/TaskList';

/**
 * Home page - Main task list application
 */
export default function Home() {
  return (
    <main className="min-vh-100 bg-light">
      <TaskList />
    </main>
  );
}
