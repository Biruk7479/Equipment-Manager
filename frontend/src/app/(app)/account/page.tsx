import type { Metadata } from "next";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { ChangePasswordForm } from "@/features/auth/change-password-form";
import { ProfileDetails } from "@/features/auth/profile-details";

export const metadata: Metadata = { title: "Account" };

export default function AccountPage() {
  return (
    <>
      <PageHeader title="Account" description="Your profile and sign-in settings." />
      <div className="grid items-start gap-6 lg:grid-cols-2">
        <Panel title="Profile">
          <ProfileDetails />
        </Panel>
        <Panel title="Change password" description="Other devices will be signed out.">
          <ChangePasswordForm />
        </Panel>
      </div>
    </>
  );
}
