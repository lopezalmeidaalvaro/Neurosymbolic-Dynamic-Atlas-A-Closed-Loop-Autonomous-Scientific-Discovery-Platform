import { test, expect, type Page } from '@playwright/test';

function attachRuntimeGuards(page: Page) {
  const messages: string[] = [];

  page.on('console', message => {
    if (message.type() === 'error' || message.type() === 'warning') {
      messages.push(`${message.type()}: ${message.text()}`);
    }
  });

  page.on('pageerror', error => {
    messages.push(`pageerror: ${error.message}`);
  });

  return messages;
}

async function expectNoRuntimeMessages(messages: readonly string[]) {
  expect(messages.filter(message => !message.includes('favicon.ico'))).toEqual([]);
}

test.describe('Neurosymbolic Dynamic Atlas - Scientific QA Suite (FASE 3.1)', () => {
  test('redirects root to English dashboard by default', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/\/en\/dashboard/);
  });

  test('renders dashboard correctly in English and Spanish', async ({ page }) => {
    await page.goto('/en/dashboard');
    await expect(page.locator('body')).toContainText(/Dashboard/i);
    await expect(page.locator('h1, h2, h3').first()).toBeVisible();

    await page.goto('/es/dashboard');
    await expect(page.locator('body')).toContainText(/Panel|Resumen/i);
  });

  test('renders discoveries page and supports cognitive mode toggle', async ({ page }) => {
    await page.goto('/en/discoveries');
    await expect(page.locator('body')).toContainText(/Discoveries/i);

    const toggleButton = page
      .locator('button:has-text("Advanced"), button:has-text("Simple"), button:has-text("Complejo"), button:has-text("Sencillo")')
      .first();

    if (await toggleButton.count() > 0) {
      await toggleButton.click();
      await page.waitForTimeout(300);
    }
  });

  test('loads interactive physics simulator page', async ({ page }) => {
    const runtimeMessages = attachRuntimeGuards(page);

    await page.goto('/en/interactive');
    await expect(page.locator('body')).toContainText(/Interactive/i);
    await expectNoRuntimeMessages(runtimeMessages);
  });

  test('renders learning pathways and formulas', async ({ page }) => {
    await page.goto('/en/learn');
    await expect(page.locator('body')).toContainText(/Learn/i);
  });

  test('loads compare engine route in English and Spanish', async ({ page }) => {
    const runtimeMessages = attachRuntimeGuards(page);

    await page.goto('/en/compare');
    await expect(page.getByTestId('compare-engine')).toBeVisible();
    await expect(page.locator('h1').first()).toContainText(/Comparison Engine/i);

    await page.goto('/es/compare');
    await expect(page.locator('h1').first()).toContainText(/Comparaci/i);
    await expectNoRuntimeMessages(runtimeMessages);
  });

  test('shows synchronized compare metrics and session selectors', async ({ page }) => {
    await page.goto('/en/compare');

    await expect(page.locator('select')).toHaveCount(2);
    await expect(page.getByTestId('compare-deltas')).toBeVisible();
    await expect(page.getByTestId('compare-deltas')).toContainText(/Accuracy Differential/i);
  });

  test('renders replay timeline and latent evolution player', async ({ page }) => {
    await page.goto('/en/compare');

    await expect(page.getByTestId('replay-timeline')).toBeVisible();
    await expect(page.getByTestId('latent-evolution-player')).toBeVisible();
    await page.getByRole('button', { name: /Play Replay/i }).click();
    await expect(page.getByTestId('replay-timeline')).toContainText(/t =/i);
  });

  test('renders telemetry stream and supports pause, resume, and severity filters', async ({ page }) => {
    await page.goto('/en/compare');

    const consolePanel = page.getByTestId('telemetry-console');
    await expect(consolePanel).toBeVisible();
    await expect(consolePanel).toContainText(/Telemetry Stream/i);

    await consolePanel.getByRole('button', { name: /Pause/i }).click();
    await expect(consolePanel.getByRole('button', { name: /Resume/i })).toBeVisible();
    await consolePanel.getByRole('button', { name: /Resume/i }).click();
    await expect(consolePanel.getByRole('button', { name: /Pause/i })).toBeVisible();

    await consolePanel.getByRole('button', { name: /Warning/i }).click();
    await expect(consolePanel).toContainText(/WARNING/i);
  });

  test('exports compare session as JSON and CSV', async ({ page }) => {
    await page.goto('/en/compare');
    await page.getByRole('button', { name: /^Export$/i }).click();

    const jsonDownload = page.waitForEvent('download');
    await page.getByRole('button', { name: /Export JSON/i }).click();
    await expect((await jsonDownload).suggestedFilename()).toMatch(/experiment_001_\d{4}-\d{2}-\d{2}\.json/);

    const csvDownload = page.waitForEvent('download');
    await page.getByRole('button', { name: /Export CSV/i }).click();
    await expect((await csvDownload).suggestedFilename()).toMatch(/experiment_001_benchmark_\d{4}-\d{2}-\d{2}\.csv/);
  });

  test('has compare navigation in desktop sidebar and mounted mobile navigation data', async ({ page, viewport }) => {
    await page.goto('/en/dashboard');
    const compareLink = page.locator('a[href*="compare"], a[title*="Compare"], a[title*="Comparar"]').first();

    if ((viewport?.width ?? 1280) >= 768) {
      await expect(compareLink).toBeVisible();
    } else {
      await expect(compareLink).toHaveCount(1);
    }
  });

  test('renders compare page without horizontal overflow', async ({ page, viewport }) => {
    await page.goto('/en/compare');
    const width = await page.evaluate(() => document.documentElement.scrollWidth);
    expect(width).toBeLessThanOrEqual((viewport?.width ?? 1280) + 1);
  });

  test('has no hydration warnings or runtime console errors on critical routes', async ({ page }) => {
    const runtimeMessages = attachRuntimeGuards(page);

    for (const route of ['/en/dashboard', '/en/interactive', '/en/compare', '/es/compare']) {
      await page.goto(route);
      await page.waitForLoadState('networkidle');
    }

    await expectNoRuntimeMessages(runtimeMessages);
  });
});
