export type Role = "employee" | "manager";
export type Category = "laptop" | "monitor" | "mobile_phone" | "keyboard" | "headset";
export type RequestStatus = "pending" | "approved" | "rejected";

export type Page<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
};

export type User = {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  created_at: string;
};

export type Equipment = {
  id: number;
  name: string;
  category: Category;
  description: string | null;
  available_quantity: number;
  created_at: string;
  updated_at: string;
};

type UserSummary = Pick<User, "id" | "full_name" | "email">;

export type EquipmentRequest = {
  id: number;
  quantity: number;
  justification: string;
  status: RequestStatus;
  review_comment: string | null;
  reviewed_at: string | null;
  created_at: string;
  equipment: Pick<Equipment, "id" | "name" | "category">;
  requester: UserSummary;
  reviewer: UserSummary | null;
};

export type HistoryEntry = {
  id: number;
  previous_status: RequestStatus | null;
  new_status: RequestStatus;
  comment: string | null;
  created_at: string;
  actor: UserSummary;
};

export type StatusCounts = Record<RequestStatus, number>;

export type Dashboard = {
  total_equipment: number;
  total_available_quantity: number;
  requests: StatusCounts;
  requests_by_category: Array<StatusCounts & { category: Category }>;
};
