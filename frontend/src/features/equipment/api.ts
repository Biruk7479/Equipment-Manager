"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Category, Equipment, Page } from "@/lib/types";

export type EquipmentFilters = {
  search?: string;
  category?: string;
  available?: string;
  page: number;
  page_size: number;
};

export type EquipmentInput = {
  name: string;
  category: Category;
  available_quantity: number;
  description: string | null;
};

export function useEquipmentList(filters: EquipmentFilters) {
  return useQuery({
    queryKey: ["equipment", "list", filters],
    queryFn: () => api.get<Page<Equipment>>("/equipment", filters),
    placeholderData: keepPreviousData,
  });
}

export function useEquipmentOptions() {
  return useQuery({
    queryKey: ["equipment", "options"],
    queryFn: () => api.get<Page<Equipment>>("/equipment", { page_size: 100 }),
    select: (page) => page.items,
  });
}

export function useEquipment(id: number) {
  return useQuery({
    queryKey: ["equipment", id],
    queryFn: () => api.get<Equipment>(`/equipment/${id}`),
  });
}

export function useSaveEquipment(id?: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: EquipmentInput) =>
      id
        ? api.put<Equipment>(`/equipment/${id}`, input)
        : api.post<Equipment>("/equipment", input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["equipment"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
