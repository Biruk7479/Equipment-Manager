import { CircleAlert } from "lucide-react";

export function Loading({ label = "Loading…" }: { label?: string }) {
  return <p className="px-4 py-12 text-center text-ink-muted">{label}</p>;
}

type EmptyStateProps = {
  title: string;
  description?: string;
  action?: React.ReactNode;
};

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="px-6 py-14 text-center">
      <p className="font-medium">{title}</p>
      {description && <p className="mt-1 text-ink-muted">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function ErrorMessage({ message }: { message: string }) {
  return (
    <div
      role="alert"
      className="flex gap-2 rounded-md border border-danger/20 bg-danger-soft px-3 py-2.5 text-[13px] text-danger"
    >
      <CircleAlert className="mt-px size-4 shrink-0" aria-hidden />
      <p>{message}</p>
    </div>
  );
}
