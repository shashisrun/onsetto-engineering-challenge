import { expect, type Page } from "@playwright/test";

import { accountSelectors } from "../selectors.js";
import type { BankingDetails, PaymentDetails } from "../test-data.js";

export class AccountPage {
  constructor(private readonly page: Page) {}

  async goto(): Promise<void> {
    await this.page.goto("/app/account");
    await expect(
      this.page.getByRole("heading", {
        name: accountSelectors.accountHeadingName,
      }),
    ).toBeVisible();
  }

  async updateBanking(details: BankingDetails): Promise<void> {
    await this.page
      .getByTestId(accountSelectors.bankRouting)
      .fill(details.routingNumber);
    await this.page
      .getByTestId(accountSelectors.bankAccount)
      .fill(details.accountNumber);
    await this.page.getByTestId(accountSelectors.bankSave).click();

    const summary = this.page.getByTestId(accountSelectors.bankSavedInfo);
    await expect(summary).toBeVisible();
    await expect(summary).toContainText(details.routingNumber.slice(-4));
    await expect(summary).toContainText(details.accountNumber.slice(-4));
    await expect(summary).toContainText(accountSelectors.lastUpdatedLabel);
  }

  async updatePayment(details: PaymentDetails): Promise<void> {
    await this.page
      .getByTestId(accountSelectors.cardHolder)
      .fill(details.cardholderName);
    await this.page
      .getByTestId(accountSelectors.cardNumber)
      .fill(details.cardNumber);
    await this.page
      .getByTestId(accountSelectors.cardExpMonth)
      .fill(details.expMonth);
    await this.page
      .getByTestId(accountSelectors.cardExpYear)
      .fill(details.expYear);
    await this.page.getByTestId(accountSelectors.cardCvc).fill(details.cvc);
    await this.page.getByTestId(accountSelectors.cardSave).click();

    const summary = this.page.getByTestId(accountSelectors.paymentSavedInfo);
    await expect(summary).toBeVisible();
    await expect(summary).toContainText(details.cardNumber.slice(-4));
    await expect(summary).toContainText(
      `Expires ${Number(details.expMonth)}/${details.expYear}`,
    );
    await expect(summary).toContainText(accountSelectors.lastUpdatedLabel);
  }
}
