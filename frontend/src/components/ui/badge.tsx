import { cn } from "@/lib/cn";

const tones = {
  neutral: "bg-subtle text-ink-muted",
  accent: "bg-accent-soft text-accent",
  pending: "bg-pending-soft text-pending",
  approved: "bg-approved-soft text-approved",
  rejected: "bg-rejected-soft text-rejected",
};

export type BadgeTone = keyof typeof tones;

export function Badge({
  tone = "neutral",
  className,
  ...props
}: React.ComponentProps<"span"> & { tone?: BadgeTone }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium whitespace-nowrap",
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}
