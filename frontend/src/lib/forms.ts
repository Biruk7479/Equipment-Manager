import type { FieldValues, Path, UseFormSetError } from "react-hook-form";
import { ApiError, errorMessage } from "./api";

export function setServerErrors<T extends FieldValues>(
  error: unknown,
  setError: UseFormSetError<T>,
  fields: ReadonlyArray<Path<T>>,
) {
  const unmatched: string[] = [];
  if (error instanceof ApiError && error.details) {
    for (const { field, message } of error.details) {
      if (fields.includes(field as Path<T>)) setError(field as Path<T>, { message });
      else unmatched.push(message);
    }
    if (unmatched.length === 0) return;
  }
  setError("root", { message: unmatched[0] ?? errorMessage(error) });
}
