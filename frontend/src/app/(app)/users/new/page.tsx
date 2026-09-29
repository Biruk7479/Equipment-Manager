import type { Metadata } from "next";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { RequireRole } from "@/features/auth/role-gates";
import { UserForm } from "@/features/users/user-form";

export const metadata: Metadata = { title: "Add user" };

export default function NewUserPage() {
  return (
    <RequireRole role="manager">
      <PageHeader
        title="Add user"
        description="Create an account for an employee or another manager."
        back={{ href: "/users", label: "Users" }}
      />
      <Panel className="max-w-2xl">
        <UserForm />
      </Panel>
    </RequireRole>
  );
}
