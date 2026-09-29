"use client";

import { ErrorMessage, Loading } from "@/components/ui/feedback";
import { PageHeader } from "@/components/ui/page-header";
import { Panel } from "@/components/ui/panel";
import { useUser } from "@/features/auth/auth-provider";
import { errorMessage } from "@/lib/api";
import { cn } from "@/lib/cn";
import { formatDateTime, formatNumber } from "@/lib/format";
import { CATEGORY_LABELS } from "@/lib/labels";
import { useRequest } from "./api";
import { HistoryTimeline } from "./history-timeline";
import { ReviewPanel } from "./review-panel";
import { StatusBadge } from "./status-badge";

function DetailRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="grid gap-1 px-5 py-3 sm:grid-cols-3 sm:gap-4">
      <dt className="text-ink-muted">{label}</dt>
      <dd className="break-words sm:col-span-2">{children}</dd>
    </div>
  );
}

export function RequestDetail({ id }: { id: number }) {
  const isManager = useUser().role === "manager";
  const { data: request, error } = useRequest(id);
  const back = { href: "/requests", label: isManager ? "Requests" : "My requests" };

  if (error) {
    return (
      <>
        <PageHeader title="Request" back={back} />
        <ErrorMessage message={errorMessage(error)} />
      </>
    );
  }
  if (!request) return <Loading />;

  const canReview = isManager && request.status === "pending";

  return (
    <>
      <PageHeader
        title={`Request #${request.id}`}
        back={back}
        actions={<StatusBadge status={request.status} />}
      />
      <div
        className={cn("grid items-start gap-6", canReview && "lg:grid-cols-[minmax(0,1fr)_340px]")}
      >
        <div className="space-y-6">
          <Panel title="Details">
            <dl className="divide-y divide-line">
              <DetailRow label="Equipment">
                {request.equipment.name}
                <span className="text-ink-muted">
                  {" · "}
                  {CATEGORY_LABELS[request.equipment.category]}
                </span>
              </DetailRow>
              <DetailRow label="Quantity">{formatNumber(request.quantity)}</DetailRow>
              <DetailRow label="Requested by">
                {request.requester.full_name}
                <span className="block text-[13px] text-ink-muted">{request.requester.email}</span>
              </DetailRow>
              <DetailRow label="Submitted">{formatDateTime(request.created_at)}</DetailRow>
              <DetailRow label="Justification">
                <span className="whitespace-pre-wrap">{request.justification}</span>
              </DetailRow>
              {request.reviewer && request.reviewed_at && (
                <>
                  <DetailRow label="Reviewed by">{request.reviewer.full_name}</DetailRow>
                  <DetailRow label="Reviewed on">{formatDateTime(request.reviewed_at)}</DetailRow>
                  {request.review_comment && (
                    <DetailRow label="Manager comment">
                      <span className="whitespace-pre-wrap">{request.review_comment}</span>
                    </DetailRow>
                  )}
                </>
              )}
            </dl>
          </Panel>
          <Panel title="History" description="Every status change is recorded and cannot be edited.">
            <HistoryTimeline requestId={request.id} />
          </Panel>
        </div>
        {canReview && <ReviewPanel request={request} />}
      </div>
    </>
  );
}
