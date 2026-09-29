"use client";

import { ButtonLink } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/feedback";
import { Panel } from "@/components/ui/panel";
import { useUser } from "./auth-provider";

export function RequireManager({ children }: { children: React.ReactNode }) {
  const user = useUser();
  if (user.role === "manager") return children;
  return (
    <Panel>
      <EmptyState
        title="You don't have access to this page"
        description="Only managers can view this section."
        action={
          <ButtonLink href="/dashboard" variant="secondary">
            Back to dashboard
          </ButtonLink>
        }
      />
    </Panel>
  );
}
