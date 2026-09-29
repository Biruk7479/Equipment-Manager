"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm, useWatch } from "react-hook-form";
import { Button, ButtonLink } from "@/components/ui/button";
import { ErrorMessage, Loading } from "@/components/ui/feedback";
import { Field, Input, Select, Textarea } from "@/components/ui/form";
import { useEquipmentOptions } from "@/features/equipment/api";
import { errorMessage } from "@/lib/api";
import { setServerErrors } from "@/lib/forms";
import { formatNumber } from "@/lib/format";
import type { Equipment } from "@/lib/types";
import { useCreateRequest } from "./api";
import { requestSchema, type RequestValues } from "./schemas";

export function RequestForm() {
  const equipment = useEquipmentOptions();

  if (equipment.error) {
    return (
      <div className="p-5">
        <ErrorMessage message={errorMessage(equipment.error)} />
      </div>
    );
  }
  return equipment.data ? <RequestFields equipment={equipment.data} /> : <Loading />;
}

function RequestFields({ equipment }: { equipment: Equipment[] }) {
  const router = useRouter();
  const params = useSearchParams();
  const createRequest = useCreateRequest();
  const {
    register,
    handleSubmit,
    setError,
    control,
    formState: { errors },
  } = useForm<RequestValues>({
    resolver: zodResolver(requestSchema),
    defaultValues: {
      equipment_id: Number(params.get("equipment")) || undefined,
      quantity: 1,
      justification: "",
    },
  });

  const equipmentId = useWatch({ control, name: "equipment_id" });
  const selected = equipment.find((item) => item.id === equipmentId);

  const onSubmit = handleSubmit((values) =>
    createRequest.mutate(values, {
      onSuccess: (request) => router.push(`/requests/${request.id}`),
      onError: (error) =>
        setServerErrors(error, setError, ["equipment_id", "quantity", "justification"], {
          duplicate_pending_request: "equipment_id",
          not_found: "equipment_id",
        }),
    }),
  );

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-5 p-5 sm:p-6">
      {errors.root?.message && <ErrorMessage message={errors.root.message} />}
      <Field label="Equipment" htmlFor="equipment_id" error={errors.equipment_id?.message}>
        <Select
          id="equipment_id"
          aria-invalid={!!errors.equipment_id}
          {...register("equipment_id", { valueAsNumber: true })}
        >
          <option value="">Select equipment</option>
          {equipment.map((item) => (
            <option key={item.id} value={item.id} disabled={item.available_quantity === 0}>
              {item.name}
              {item.available_quantity === 0 ? " (out of stock)" : ""}
            </option>
          ))}
        </Select>
      </Field>
      <Field
        label="Quantity"
        htmlFor="quantity"
        error={errors.quantity?.message}
        hint={selected && `${formatNumber(selected.available_quantity)} currently available.`}
      >
        <Input
          id="quantity"
          type="number"
          min={1}
          step={1}
          inputMode="numeric"
          className="sm:w-40"
          aria-invalid={!!errors.quantity}
          {...register("quantity", { valueAsNumber: true })}
        />
      </Field>
      <Field
        label="Justification"
        htmlFor="justification"
        error={errors.justification?.message}
        hint="Tell your manager what you need it for."
      >
        <Textarea
          id="justification"
          rows={5}
          aria-invalid={!!errors.justification}
          {...register("justification")}
        />
      </Field>
      <div className="flex gap-2 border-t border-line pt-5">
        <Button type="submit" loading={createRequest.isPending}>
          Submit request
        </Button>
        <ButtonLink href="/requests" variant="secondary">
          Cancel
        </ButtonLink>
      </div>
    </form>
  );
}
