"use client";

import { CircleCheck, CircleX, Clock3 } from "lucide-react";
import { ErrorMessage, Loading } from "@/components/ui/feedback";
import { useUser } from "@/features/auth/auth-provider";
import { errorMessage } from "@/lib/api";
import { useDashboard } from "./api";
import { CategoryBreakdown } from "./category-breakdown";
import { StatTile } from "./stat-tile";

export function DashboardView() {
  const isManager = useUser().role === "manager";
  const { data, error } = useDashboard();

  if (error) return <ErrorMessage message={errorMessage(error)} />;
  if (!data) return <Loading />;

  return (
    <div className="space-y-8">
      <section aria-labelledby="stock-heading">
        <h2 id="stock-heading" className="mb-3 text-[13px] font-medium text-ink-muted">
          Equipment
        </h2>
        <div className="grid grid-cols-2 gap-3">
          <StatTile label="Equipment items" value={data.total_equipment} href="/equipment" />
          <StatTile
            label="Units available"
            value={data.total_available_quantity}
            href="/equipment?available=true"
          />
        </div>
      </section>

      <section aria-labelledby="requests-heading">
        <h2 id="requests-heading" className="mb-3 text-[13px] font-medium text-ink-muted">
          {isManager ? "All requests" : "My requests"}
        </h2>
        <div className="grid grid-cols-3 gap-3">
          <StatTile
            label="Pending"
            value={data.requests.pending}
            href="/requests?status=pending"
            icon={<Clock3 className="size-4 text-pending" aria-hidden />}
          />
          <StatTile
            label="Approved"
            value={data.requests.approved}
            href="/requests?status=approved"
            icon={<CircleCheck className="size-4 text-approved" aria-hidden />}
          />
          <StatTile
            label="Rejected"
            value={data.requests.rejected}
            href="/requests?status=rejected"
            icon={<CircleX className="size-4 text-rejected" aria-hidden />}
          />
        </div>
      </section>

      <CategoryBreakdown rows={data.requests_by_category} />
    </div>
  );
}
