export const loginSelectors = {
  email: "#email",
  password: "#password",
  signInButtonName: "Sign in",
  mfaHeadingName: "Verify your identity",
  mfaTextboxRole: "textbox",
  verifyButtonName: "Verify",
} as const;

export const accountSelectors = {
  bankRouting: "#bank-routing",
  bankAccount: "#bank-account",
  bankSave: "#bank-save",
  bankSavedInfo: "bank-saved-info",
  cardHolder: "#card-holder",
  cardNumber: "#card-number",
  cardExpMonth: "#card-exp-month",
  cardExpYear: "#card-exp-year",
  cardCvc: "#card-cvc",
  cardSave: "#card-save",
  paymentSavedInfo: "payment-saved-info",
} as const;
