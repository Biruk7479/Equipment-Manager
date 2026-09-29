"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { CircleCheck } from "lucide-react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/feedback";
import { Field, Input } from "@/components/ui/form";
import { setServerErrors } from "@/lib/forms";
import { useChangePassword } from "./api";
import { changePasswordSchema, type ChangePasswordValues } from "./schemas";

export function ChangePasswordForm() {
  const changePassword = useChangePassword();
  const {
    register,
    handleSubmit,
    setError,
    reset,
    formState: { errors },
  } = useForm<ChangePasswordValues>({ resolver: zodResolver(changePasswordSchema) });

  const onSubmit = handleSubmit((values) =>
    changePassword.mutate(values, {
      onSuccess: () => reset(),
      onError: (error) =>
        setServerErrors(error, setError, ["current_password", "new_password"]),
    }),
  );

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-4 p-5">
      {errors.root?.message && <ErrorMessage message={errors.root.message} />}
      {changePassword.isSuccess && (
        <p
          role="status"
          className="flex gap-2 rounded-md bg-approved-soft px-3 py-2.5 text-[13px] text-approved"
        >
          <CircleCheck className="mt-px size-4 shrink-0" aria-hidden />
          Password updated. Your other sessions have been signed out.
        </p>
      )}
      <Field
        label="Current password"
        htmlFor="current_password"
        error={errors.current_password?.message}
      >
        <Input
          id="current_password"
          type="password"
          autoComplete="current-password"
          aria-invalid={!!errors.current_password}
          {...register("current_password")}
        />
      </Field>
      <Field
        label="New password"
        htmlFor="new_password"
        error={errors.new_password?.message}
        hint="At least 8 characters."
      >
        <Input
          id="new_password"
          type="password"
          autoComplete="new-password"
          aria-invalid={!!errors.new_password}
          {...register("new_password")}
        />
      </Field>
      <Field
        label="Confirm new password"
        htmlFor="confirm_password"
        error={errors.confirm_password?.message}
      >
        <Input
          id="confirm_password"
          type="password"
          autoComplete="new-password"
          aria-invalid={!!errors.confirm_password}
          {...register("confirm_password")}
        />
      </Field>
      <Button type="submit" loading={changePassword.isPending}>
        Update password
      </Button>
    </form>
  );
}
