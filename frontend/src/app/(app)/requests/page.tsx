import type { Metadata } from "next";
import { Suspense } from "react";
import { RequestList } from "@/features/requests/request-list";
import { RequestsHeader } from "@/features/requests/requests-header";

export const metadata: Metadata = { title: "Requests" };

export default function RequestsPage() {
  return (
    <>
      <RequestsHeader />
      <Suspense>
        <RequestList />
      </Suspense>
    </>
  );
}
