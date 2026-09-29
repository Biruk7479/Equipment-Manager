import { cn } from "@/lib/cn";

type PanelProps = {
  title?: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
};

export function Panel({ title, description, actions, className, children }: PanelProps) {
  return (
    <section className={cn("rounded-lg border border-line bg-surface", className)}>
      {title && (
        <header className="flex items-start justify-between gap-4 border-b border-line px-5 py-4">
          <div>
            <h2 className="text-[15px] font-semibold">{title}</h2>
            {description && <p className="mt-0.5 text-[13px] text-ink-muted">{description}</p>}
          </div>
          {actions}
        </header>
      )}
      {children}
    </section>
  );
}
