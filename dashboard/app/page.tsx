import { redirect } from 'next/navigation';

// Root redirects to default language
export default function RootPage() {
  redirect('/en/dashboard');
}
