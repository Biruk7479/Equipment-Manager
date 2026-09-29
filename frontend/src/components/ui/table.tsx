import { cn } from "@/lib/cn";

export function Table({ children }: { children: React.ReactNode }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left [&_tbody_tr:last-child_td]:border-0">{children}</table>
    </div>
  );
}

export function TH({ className, ...props }: React.ComponentProps<"th">) {
  return (
    <th
      className={cn(
        "border-b border-line px-4 py-2.5 text-[13px] font-medium whitespace-nowrap text-ink-muted",
        className,
      )}
      {...props}
    />
  );
}

export function TD({ className, ...props }: React.ComponentProps<"td">) {
  return <td className={cn("border-b border-line px-4 py-3 align-middle", className)} {...props} />;
}
