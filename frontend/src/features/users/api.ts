"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Page, User } from "@/lib/types";

export function useEmployeeOptions(enabled: boolean) {
  return useQuery({
    enabled,
    queryKey: ["users", "employees"],
    queryFn: () => api.get<Page<User>>("/users", { role: "employee", page_size: 100 }),
    select: (page) => page.items,
  });
}
