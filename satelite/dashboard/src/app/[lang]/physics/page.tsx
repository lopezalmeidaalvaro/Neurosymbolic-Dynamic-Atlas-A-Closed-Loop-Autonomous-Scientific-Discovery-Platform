import { redirect } from 'next/navigation';

export default async function LocalizedPhysicsRedirectPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  redirect(`/${lang}/dashboard`);
}
