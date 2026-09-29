"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Page, Role, User } from "@/lib/types";

export type UserFilters = { search?: string; role?: string; page: number; page_size: number };
export type UserInput = { full_name: string; email: string; password: string; role: Role };

export function useUserList(filters: UserFilters) {
  return useQuery({
    queryKey: ["users", "list", filters],
    queryFn: () => api.get<Page<User>>("/users", filters),
    placeholderData: keepPreviousData,
  });
}

export function useEmployeeOptions(enabled: boolean) {
  return useQuery({
    enabled,
    queryKey: ["users", "employees"],
    queryFn: () => api.get<Page<User>>("/users", { role: "employee", page_size: 100 }),
    select: (page) => page.items,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: UserInput) => api.post<User>("/users", input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });
}
