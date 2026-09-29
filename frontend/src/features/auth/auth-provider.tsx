"use client";

import { createContext, useContext } from "react";
import { Button } from "@/components/ui/button";
import { ErrorMessage, Loading } from "@/components/ui/feedback";
import { errorMessage } from "@/lib/api";
import type { User } from "@/lib/types";
import { useMe } from "./api";

const AuthContext = createContext<User | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: user, error, refetch, isFetching } = useMe();

  if (user) return <AuthContext value={user}>{children}</AuthContext>;

  if (error) {
    return (
      <div className="mx-auto mt-24 max-w-sm space-y-3 px-4">
        <ErrorMessage message={errorMessage(error)} />
        <Button variant="secondary" onClick={() => refetch()} loading={isFetching}>
          Try again
        </Button>
      </div>
    );
  }

  return <Loading />;
}

export function useUser() {
  const user = useContext(AuthContext);
  if (!user) throw new Error("useUser must be used inside AuthProvider");
  return user;
}
