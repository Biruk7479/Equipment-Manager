"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { Button, ButtonLink } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/feedback";
import { Field, Input, Select, Textarea } from "@/components/ui/form";
import { setServerErrors } from "@/lib/forms";
import { CATEGORIES, CATEGORY_LABELS } from "@/lib/labels";
import type { Equipment } from "@/lib/types";
import { useSaveEquipment } from "./api";
import { equipmentSchema, type EquipmentValues } from "./schemas";

export function EquipmentForm({ equipment }: { equipment?: Equipment }) {
  const router = useRouter();
  const save = useSaveEquipment(equipment?.id);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<EquipmentValues>({
    resolver: zodResolver(equipmentSchema),
    defaultValues: {
      name: equipment?.name ?? "",
      category: equipment?.category,
      available_quantity: equipment?.available_quantity ?? 0,
      description: equipment?.description ?? "",
    },
  });

  const onSubmit = handleSubmit((values) =>
    save.mutate(
      { ...values, description: values.description || null },
      {
        onSuccess: () => router.push("/equipment"),
        onError: (error) =>
          setServerErrors(
            error,
            setError,
            ["name", "category", "available_quantity", "description"],
            { equipment_name_taken: "name" },
          ),
      },
    ),
  );

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-5 p-5 sm:p-6">
      {errors.root?.message && <ErrorMessage message={errors.root.message} />}
      <Field label="Name" htmlFor="name" error={errors.name?.message}>
        <Input id="name" aria-invalid={!!errors.name} {...register("name")} />
      </Field>
      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="Category" htmlFor="category" error={errors.category?.message}>
          <Select id="category" aria-invalid={!!errors.category} {...register("category")}>
            <option value="">Select a category</option>
            {CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {CATEGORY_LABELS[category]}
              </option>
            ))}
          </Select>
        </Field>
        <Field
          label="Available quantity"
          htmlFor="available_quantity"
          error={errors.available_quantity?.message}
        >
          <Input
            id="available_quantity"
            type="number"
            min={0}
            step={1}
            inputMode="numeric"
            aria-invalid={!!errors.available_quantity}
            {...register("available_quantity", { valueAsNumber: true })}
          />
        </Field>
      </div>
      <Field
        label="Description"
        htmlFor="description"
        error={errors.description?.message}
        hint="Optional. Model, specs or anything employees should know."
      >
        <Textarea id="description" rows={4} {...register("description")} />
      </Field>
      <div className="flex gap-2 border-t border-line pt-5">
        <Button type="submit" loading={save.isPending}>
          {equipment ? "Save changes" : "Add equipment"}
        </Button>
        <ButtonLink href="/equipment" variant="secondary">
          Cancel
        </ButtonLink>
      </div>
    </form>
  );
}
