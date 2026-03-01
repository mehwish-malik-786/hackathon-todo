'use client';

import ChatWindow from '@/components/ChatWindow';
import Link from 'next/link';
import { useEffect, useState } from 'react';

/**
 * Generate or get session ID for chat
 */
function getSessionId(): string {
  if (typeof window === 'undefined') return 'default-session';
  
  let sessionId = localStorage.getItem('chat_session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    localStorage.setItem('chat_session_id', sessionId);
  }
  return sessionId;
}

/**
 * Chat page - AI-powered task management interface
 */
export default function ChatPage() {
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    setSessionId(getSessionId());
  }, []);

  if (!sessionId) {
    return (
      <div className="container mt-5">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <main className="min-vh-100 bg-light">
      {/* Header */}
      <div className="bg-white border-bottom">
        <div className="container py-3">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="h3 mb-0">🤖 AI Chatbot Assistant</h1>
              <p className="text-muted mb-0">Manage your tasks with natural language</p>
            </div>
            <div>
              <Link href="/" className="btn btn-outline-secondary">
                ← Back to Tasks
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Window */}
      <div className="container py-4">
        <div className="row justify-content-center">
          <div className="col-lg-8">
            <ChatWindow sessionId={sessionId} />
          </div>
        </div>
      </div>

      {/* Help Section */}
      <div className="container pb-4">
        <div className="card">
          <div className="card-body">
            <h5 className="card-title">💡 Example Commands</h5>
            <div className="row mt-3">
              <div className="col-md-6">
                <ul className="list-unstyled">
                  <li className="mb-2">
                    <code className="text-primary">"Add task buy milk tomorrow"</code>
                    <br />
                    <small className="text-muted">Create a new task</small>
                  </li>
                  <li className="mb-2">
                    <code className="text-primary">"Show my pending tasks"</code>
                    <br />
                    <small className="text-muted">List tasks by status</small>
                  </li>
                </ul>
              </div>
              <div className="col-md-6">
                <ul className="list-unstyled">
                  <li className="mb-2">
                    <code className="text-primary">"Mark task 1 as done"</code>
                    <br />
                    <small className="text-muted">Complete a task</small>
                  </li>
                  <li className="mb-2">
                    <code className="text-primary">"Delete task 3"</code>
                    <br />
                    <small className="text-muted">Remove a task</small>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
