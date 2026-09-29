import { Plus } from "lucide-react";
import type { Metadata } from "next";
import { Suspense } from "react";
import { ButtonLink } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { RequireRole } from "@/features/auth/role-gates";
import { UserList } from "@/features/users/user-list";

export const metadata: Metadata = { title: "Users" };

export default function UsersPage() {
  return (
    <RequireRole role="manager">
      <PageHeader
        title="Users"
        description="Everyone with access to equipment requests."
        actions={
          <ButtonLink href="/users/new">
            <Plus className="size-4" aria-hidden />
            Add user
          </ButtonLink>
        }
      />
      <Suspense>
        <UserList />
      </Suspense>
    </RequireRole>
  );
}
