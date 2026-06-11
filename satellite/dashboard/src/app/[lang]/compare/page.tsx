import { notFound } from 'next/navigation';
import { getDictionary } from '@/lib/i18n/dictionaries';
import type { Language } from '@/types';
import { ComparePageClient } from './ComparePageClient';

interface ComparePageProps {
  params: Promise<{ lang: string }>;
}

export async function generateStaticParams() {
  return [{ lang: 'en' }, { lang: 'es' }];
}

export default async function ComparePage({ params }: ComparePageProps) {
  const { lang: rawLang } = await params;
  const lang = rawLang as Language;
  if (lang !== 'en' && lang !== 'es') notFound();
  const dict = getDictionary(lang);
  return <ComparePageClient lang={lang} dict={dict} />;
}
