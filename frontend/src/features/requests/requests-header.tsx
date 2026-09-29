"use client";

import { Plus } from "lucide-react";
import { ButtonLink } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { useUser } from "@/features/auth/auth-provider";

export function RequestsHeader() {
  const isManager = useUser().role === "manager";
  return isManager ? (
    <PageHeader title="Requests" description="Review and track equipment requests from your team." />
  ) : (
    <PageHeader
      title="My requests"
      description="Track the status of equipment you've asked for."
      actions={
        <ButtonLink href="/requests/new">
          <Plus className="size-4" aria-hidden />
          New request
        </ButtonLink>
      }
    />
  );
}
