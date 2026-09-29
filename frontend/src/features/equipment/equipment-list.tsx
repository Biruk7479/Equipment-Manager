"use client";

import { Badge } from "@/components/ui/badge";
import { ButtonLink } from "@/components/ui/button";
import { EmptyState, ErrorMessage, Loading } from "@/components/ui/feedback";
import { Select } from "@/components/ui/form";
import { Pagination } from "@/components/ui/pagination";
import { Panel } from "@/components/ui/panel";
import { SearchInput } from "@/components/ui/search-input";
import { Table, TD, TH } from "@/components/ui/table";
import { useUser } from "@/features/auth/auth-provider";
import { errorMessage } from "@/lib/api";
import { cn } from "@/lib/cn";
import { formatDate, formatNumber } from "@/lib/format";
import { CATEGORIES, CATEGORY_LABELS } from "@/lib/labels";
import { useSearchState } from "@/lib/use-search-state";
import { useEquipmentList } from "./api";

const PAGE_SIZE = 10;

export function EquipmentList() {
  const isManager = useUser().role === "manager";
  const [filters, setFilters] = useSearchState({ search: "", category: "", available: "", page: "1" });
  const page = Number(filters.page) || 1;
  const { data, error, isPending, isPlaceholderData } = useEquipmentList({
    search: filters.search,
    category: filters.category,
    available: filters.available,
    page,
    page_size: PAGE_SIZE,
  });
  const filtered = Boolean(filters.search || filters.category || filters.available);

  return (
    <Panel>
      <div className="flex flex-col gap-3 border-b border-line p-4 sm:flex-row">
        <div className="sm:w-72">
          <SearchInput
            label="Search equipment"
            placeholder="Search by name"
            value={filters.search}
            onChange={(search) => setFilters({ search })}
          />
        </div>
        <Select
          aria-label="Category"
          value={filters.category}
          onChange={(event) => setFilters({ category: event.target.value })}
          className="sm:w-44"
        >
          <option value="">All categories</option>
          {CATEGORIES.map((category) => (
            <option key={category} value={category}>
              {CATEGORY_LABELS[category]}
            </option>
          ))}
        </Select>
        <Select
          aria-label="Availability"
          value={filters.available}
          onChange={(event) => setFilters({ available: event.target.value })}
          className="sm:w-44"
        >
          <option value="">Any availability</option>
          <option value="true">In stock</option>
          <option value="false">Out of stock</option>
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
          title="No equipment found"
          description={
            filtered
              ? "Try a different search or clear the filters."
              : isManager
                ? "Add your first item to start taking requests."
                : "Nothing has been added yet."
          }
        />
      ) : (
        <div className={cn("transition-opacity", isPlaceholderData && "opacity-60")}>
          <Table>
            <thead>
              <tr>
                <TH>Name</TH>
                <TH className="hidden sm:table-cell">Category</TH>
                <TH className="text-right">Available</TH>
                <TH className="hidden md:table-cell">Updated</TH>
                <TH>
                  <span className="sr-only">Actions</span>
                </TH>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr key={item.id}>
                  <TD>
                    <p className="font-medium">{item.name}</p>
                    <p className="mt-0.5 line-clamp-1 max-w-md text-[13px] text-ink-muted">
                      <span className="sm:hidden">{CATEGORY_LABELS[item.category]}</span>
                      <span className="hidden sm:inline">{item.description}</span>
                    </p>
                  </TD>
                  <TD className="hidden whitespace-nowrap sm:table-cell">
                    {CATEGORY_LABELS[item.category]}
                  </TD>
                  <TD className="text-right tabular-nums">
                    {item.available_quantity > 0 ? (
                      formatNumber(item.available_quantity)
                    ) : (
                      <Badge>Out of stock</Badge>
                    )}
                  </TD>
                  <TD className="hidden whitespace-nowrap text-ink-muted md:table-cell">
                    {formatDate(item.updated_at)}
                  </TD>
                  <TD className="text-right">
                    {isManager ? (
                      <ButtonLink href={`/equipment/${item.id}/edit`} variant="ghost" size="sm">
                        Edit
                      </ButtonLink>
                    ) : (
                      item.available_quantity > 0 && (
                        <ButtonLink
                          href={`/requests/new?equipment=${item.id}`}
                          variant="secondary"
                          size="sm"
                        >
                          Request
                        </ButtonLink>
                      )
                    )}
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
