import { CircleCheck, CircleX, Clock3 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { STATUS_LABELS } from "@/lib/labels";
import type { RequestStatus } from "@/lib/types";

const icons = { pending: Clock3, approved: CircleCheck, rejected: CircleX };

export function StatusBadge({ status }: { status: RequestStatus }) {
  const Icon = icons[status];
  return (
    <Badge tone={status}>
      <Icon className="size-3.5" aria-hidden />
      {STATUS_LABELS[status]}
    </Badge>
  );
}
