import type { Metadata } from "next";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { RequireRole } from "@/features/auth/role-gates";
import { EquipmentForm } from "@/features/equipment/equipment-form";

export const metadata: Metadata = { title: "Add equipment" };

export default function NewEquipmentPage() {
  return (
    <RequireRole role="manager">
      <PageHeader
        title="Add equipment"
        description="New items become available for employees to request."
        back={{ href: "/equipment", label: "Equipment" }}
      />
      <Panel className="max-w-2xl">
        <EquipmentForm />
      </Panel>
    </RequireRole>
  );
}
