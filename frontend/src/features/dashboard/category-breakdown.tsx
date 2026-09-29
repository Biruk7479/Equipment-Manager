"use client";

import { useState } from "react";
import { Table, TD, TH } from "@/components/ui/table";
import { cn } from "@/lib/cn";
import { formatNumber } from "@/lib/format";
import { CATEGORY_LABELS } from "@/lib/labels";
import type { Dashboard, RequestStatus } from "@/lib/types";

type Row = Dashboard["requests_by_category"][number];

const SERIES: Array<{ key: RequestStatus; label: string; mark: string }> = [
  { key: "approved", label: "Approved", mark: "bg-approved-mark" },
  { key: "pending", label: "Pending", mark: "bg-pending-mark" },
  { key: "rejected", label: "Rejected", mark: "bg-rejected-mark" },
];

const total = (row: Row) => row.pending + row.approved + row.rejected;

export function CategoryBreakdown({ rows }: { rows: Row[] }) {
  const [view, setView] = useState<"chart" | "table">("chart");

  return (
    <section className="rounded-lg border border-line bg-surface">
      <header className="flex flex-wrap items-start justify-between gap-3 border-b border-line px-5 py-4">
        <div>
          <h2 className="text-[15px] font-semibold">Requests by category</h2>
          <p className="mt-0.5 text-[13px] text-ink-muted">Number of requests per status.</p>
        </div>
        <div
          role="group"
          aria-label="Display as"
          className="inline-flex rounded-md border border-line-strong p-0.5"
        >
          {(["chart", "table"] as const).map((option) => (
            <button
              key={option}
              type="button"
              aria-pressed={view === option}
              onClick={() => setView(option)}
              className={cn(
                "rounded px-2.5 py-1 text-[13px] font-medium capitalize",
                view === option ? "bg-subtle text-ink" : "text-ink-muted hover:text-ink",
              )}
            >
              {option}
            </button>
          ))}
        </div>
      </header>
      {view === "chart" ? <Chart rows={rows} /> : <BreakdownTable rows={rows} />}
    </section>
  );
}

function Chart({ rows }: { rows: Row[] }) {
  const max = Math.max(1, ...rows.map(total));

  return (
    <div className="p-5">
      <ul className="mb-5 flex flex-wrap gap-x-4 gap-y-1 text-[13px] text-ink-muted" aria-label="Legend">
        {SERIES.map((series) => (
          <li key={series.key} className="flex items-center gap-1.5">
            <span className={cn("size-2.5 rounded-[2px]", series.mark)} aria-hidden />
            {series.label}
          </li>
        ))}
      </ul>
      <ul className="space-y-3.5">
        {rows.map((row) => {
          const segments = SERIES.filter((series) => row[series.key] > 0);
          return (
            <li
              key={row.category}
              className="grid grid-cols-[92px_minmax(0,1fr)] items-center gap-3 sm:grid-cols-[120px_minmax(0,1fr)]"
            >
              <span className="truncate text-ink-muted">{CATEGORY_LABELS[row.category]}</span>
              <div className="flex items-center gap-2">
                <div
                  className="flex h-4 gap-[2px]"
                  style={{ width: `calc((100% - 2.5rem) * ${total(row) / max})` }}
                >
                  {segments.map((series, index) => (
                    <span
                      key={series.key}
                      tabIndex={0}
                      aria-label={`${CATEGORY_LABELS[row.category]}: ${row[series.key]} ${series.label.toLowerCase()}`}
                      className={cn(
                        "group relative min-w-[3px] outline-offset-1 hover:brightness-110",
                        series.mark,
                        index === segments.length - 1 && "rounded-r-[4px]",
                      )}
                      style={{ flex: `${row[series.key]} 1 0` }}
                    >
                      <span
                        role="tooltip"
                        className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 hidden -translate-x-1/2 items-center gap-2 rounded-md bg-ink px-2.5 py-1.5 text-xs whitespace-nowrap text-white group-hover:flex group-focus-visible:flex"
                      >
                        <span className={cn("h-0.5 w-3 rounded-full", series.mark)} aria-hidden />
                        <strong className="font-semibold">{formatNumber(row[series.key])}</strong>
                        <span className="text-white/75">{series.label.toLowerCase()}</span>
                      </span>
                    </span>
                  ))}
                </div>
                <span className="text-[13px] text-ink-muted tabular-nums">
                  {formatNumber(total(row))}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function BreakdownTable({ rows }: { rows: Row[] }) {
  return (
    <Table>
      <thead>
        <tr>
          <TH>Category</TH>
          {SERIES.map((series) => (
            <TH key={series.key} className="text-right">
              {series.label}
            </TH>
          ))}
          <TH className="text-right">Total</TH>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.category}>
            <TD>{CATEGORY_LABELS[row.category]}</TD>
            {SERIES.map((series) => (
              <TD key={series.key} className="text-right tabular-nums">
                {formatNumber(row[series.key])}
              </TD>
            ))}
            <TD className="text-right font-medium tabular-nums">{formatNumber(total(row))}</TD>
          </tr>
        ))}
      </tbody>
    </Table>
  );
}
