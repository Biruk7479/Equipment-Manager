import type { Category, RequestStatus, Role } from "./types";

export const CATEGORY_LABELS: Record<Category, string> = {
  laptop: "Laptop",
  monitor: "Monitor",
  mobile_phone: "Mobile phone",
  keyboard: "Keyboard",
  headset: "Headset",
};

export const CATEGORIES = [
  "laptop",
  "monitor",
  "mobile_phone",
  "keyboard",
  "headset",
] as const satisfies readonly Category[];

export const STATUS_LABELS: Record<RequestStatus, string> = {
  pending: "Pending",
  approved: "Approved",
  rejected: "Rejected",
};

export const STATUSES = ["pending", "approved", "rejected"] as const satisfies readonly RequestStatus[];

export const ROLE_LABELS: Record<Role, string> = {
  employee: "Employee",
  manager: "Manager",
};
