import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { AmbientBackground } from '@/components/cinematic/AmbientBackground';
import { AdaptiveSidebar } from '@/components/layout/AdaptiveSidebar';
import { ExperimentalDock } from '@/components/layout/ExperimentalDock';
import { Header } from '@/components/layout/Header';
import { getDictionary, SUPPORTED_LANGUAGES } from '@/lib/i18n/dictionaries';
import type { Language } from '@/types';

export async function generateStaticParams() {
  return SUPPORTED_LANGUAGES.map((lang) => ({ lang }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ lang: string }>;
}): Promise<Metadata> {
  const { lang: rawLang } = await params;
  const lang = rawLang as Language;
  return {
    title: lang === 'es' ? 'Atlas Dinámico Neurosimbólico' : 'Neurosymbolic Dynamic Atlas',
  };
}

export default async function LangLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ lang: string }>;
}) {
  const { lang: rawLang } = await params;

  if (!SUPPORTED_LANGUAGES.includes(rawLang as Language)) {
    notFound();
  }

  const lang = rawLang as Language;
  const dict = getDictionary(lang);

  return (
    <div className="relative flex h-screen overflow-hidden">
      <AmbientBackground />
      <AdaptiveSidebar lang={lang} />
      <div className="relative flex flex-1 flex-col overflow-hidden">
        <Header lang={lang} dict={dict} />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
      <ExperimentalDock lang={lang} />
    </div>
  );
}
