"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

export function useSearchState<T extends Record<string, string>>(defaults: T) {
  const params = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const state = Object.fromEntries(
    Object.entries(defaults).map(([key, fallback]) => [key, params.get(key) ?? fallback]),
  ) as T;

  function update(changes: Partial<T>) {
    const next = new URLSearchParams(params);
    for (const [key, value] of Object.entries(changes)) {
      if (!value || value === defaults[key]) next.delete(key);
      else next.set(key, value);
    }
    if (!("page" in changes)) next.delete("page");
    router.replace(next.size ? `${pathname}?${next}` : pathname, { scroll: false });
  }

  return [state, update] as const;
}
