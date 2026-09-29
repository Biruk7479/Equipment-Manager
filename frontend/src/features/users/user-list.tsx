"use client";

import { Badge } from "@/components/ui/badge";
import { EmptyState, ErrorMessage, Loading } from "@/components/ui/feedback";
import { Select } from "@/components/ui/form";
import { Pagination } from "@/components/ui/pagination";
import { Panel } from "@/components/ui/panel";
import { SearchInput } from "@/components/ui/search-input";
import { Table, TD, TH } from "@/components/ui/table";
import { errorMessage } from "@/lib/api";
import { cn } from "@/lib/cn";
import { formatDate } from "@/lib/format";
import { ROLE_LABELS } from "@/lib/labels";
import { useSearchState } from "@/lib/use-search-state";
import { useUserList } from "./api";

const PAGE_SIZE = 10;

export function UserList() {
  const [filters, setFilters] = useSearchState({ search: "", role: "", page: "1" });
  const page = Number(filters.page) || 1;
  const { data, error, isPending, isPlaceholderData } = useUserList({
    ...filters,
    page,
    page_size: PAGE_SIZE,
  });

  return (
    <Panel>
      <div className="flex flex-col gap-3 border-b border-line p-4 sm:flex-row">
        <div className="sm:w-72">
          <SearchInput
            label="Search users"
            placeholder="Search by name or email"
            value={filters.search}
            onChange={(search) => setFilters({ search })}
          />
        </div>
        <Select
          aria-label="Role"
          value={filters.role}
          onChange={(event) => setFilters({ role: event.target.value })}
          className="sm:w-44"
        >
          <option value="">All roles</option>
          <option value="employee">Employees</option>
          <option value="manager">Managers</option>
        </Select>
      </div>

      {error ? (
        <div className="p-4">
          <ErrorMessage message={errorMessage(error)} />
        </div>
      ) : isPending ? (
        <Loading />
      ) : data.items.length === 0 ? (
        <EmptyState title="No users found" description="Try a different search or role." />
      ) : (
        <div className={cn("transition-opacity", isPlaceholderData && "opacity-60")}>
          <Table>
            <thead>
              <tr>
                <TH>Name</TH>
                <TH className="hidden sm:table-cell">Email</TH>
                <TH>Role</TH>
                <TH className="hidden md:table-cell">Joined</TH>
              </tr>
            </thead>
            <tbody>
              {data.items.map((user) => (
                <tr key={user.id}>
                  <TD>
                    <p className="font-medium">{user.full_name}</p>
                    <p className="mt-0.5 text-[13px] break-all text-ink-muted sm:hidden">
                      {user.email}
                    </p>
                  </TD>
                  <TD className="hidden text-ink-muted sm:table-cell">{user.email}</TD>
                  <TD>
                    <Badge tone={user.role === "manager" ? "accent" : "neutral"}>
                      {ROLE_LABELS[user.role]}
                    </Badge>
                  </TD>
                  <TD className="hidden whitespace-nowrap text-ink-muted md:table-cell">
                    {formatDate(user.created_at)}
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
