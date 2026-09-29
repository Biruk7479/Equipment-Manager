"use client";

import Link from "next/link";
import { ButtonLink } from "@/components/ui/button";
import { EmptyState, ErrorMessage, Loading } from "@/components/ui/feedback";
import { Select } from "@/components/ui/form";
import { Pagination } from "@/components/ui/pagination";
import { Panel } from "@/components/ui/panel";
import { Table, TD, TH } from "@/components/ui/table";
import { useUser } from "@/features/auth/auth-provider";
import { useEquipmentOptions } from "@/features/equipment/api";
import { useEmployeeOptions } from "@/features/users/api";
import { errorMessage } from "@/lib/api";
import { cn } from "@/lib/cn";
import { formatDate, formatNumber } from "@/lib/format";
import { CATEGORY_LABELS, STATUSES, STATUS_LABELS } from "@/lib/labels";
import { useSearchState } from "@/lib/use-search-state";
import { useRequestList } from "./api";
import { StatusBadge } from "./status-badge";

const PAGE_SIZE = 10;

export function RequestList() {
  const isManager = useUser().role === "manager";
  const [filters, setFilters] = useSearchState({
    status: "",
    employee_id: "",
    equipment_id: "",
    order: "desc",
    page: "1",
  });
  const page = Number(filters.page) || 1;
  const { data, error, isPending, isPlaceholderData } = useRequestList({
    ...filters,
    page,
    page_size: PAGE_SIZE,
  });
  const equipment = useEquipmentOptions();
  const employees = useEmployeeOptions(isManager);
  const filtered = Boolean(filters.status || filters.employee_id || filters.equipment_id);

  return (
    <Panel>
      <div
        className={cn(
          "grid gap-3 border-b border-line p-4 sm:grid-cols-2",
          isManager ? "lg:grid-cols-4" : "lg:grid-cols-3",
        )}
      >
        <Select
          aria-label="Status"
          value={filters.status}
          onChange={(event) => setFilters({ status: event.target.value })}
        >
          <option value="">All statuses</option>
          {STATUSES.map((status) => (
            <option key={status} value={status}>
              {STATUS_LABELS[status]}
            </option>
          ))}
        </Select>
        {isManager && (
          <Select
            aria-label="Employee"
            value={filters.employee_id}
            onChange={(event) => setFilters({ employee_id: event.target.value })}
          >
            <option value="">All employees</option>
            {employees.data?.map((employee) => (
              <option key={employee.id} value={employee.id}>
                {employee.full_name}
              </option>
            ))}
          </Select>
        )}
        <Select
          aria-label="Equipment"
          value={filters.equipment_id}
          onChange={(event) => setFilters({ equipment_id: event.target.value })}
        >
          <option value="">All equipment</option>
          {equipment.data?.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </Select>
        <Select
          aria-label="Sort by date"
          value={filters.order}
          onChange={(event) => setFilters({ order: event.target.value })}
        >
          <option value="desc">Newest first</option>
          <option value="asc">Oldest first</option>
        </Select>
      </div>

      {error ? (
        <div className="p-4">
          <ErrorMessage message={errorMessage(error)} />
        </div>
      ) : isPending ? (
        <Loading />
      ) : data.items.length === 0 ? (
        <EmptyState
          title="No requests found"
          description={
            filtered
              ? "Try changing or clearing the filters."
              : isManager
                ? "Requests from employees will appear here."
                : "When you request equipment, you can track it here."
          }
          action={
            !filtered &&
            !isManager && <ButtonLink href="/requests/new">Request equipment</ButtonLink>
          }
        />
      ) : (
        <div className={cn("transition-opacity", isPlaceholderData && "opacity-60")}>
          <Table>
            <thead>
              <tr>
                <TH>Equipment</TH>
                <TH className="text-right">Qty</TH>
                {isManager && <TH className="hidden md:table-cell">Requested by</TH>}
                <TH>Status</TH>
                <TH className="hidden sm:table-cell">Submitted</TH>
                <TH>
                  <span className="sr-only">Actions</span>
                </TH>
              </tr>
            </thead>
            <tbody>
              {data.items.map((request) => (
                <tr key={request.id}>
                  <TD>
                    <Link href={`/requests/${request.id}`} className="font-medium hover:underline">
                      {request.equipment.name}
                    </Link>
                    <p className="mt-0.5 text-[13px] text-ink-muted">
                      #{request.id} · {CATEGORY_LABELS[request.equipment.category]}
                    </p>
                  </TD>
                  <TD className="text-right tabular-nums">{formatNumber(request.quantity)}</TD>
                  {isManager && (
                    <TD className="hidden md:table-cell">{request.requester.full_name}</TD>
                  )}
                  <TD>
                    <StatusBadge status={request.status} />
                  </TD>
                  <TD className="hidden whitespace-nowrap text-ink-muted sm:table-cell">
                    {formatDate(request.created_at)}
                  </TD>
                  <TD className="text-right">
                    <ButtonLink
                      href={`/requests/${request.id}`}
                      variant={isManager && request.status === "pending" ? "secondary" : "ghost"}
                      size="sm"
                    >
                      {isManager && request.status === "pending" ? "Review" : "View"}
                    </ButtonLink>
                  </TD>
                </tr>
              ))}
            </tbody>
          </Table>
          <Pagination
            page={page}
            pageSize={PAGE_SIZE}
            total={data.total}
            onPageChange={(next) => setFilters({ page: String(next) })}
          />
        </div>
      )}
    </Panel>
  );
}
