import { defaultExpiryYear } from "./utils/dates.js";

export type ChallengeCredentials = {
  email: string;
  password: string;
  mfaCode: string;
};

export type BankingDetails = {
  routingNumber: string;
  accountNumber: string;
};

export type PaymentDetails = {
  cardholderName: string;
  cardNumber: string;
  expMonth: string;
  expYear: string;
  cvc: string;
};

export const credentials: ChallengeCredentials = {
  email: process.env.ONSETTO_EMAIL ?? "candidate1@onsetto.test",
  password: process.env.ONSETTO_PASSWORD ?? "Password123!",
  mfaCode: process.env.ONSETTO_MFA_CODE ?? "1234",
};

export const bankingDetails: BankingDetails = {
  routingNumber: process.env.ONSETTO_BANK_ROUTING ?? "021000021",
  accountNumber: process.env.ONSETTO_BANK_ACCOUNT ?? "1234567890",
};

export const paymentDetails: PaymentDetails = {
  cardholderName: process.env.ONSETTO_CARDHOLDER_NAME ?? "Test User",
  cardNumber: process.env.ONSETTO_CARD_NUMBER ?? "4242424242424242",
  expMonth: process.env.ONSETTO_CARD_EXP_MONTH ?? "12",
  expYear: process.env.ONSETTO_CARD_EXP_YEAR ?? defaultExpiryYear(),
  cvc: process.env.ONSETTO_CARD_CVC ?? "123",
};
