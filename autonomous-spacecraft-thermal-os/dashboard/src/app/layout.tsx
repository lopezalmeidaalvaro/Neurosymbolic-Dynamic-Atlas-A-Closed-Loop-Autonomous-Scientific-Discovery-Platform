import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import 'katex/dist/katex.min.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    default: 'Neurosymbolic Dynamic Atlas',
    template: '%s | Neurosymbolic Atlas',
  },
  description:
    'Scientific dashboard for the Neurosymbolic Pipeline — geometric classification of nonlinear dynamical systems via latent embeddings.',
  keywords: ['dynamical systems', 'machine learning', 'chaos theory', 'latent space', 'benchmark'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased bg-[#030712] text-white`}>
        {children}
      </body>
    </html>
  );
}
