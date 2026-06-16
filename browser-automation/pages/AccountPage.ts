import { expect, type Page } from "@playwright/test";

import { accountSelectors } from "../selectors.js";
import type { BankingDetails, PaymentDetails } from "../test-data.js";

export class AccountPage {
  constructor(private readonly page: Page) {}

  async goto(): Promise<void> {
    await this.page.goto("/app/account");
    await expect(
      this.page.getByRole("heading", { name: "Account Settings" }),
    ).toBeVisible();
  }

  async updateBanking(details: BankingDetails): Promise<void> {
    await this.page
      .locator(accountSelectors.bankRouting)
      .fill(details.routingNumber);
    await this.page
      .locator(accountSelectors.bankAccount)
      .fill(details.accountNumber);
    await this.page.locator(accountSelectors.bankSave).click();

    const summary = this.page.getByTestId(accountSelectors.bankSavedInfo);
    await expect(summary).toBeVisible();
    await expect(summary).toContainText(details.routingNumber.slice(-4));
    await expect(summary).toContainText(details.accountNumber.slice(-4));
    await expect(summary).toContainText("Last updated:");
  }

  async updatePayment(details: PaymentDetails): Promise<void> {
    await this.page
      .locator(accountSelectors.cardHolder)
      .fill(details.cardholderName);
    await this.page
      .locator(accountSelectors.cardNumber)
      .fill(details.cardNumber);
    await this.page
      .locator(accountSelectors.cardExpMonth)
      .fill(details.expMonth);
    await this.page.locator(accountSelectors.cardExpYear).fill(details.expYear);
    await this.page.locator(accountSelectors.cardCvc).fill(details.cvc);
    await this.page.locator(accountSelectors.cardSave).click();

    const summary = this.page.getByTestId(accountSelectors.paymentSavedInfo);
    await expect(summary).toBeVisible();
    await expect(summary).toContainText(details.cardNumber.slice(-4));
    await expect(summary).toContainText(
      `Expires ${Number(details.expMonth)}/${details.expYear}`,
    );
    await expect(summary).toContainText("Last updated:");
  }
}
