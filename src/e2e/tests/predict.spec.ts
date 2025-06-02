import { test, expect } from '@playwright/test';

test("Fraud prediction", () => {
    test('should predict legitimate result for Legit Sample 1', async ({ page }) => {
        await page.goto('/');
        await page.getByRole('button', { name: 'Legit Sample 1' }).click();
        await page.getByRole('button', { name: 'Predict' }).click();
        await expect(page.getByText(/legitimate/i)).toBeVisible();
    });
})
