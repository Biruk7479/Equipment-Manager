import type { Metadata } from "next";
import { Suspense } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { RequireRole } from "@/features/auth/role-gates";
import { RequestForm } from "@/features/requests/request-form";

export const metadata: Metadata = { title: "New request" };

export default function NewRequestPage() {
  return (
    <RequireRole role="employee">
      <PageHeader
        title="Request equipment"
        description="Your manager will review the request and approve it if stock allows."
        back={{ href: "/requests", label: "My requests" }}
      />
      <Panel className="max-w-2xl">
        <Suspense>
          <RequestForm />
        </Suspense>
      </Panel>
    </RequireRole>
  );
}
