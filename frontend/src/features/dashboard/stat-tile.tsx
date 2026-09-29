import Link from "next/link";
import { cn } from "@/lib/cn";
import { formatNumber } from "@/lib/format";

type StatTileProps = {
  label: string;
  value: number;
  href?: string;
  icon?: React.ReactNode;
};

export function StatTile({ label, value, href, icon }: StatTileProps) {
  const className = "block rounded-lg border border-line bg-surface p-3 sm:p-4";
  const content = (
    <>
      <p className="flex items-center gap-1.5 text-[13px] text-ink-muted">
        {icon}
        {label}
      </p>
      <p className="mt-2 text-xl font-semibold tracking-tight sm:text-2xl">{formatNumber(value)}</p>
    </>
  );

  return href ? (
    <Link href={href} className={cn(className, "transition-colors hover:border-line-strong")}>
      {content}
    </Link>
  ) : (
    <div className={className}>{content}</div>
  );
}
