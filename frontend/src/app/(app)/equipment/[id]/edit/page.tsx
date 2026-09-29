import type { Metadata } from "next";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { RequireRole } from "@/features/auth/role-gates";
import { EditEquipment } from "@/features/equipment/edit-equipment";

export const metadata: Metadata = { title: "Edit equipment" };

export default async function EditEquipmentPage({ params }: PageProps<"/equipment/[id]/edit">) {
  const { id } = await params;
  return (
    <RequireRole role="manager">
      <PageHeader title="Edit equipment" back={{ href: "/equipment", label: "Equipment" }} />
      <Panel className="max-w-2xl">
        <EditEquipment id={Number(id)} />
      </Panel>
    </RequireRole>
  );
}
