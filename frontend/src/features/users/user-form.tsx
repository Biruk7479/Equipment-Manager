"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { Button, ButtonLink } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/feedback";
import { Field, Input, Select } from "@/components/ui/form";
import { setServerErrors } from "@/lib/forms";
import { useCreateUser } from "./api";
import { userSchema, type UserValues } from "./schemas";

export function UserForm() {
  const router = useRouter();
  const createUser = useCreateUser();
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<UserValues>({
    resolver: zodResolver(userSchema),
    defaultValues: { role: "employee" },
  });

  const onSubmit = handleSubmit((values) =>
    createUser.mutate(values, {
      onSuccess: () => router.push("/users"),
      onError: (error) =>
        setServerErrors(error, setError, ["full_name", "email", "password", "role"], {
          email_taken: "email",
        }),
    }),
  );

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-5 p-5 sm:p-6">
      {errors.root?.message && <ErrorMessage message={errors.root.message} />}
      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="Full name" htmlFor="full_name" error={errors.full_name?.message}>
          <Input id="full_name" aria-invalid={!!errors.full_name} {...register("full_name")} />
        </Field>
        <Field label="Role" htmlFor="role" error={errors.role?.message}>
          <Select id="role" aria-invalid={!!errors.role} {...register("role")}>
            <option value="employee">Employee</option>
            <option value="manager">Manager</option>
          </Select>
        </Field>
      </div>
      <Field label="Email" htmlFor="email" error={errors.email?.message}>
        <Input
          id="email"
          type="email"
          autoComplete="off"
          aria-invalid={!!errors.email}
          {...register("email")}
        />
      </Field>
      <Field
        label="Temporary password"
        htmlFor="password"
        error={errors.password?.message}
        hint="Share it securely. They can change it from their account page."
      >
        <Input
          id="password"
          type="password"
          autoComplete="new-password"
          aria-invalid={!!errors.password}
          {...register("password")}
        />
      </Field>
      <div className="flex gap-2 border-t border-line pt-5">
        <Button type="submit" loading={createUser.isPending}>
          Create account
        </Button>
        <ButtonLink href="/users" variant="secondary">
          Cancel
        </ButtonLink>
      </div>
    </form>
  );
}
