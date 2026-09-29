"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { EquipmentRequest, HistoryEntry, Page } from "@/lib/types";

export type RequestFilters = {
  status?: string;
  employee_id?: string;
  equipment_id?: string;
  order: string;
  page: number;
  page_size: number;
};

export type RequestInput = { equipment_id: number; quantity: number; justification: string };
export type ReviewInput = { decision: "approve" | "reject"; comment: string | null };

export function useRequestList(filters: RequestFilters) {
  return useQuery({
    queryKey: ["requests", "list", filters],
    queryFn: () => api.get<Page<EquipmentRequest>>("/requests", filters),
    placeholderData: keepPreviousData,
  });
}

export function useRequest(id: number) {
  return useQuery({
    queryKey: ["requests", id],
    queryFn: () => api.get<EquipmentRequest>(`/requests/${id}`),
  });
}

export function useRequestHistory(id: number) {
  return useQuery({
    queryKey: ["requests", id, "history"],
    queryFn: () => api.get<HistoryEntry[]>(`/requests/${id}/history`),
  });
}

export function useCreateRequest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: RequestInput) => api.post<EquipmentRequest>("/requests", input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["requests"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useReviewRequest(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ decision, comment }: ReviewInput) =>
      api.post<EquipmentRequest>(`/requests/${id}/${decision}`, { comment }),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["requests"] });
      queryClient.invalidateQueries({ queryKey: ["equipment"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
