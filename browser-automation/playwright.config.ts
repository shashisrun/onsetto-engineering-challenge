import { defineConfig, devices } from "@playwright/test";
import "dotenv/config";

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  retries: 0,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    actionTimeout: 10_000,
    baseURL:
      process.env.ONSETTO_CHALLENGE_URL ?? "https://challenge.onsetto.dev",
    navigationTimeout: 20_000,
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
