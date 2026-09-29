"use client";

import { ErrorMessage, Loading } from "@/components/ui/feedback";
import { errorMessage } from "@/lib/api";
import { useEquipment } from "./api";
import { EquipmentForm } from "./equipment-form";

export function EditEquipment({ id }: { id: number }) {
  const { data, error } = useEquipment(id);

  if (error) {
    return (
      <div className="p-5">
        <ErrorMessage message={errorMessage(error)} />
      </div>
    );
  }
  return data ? <EquipmentForm equipment={data} /> : <Loading />;
}
