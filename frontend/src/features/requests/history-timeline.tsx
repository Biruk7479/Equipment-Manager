"use client";

import { ErrorMessage, Loading } from "@/components/ui/feedback";
import { errorMessage } from "@/lib/api";
import { cn } from "@/lib/cn";
import { formatDateTime } from "@/lib/format";
import { STATUS_LABELS } from "@/lib/labels";
import { useRequestHistory } from "./api";

const markColors = {
  pending: "bg-pending-mark",
  approved: "bg-approved-mark",
  rejected: "bg-rejected-mark",
};

const actions = {
  pending: "submitted the request",
  approved: "approved the request",
  rejected: "rejected the request",
};

export function HistoryTimeline({ requestId }: { requestId: number }) {
  const { data, error } = useRequestHistory(requestId);

  if (error) {
    return (
      <div className="p-5">
        <ErrorMessage message={errorMessage(error)} />
      </div>
    );
  }
  if (!data) return <Loading />;

  return (
    <ol className="p-5">
      {data.map((entry, index) => (
        <li key={entry.id} className="relative flex gap-3 pb-6 last:pb-0">
          {index < data.length - 1 && (
            <span className="absolute top-4 bottom-0 left-[5px] w-px bg-line" aria-hidden />
          )}
          <span
            className={cn(
              "relative mt-1.5 size-[11px] shrink-0 rounded-full ring-4 ring-surface",
              markColors[entry.new_status],
            )}
            aria-hidden
          />
          <div className="min-w-0 flex-1">
            <p>
              <span className="font-medium">{entry.actor.full_name}</span>{" "}
              {actions[entry.new_status]}
            </p>
            <p className="mt-0.5 text-[13px] text-ink-muted">
              {entry.previous_status
                ? `${STATUS_LABELS[entry.previous_status]} → ${STATUS_LABELS[entry.new_status]}`
                : STATUS_LABELS[entry.new_status]}
              {" · "}
              <time dateTime={entry.created_at}>{formatDateTime(entry.created_at)}</time>
            </p>
            {entry.comment && (
              <p className="mt-2 rounded-md bg-canvas px-3 py-2 whitespace-pre-wrap">
                {entry.comment}
              </p>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
