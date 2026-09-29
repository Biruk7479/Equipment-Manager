import { Plus } from "lucide-react";
import type { Metadata } from "next";
import { ButtonLink } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { RoleOnly } from "@/features/auth/role-gates";
import { DashboardView } from "@/features/dashboard/dashboard-view";

export const metadata: Metadata = { title: "Dashboard" };

export default function DashboardPage() {
  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Stock levels and request activity at a glance."
        actions={
          <RoleOnly role="employee">
            <ButtonLink href="/requests/new">
              <Plus className="size-4" aria-hidden />
              Request equipment
            </ButtonLink>
          </RoleOnly>
        }
      />
      <DashboardView />
    </>
  );
}
