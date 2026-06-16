import { expect, type Page } from "@playwright/test";

import { appSelectors, loginSelectors } from "../selectors.js";
import type { ChallengeCredentials } from "../test-data.js";

export class LoginPage {
  constructor(private readonly page: Page) {}

  async signInWithMfa(credentials: ChallengeCredentials): Promise<void> {
    await this.page.goto("/login");
    await this.page.locator(loginSelectors.email).fill(credentials.email);
    await this.page.locator(loginSelectors.password).fill(credentials.password);
    await this.page
      .getByRole("button", { name: loginSelectors.signInButtonName })
      .click();

    await expect(
      this.page.getByRole("heading", { name: loginSelectors.mfaHeadingName }),
    ).toBeVisible();

    await this.page
      .getByRole(loginSelectors.mfaTextboxRole)
      .fill(credentials.mfaCode);
    await this.page
      .getByRole("button", { name: loginSelectors.verifyButtonName })
      .click();
    await expect(
      this.page.getByRole("heading", {
        name: appSelectors.marketplaceHeadingName,
      }),
    ).toBeVisible();
  }
}
