from __future__ import annotations

import argparse
import logging

from onsetto_client.account import AccountClient
from onsetto_client.auth import AuthClient
from onsetto_client.exceptions import OnsettoAPIError, ValidationError
from onsetto_client.models import BankingRequest, PaymentRequest
from onsetto_client.settings import Settings
from onsetto_client.transport import APITransport

SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
logging.addLevelName(logging.WARNING, "WARN")


def _success(self: logging.Logger, message: str, *args: object) -> None:
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args)


logging.Logger.success = _success  # type: ignore[attr-defined]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(verbose=args.verbose)

    if args.command == "update-account":
        return update_account(args)

    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m onsetto_client",
        description="Update Onsetto challenge banking and payment details.",
    )
    parser.add_argument("--verbose", action="store_true", help="show debug logs")

    subcommands = parser.add_subparsers(dest="command")
    update = subcommands.add_parser(
        "update-account",
        help="authenticate and update banking/payment details",
    )
    update.add_argument("--email")
    update.add_argument("--password")
    update.add_argument("--mfa-code")
    update.add_argument("--base-url")
    update.add_argument("--routing-number")
    update.add_argument("--account-number")
    update.add_argument("--cardholder-name")
    update.add_argument("--card-number")
    update.add_argument("--exp-month", type=int)
    update.add_argument("--exp-year", type=int)
    update.add_argument("--cvc")

    return parser


def configure_logging(*, verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )
    if not verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)


def update_account(args: argparse.Namespace) -> int:
    logger = logging.getLogger("onsetto_client")
    settings = Settings.from_env()

    email = args.email or settings.email
    password = args.password or settings.password
    mfa_code = args.mfa_code or settings.mfa_code
    base_url = args.base_url or settings.api_base_url

    banking = BankingRequest(
        routing_number=args.routing_number or settings.banking.routing_number,
        account_number=args.account_number or settings.banking.account_number,
    )
    payment = PaymentRequest(
        cardholder_name=args.cardholder_name or settings.payment.cardholder_name,
        card_number=args.card_number or settings.payment.card_number,
        exp_month=args.exp_month or settings.payment.exp_month,
        exp_year=args.exp_year or settings.payment.exp_year,
        cvc=args.cvc or settings.payment.cvc,
    )

    transport = APITransport(base_url=base_url, logger=logger)
    auth_client = AuthClient(transport)
    account_client = AccountClient(transport)

    try:
        logger.info("Authenticating...")
        challenge = auth_client.request_mfa(email, password)

        logger.info("Verifying MFA...")
        token = auth_client.verify_mfa(challenge.mfa_token, mfa_code)
        logger.success("MFA verified.")  # type: ignore[attr-defined]

        logger.info("Updating banking details.")
        banking_confirmation = account_client.update_banking(
            banking,
            access_token=token.access_token,
        )
        logger.success(  # type: ignore[attr-defined]
            "Banking updated: routing=%s account=%s",
            banking_confirmation.routing_masked,
            banking_confirmation.account_masked,
        )

        logger.info("Updating payment method.")
        payment_confirmation = account_client.update_payment(
            payment,
            access_token=token.access_token,
        )
        logger.success(  # type: ignore[attr-defined]
            "Payment updated: %s ending in %s exp=%02d/%d",
            payment_confirmation.card_brand,
            payment_confirmation.last4,
            payment_confirmation.exp_month,
            payment_confirmation.exp_year,
        )
        return 0
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        return 2
    except OnsettoAPIError as exc:
        logger.error("API request failed: %s", exc)
        return 1
    finally:
        transport.close()
