"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/feedback";
import { Field, Input } from "@/components/ui/form";
import { setServerErrors } from "@/lib/forms";
import { useRegister } from "./api";
import { registerSchema, type RegisterValues } from "./schemas";

export function RegisterForm() {
  const router = useRouter();
  const registerUser = useRegister();
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<RegisterValues>({ resolver: zodResolver(registerSchema) });

  const onSubmit = handleSubmit((values) =>
    registerUser.mutate(values, {
      onSuccess: () => router.replace("/dashboard"),
      onError: (error) =>
        setServerErrors(error, setError, ["full_name", "email", "password"], {
          email_taken: "email",
        }),
    }),
  );

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-4">
      {errors.root?.message && <ErrorMessage message={errors.root.message} />}
      <Field label="Full name" htmlFor="full_name" error={errors.full_name?.message}>
        <Input
          id="full_name"
          autoComplete="name"
          aria-invalid={!!errors.full_name}
          {...register("full_name")}
        />
      </Field>
      <Field label="Work email" htmlFor="email" error={errors.email?.message}>
        <Input
          id="email"
          type="email"
          autoComplete="email"
          aria-invalid={!!errors.email}
          {...register("email")}
        />
      </Field>
      <Field
        label="Password"
        htmlFor="password"
        error={errors.password?.message}
        hint="At least 8 characters."
      >
        <Input
          id="password"
          type="password"
          autoComplete="new-password"
          aria-invalid={!!errors.password}
          {...register("password")}
        />
      </Field>
      <Button type="submit" className="w-full" loading={registerUser.isPending}>
        Create account
      </Button>
    </form>
  );
}
