import { test } from "@playwright/test";

import { AccountPage } from "../pages/AccountPage.js";
import { LoginPage } from "../pages/LoginPage.js";
import { bankingDetails, credentials, paymentDetails } from "../test-data.js";

test("updates banking details and payment method", async ({ page }) => {
  const loginPage = new LoginPage(page);
  const accountPage = new AccountPage(page);

  await loginPage.signInWithMfa(credentials);
  await accountPage.goto();
  await accountPage.updateBanking(bankingDetails);
  await accountPage.updatePayment(paymentDetails);
});
