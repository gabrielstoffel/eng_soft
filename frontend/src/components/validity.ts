import type { FormEvent } from "react";

type ValidatableElement = HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;

/**
 * Translate the browser's native constraint-validation bubble to Portuguese.
 * Wire as `onInvalid`; pair with `clearValidity` on `onInput` so the custom
 * message doesn't stick once the user fixes the field.
 */
export function localizeValidity(e: FormEvent<ValidatableElement>) {
  const el = e.currentTarget;
  if (el.validity.valueMissing) el.setCustomValidity("Por favor, preencha este campo.");
  else if (el.validity.typeMismatch) el.setCustomValidity("Por favor, insira um valor válido.");
  else el.setCustomValidity("");
}

export function clearValidity(e: FormEvent<ValidatableElement>) {
  e.currentTarget.setCustomValidity("");
}
