export function defaultExpiryYear(today = new Date()): string {
  return String(today.getFullYear() + 2);
}
