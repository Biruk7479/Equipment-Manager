"use client";

import { ButtonLink } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/feedback";
import { Panel } from "@/components/ui/panel";
import type { Role } from "@/lib/types";
import { useUser } from "./auth-provider";

export function RoleOnly({ role, children }: { role: Role; children: React.ReactNode }) {
  return useUser().role === role ? children : null;
}

export function RequireRole({ role, children }: { role: Role; children: React.ReactNode }) {
  if (useUser().role === role) return children;
  return (
    <Panel>
      <EmptyState
        title="You don't have access to this page"
        description={`This section is only available to ${role}s.`}
        action={
          <ButtonLink href="/dashboard" variant="secondary">
            Back to dashboard
          </ButtonLink>
        }
      />
    </Panel>
  );
}
