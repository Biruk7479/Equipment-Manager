"use client";

import {
  ClipboardList,
  LayoutDashboard,
  LogOut,
  Menu,
  Package,
  UserRound,
  Users,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useLogout } from "@/features/auth/api";
import { useUser } from "@/features/auth/auth-provider";
import { cn } from "@/lib/cn";
import { ROLE_LABELS } from "@/lib/labels";
import { Logo } from "./logo";

export function AppShell({ children }: { children: React.ReactNode }) {
  const user = useUser();
  const pathname = usePathname();
  const logout = useLogout();
  const [menuOpen, setMenuOpen] = useState(false);
  const isManager = user.role === "manager";

  const items = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/equipment", label: "Equipment", icon: Package },
    { href: "/requests", label: isManager ? "Requests" : "My requests", icon: ClipboardList },
    ...(isManager ? [{ href: "/users", label: "Users", icon: Users }] : []),
    { href: "/account", label: "Account", icon: UserRound },
  ];

  const nav = (
    <nav aria-label="Main" className="space-y-0.5">
      {items.map(({ href, label, icon: Icon }) => {
        const active = pathname === href || pathname.startsWith(`${href}/`);
        return (
          <Link
            key={href}
            href={href}
            onClick={() => setMenuOpen(false)}
            aria-current={active ? "page" : undefined}
            className={cn(
              "flex items-center gap-2.5 rounded-md px-2.5 py-2 text-ink-muted transition-colors hover:bg-subtle hover:text-ink",
              active && "bg-subtle font-medium text-ink",
            )}
          >
            <Icon className={cn("size-4", active ? "text-accent" : "text-ink-faint")} aria-hidden />
            {label}
          </Link>
        );
      })}
    </nav>
  );

  const account = (
    <div className="flex items-center justify-between gap-2 border-t border-line px-2.5 pt-4">
      <div className="min-w-0">
        <p className="truncate font-medium">{user.full_name}</p>
        <p className="text-[13px] text-ink-muted">{ROLE_LABELS[user.role]}</p>
      </div>
      <Button
        variant="ghost"
        size="sm"
        className="px-2"
        onClick={() => logout.mutate()}
        disabled={logout.isPending}
        aria-label="Sign out"
        title="Sign out"
      >
        <LogOut className="size-4" />
      </Button>
    </div>
  );

  return (
    <div className="min-h-dvh">
      <aside className="fixed inset-y-0 left-0 hidden w-60 flex-col border-r border-line bg-surface px-3 py-5 lg:flex">
        <Link href="/dashboard" className="mb-8 px-2.5">
          <Logo />
        </Link>
        <div className="flex-1">{nav}</div>
        {account}
      </aside>

      <header className="sticky top-0 z-20 border-b border-line bg-surface lg:hidden">
        <div className="flex h-14 items-center justify-between px-4">
          <Link href="/dashboard">
            <Logo />
          </Link>
          <Button
            variant="ghost"
            size="sm"
            className="px-2"
            onClick={() => setMenuOpen((open) => !open)}
            aria-expanded={menuOpen}
            aria-controls="mobile-nav"
            aria-label={menuOpen ? "Close menu" : "Open menu"}
          >
            {menuOpen ? <X className="size-5" /> : <Menu className="size-5" />}
          </Button>
        </div>
        {menuOpen && (
          <div id="mobile-nav" className="space-y-4 border-t border-line px-3 py-4">
            {nav}
            {account}
          </div>
        )}
      </header>

      <main className="lg:pl-60">
        <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-10 lg:py-10">{children}</div>
      </main>
    </div>
  );
}
