import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Hackathon TODO',
  description: 'Simple task management app built with Next.js and FastAPI',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
