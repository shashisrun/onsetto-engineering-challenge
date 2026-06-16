# Onsetto Engineering Challenge

This repository contains a focused implementation of the Onsetto Engineering
Challenge:

- **Part 1:** TypeScript Playwright browser automation.
- **Part 2:** Typed Python API client using `httpx`.

The project intentionally favors readability and maintainability over broad
framework usage. The assignment scope is small, so the implementation avoids
Django, Docker, ADRs, and other ceremony that would add more surface area than
value.

## Repository Structure

```text
browser-automation/       TypeScript Playwright test, page objects, selectors
api-client/onsetto_client/ Typed Python API client package
tests/                    Python unit and mocked HTTP tests
docs/architecture.md      Architecture notes and trade-offs
.github/workflows/ci.yml  Minimal lint/type/test workflow
```

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

npm install
npx playwright install chromium
```

Optional local configuration:

```bash
cp .env.example .env
```

The checked-in defaults use only the sandbox account and fake test data.

## Browser Automation

```bash
npm run browser
```

The Playwright flow signs in, completes MFA, opens `/app/account`, updates
banking details, updates the payment method, and verifies the saved summaries.
Screenshots and traces are retained only on failure.

## Python API Client

```bash
python -m onsetto_client update-account
```

The client performs:

1. `POST /auth/token`
2. `POST /auth/mfa/verify`
3. `PUT /account/banking`
4. `PUT /account/payment`

Example output:

```text
INFO Authenticating...
INFO Verifying MFA...
SUCCESS MFA verified.
INFO Updating banking details.
SUCCESS Banking updated: routing=.....0021 account=......7890
INFO Updating payment method.
SUCCESS Payment updated: visa ending in 4242 exp=12/2028
```

Raw passwords, bearer tokens, account numbers, card numbers, and CVC values are
not logged.

## Environment Variables

| Variable                  | Purpose                        |
| ------------------------- | ------------------------------ |
| `ONSETTO_CHALLENGE_URL`   | Browser challenge site URL     |
| `ONSETTO_API_BASE_URL`    | REST API base URL              |
| `ONSETTO_EMAIL`           | Sandbox user email             |
| `ONSETTO_PASSWORD`        | Sandbox user password          |
| `ONSETTO_MFA_CODE`        | MFA code; defaults to `1234`   |
| `ONSETTO_BANK_ROUTING`    | 9-digit fake routing number    |
| `ONSETTO_BANK_ACCOUNT`    | 4-17 digit fake account number |
| `ONSETTO_CARDHOLDER_NAME` | Fake cardholder name           |
| `ONSETTO_CARD_NUMBER`     | Luhn-valid fake card number    |
| `ONSETTO_CARD_EXP_MONTH`  | Future expiry month            |
| `ONSETTO_CARD_EXP_YEAR`   | Future expiry year             |
| `ONSETTO_CARD_CVC`        | 3-4 digit fake CVC             |

## Tests And Quality Checks

```bash
pytest
ruff check
black --check .
mypy api-client tests
npm run lint
npm run typecheck
```

CI runs Python lint/typecheck/tests and TypeScript lint/typecheck. It does not
run live browser or API mutation flows because the sandbox account is shared.

## Trade-offs

- **No Django:** the assignment evaluates browser automation and API client
  integration, not service development. A small Python package is easier to
  review and better aligned with the requested scope.
- **Dataclasses over Pydantic:** the models are simple and are validated at the
  boundary. Runtime parsing features would not add enough value here.
- **Retry only `429`:** rate limits are transient and explicitly called out.
  Auth, MFA, validation, and malformed responses should fail fast.
- **Page Objects, but shallow:** page objects keep selectors and workflows
  reusable without hiding the test intent behind excessive abstraction.

## Engineering Process

LLM assistance was used to accelerate repetitive implementation work. Architecture
choices, scope control, validation strategy, review, testing, and final
verification were owned and checked manually. The final code is intentionally
small enough for a reviewer to understand quickly.
