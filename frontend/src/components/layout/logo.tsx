import { Boxes } from "lucide-react";

export function Logo() {
  return (
    <span className="inline-flex items-center gap-2.5">
      <span className="grid size-7 place-items-center rounded-md bg-accent text-white">
        <Boxes className="size-4" aria-hidden />
      </span>
      <span className="text-[15px] font-semibold tracking-tight">Equipment Manager</span>
    </span>
  );
}
