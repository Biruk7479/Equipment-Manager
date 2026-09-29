import { Plus } from "lucide-react";
import type { Metadata } from "next";
import { Suspense } from "react";
import { ButtonLink } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { RoleOnly } from "@/features/auth/role-gates";
import { EquipmentList } from "@/features/equipment/equipment-list";

export const metadata: Metadata = { title: "Equipment" };

export default function EquipmentPage() {
  return (
    <>
      <PageHeader
        title="Equipment"
        description="Browse what's available and its current stock."
        actions={
          <RoleOnly role="manager">
            <ButtonLink href="/equipment/new">
              <Plus className="size-4" aria-hidden />
              Add equipment
            </ButtonLink>
          </RoleOnly>
        }
      />
      <Suspense>
        <EquipmentList />
      </Suspense>
    </>
  );
}
