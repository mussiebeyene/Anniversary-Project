import type { Metadata } from 'next';
import { Fraunces, Outfit } from 'next/font/google';
import './globals.css';

const display = Fraunces({
  subsets: ['latin'],
  variable: '--font-display',
});

const sans = Outfit({
  subsets: ['latin'],
  variable: '--font-sans',
});

export const metadata: Metadata = {
  title: 'Our Journey Together',
  description: 'Nine milestones, a present, and a chatbot trained on our messages.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${display.variable} ${sans.variable} font-[Outfit,ui-sans-serif,system-ui,sans-serif] antialiased`}>
        {children}
      </body>
    </html>
  );
}
