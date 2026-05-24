import type { Metadata } from 'next';
import { getDictionary } from '@/lib/i18n/dictionaries';
import { LearnPageClient } from './LearnPageClient';
import type { Language } from '@/types';

export const metadata: Metadata = { title: 'Learn' };

export default async function LearnPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang: rawLang } = await params;
  const lang = rawLang as Language;
  const dict = getDictionary(lang);

  return <LearnPageClient lang={lang} dict={dict} />;
}
