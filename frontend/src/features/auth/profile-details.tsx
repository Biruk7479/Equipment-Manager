"use client";

import { formatDate } from "@/lib/format";
import { ROLE_LABELS } from "@/lib/labels";
import { useUser } from "./auth-provider";

export function ProfileDetails() {
  const user = useUser();
  const rows = [
    ["Name", user.full_name],
    ["Email", user.email],
    ["Role", ROLE_LABELS[user.role]],
    ["Member since", formatDate(user.created_at)],
  ];

  return (
    <dl className="divide-y divide-line">
      {rows.map(([label, value]) => (
        <div key={label} className="grid grid-cols-3 gap-4 px-5 py-3">
          <dt className="text-ink-muted">{label}</dt>
          <dd className="col-span-2 break-words">{value}</dd>
        </div>
      ))}
    </dl>
  );
}
