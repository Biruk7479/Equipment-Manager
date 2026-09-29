"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/feedback";
import { Field, Input } from "@/components/ui/form";
import { setServerErrors } from "@/lib/forms";
import { useLogin } from "./api";
import { nextPath } from "./next-path";
import { loginSchema, type LoginValues } from "./schemas";

export function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const login = useLogin();
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) });

  const onSubmit = handleSubmit((values) =>
    login.mutate(values, {
      onSuccess: () => router.replace(nextPath(params.get("next"))),
      onError: (error) => setServerErrors(error, setError, ["email", "password"]),
    }),
  );

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-4">
      {errors.root?.message && <ErrorMessage message={errors.root.message} />}
      <Field label="Email" htmlFor="email" error={errors.email?.message}>
        <Input
          id="email"
          type="email"
          autoComplete="email"
          aria-invalid={!!errors.email}
          {...register("email")}
        />
      </Field>
      <Field label="Password" htmlFor="password" error={errors.password?.message}>
        <Input
          id="password"
          type="password"
          autoComplete="current-password"
          aria-invalid={!!errors.password}
          {...register("password")}
        />
      </Field>
      <Button type="submit" className="w-full" loading={login.isPending}>
        Sign in
      </Button>
    </form>
  );
}
