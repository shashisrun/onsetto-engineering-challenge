import { test } from "@playwright/test";

import { AccountPage } from "../pages/AccountPage.js";
import { LoginPage } from "../pages/LoginPage.js";
import { bankingDetails, credentials, paymentDetails } from "../test-data.js";

test("authenticated user can update banking details and payment method", async ({
  page,
}) => {
  const loginPage = new LoginPage(page);
  const accountPage = new AccountPage(page);

  await test.step("Sign in with MFA", async () => {
    await loginPage.signInWithMfa(credentials);
  });

  await test.step("Open account settings", async () => {
    await accountPage.goto();
  });

  await test.step("Update banking details", async () => {
    await accountPage.updateBanking(bankingDetails);
  });

  await test.step("Update payment method", async () => {
    await accountPage.updatePayment(paymentDetails);
  });
});
