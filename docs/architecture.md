# Architecture

## Overview

```text
TypeScript Playwright -> Challenge Site
Python API Client     -> REST API
```

The browser automation and API client solve the same account update workflow
through two different integration surfaces. They share test data conventions but
do not depend on each other.

## Project Structure

```text
browser-automation/
  pages/AccountPage.ts
  pages/LoginPage.ts
  selectors.ts
  test-data.ts
  tests/account-update.spec.ts

api-client/onsetto_client/
  auth.py
  account.py
  constants.py
  exceptions.py
  models.py
  settings.py
  transport.py
  validators.py
```

## Design Decisions

### Why Playwright

Playwright provides reliable auto-waiting, first-class TypeScript support,
browser traces, screenshots on failure, and readable assertions. Those qualities
matter more here than broad browser-driver portability.

### Why Page Object Model

The browser flow has a small but clear domain: login/MFA and account updates.
Page Objects keep selectors and repeatable actions in one place while keeping
the test readable.

### Why `httpx`

`httpx` gives explicit timeout support, connection reuse, clean testability via
`MockTransport`, and a future async path if the client grows. The implementation
uses the synchronous client because the assignment flow is sequential.

### Why dataclasses instead of Pydantic

The request and response shapes are small. Dataclasses keep the types explicit
without adding heavier runtime parsing. Validation is handled at the boundary by
focused validator functions.

### Why no Django

The prompt asks for a Python API client, not a server. Django would add routing,
settings, application lifecycle, and framework decisions unrelated to the
requested integration.

### Why retry only `429`

Rate limiting is transient and explicitly mentioned in the challenge. Credential
failures, MFA failures, validation errors, and malformed responses should fail
fast because retrying them is unlikely to succeed and can hide real defects.

## Future Improvements Intentionally Skipped

- Docker, because local install commands are enough for this submission.
- Poetry or uv, because standard `pip install -e ".[dev]"` keeps setup simple.
- Complex dependency injection, because `httpx.MockTransport` already gives
  testable boundaries.
- Live CI browser/API runs, because they mutate a shared sandbox account.
