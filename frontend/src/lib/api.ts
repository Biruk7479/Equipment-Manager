export type ApiErrorDetail = { field: string; message: string };

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly details: ApiErrorDetail[] | null = null,
  ) {
    super(message);
  }
}

type Query = Record<string, string | number | boolean | null | undefined>;

const SKIP_REFRESH = ["/auth/login", "/auth/register", "/auth/refresh", "/auth/logout"];

let refreshing: Promise<boolean> | null = null;

function refreshSession() {
  refreshing ??= acrossTabs("session-refresh", () =>
    fetch("/api/v1/auth/refresh", { method: "POST" }).then((response) => response.ok),
  ).finally(() => {
    refreshing = null;
  });
  return refreshing;
}

// Refresh tokens are single-use, so tabs must take turns or a concurrent refresh looks like theft.
async function acrossTabs<T>(lock: string, task: () => Promise<T>): Promise<T> {
  return "locks" in navigator ? navigator.locks.request(lock, task) : task();
}

async function request<T>(method: string, path: string, body?: unknown, retry = true): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (response.status === 401 && retry && !SKIP_REFRESH.includes(path) && (await refreshSession())) {
    return request<T>(method, path, body, false);
  }

  if (!response.ok) {
    const error = (await response.json().catch(() => null))?.error;
    throw new ApiError(
      response.status,
      error?.code ?? "unknown_error",
      error?.message ?? "Something went wrong. Please try again.",
      error?.details ?? null,
    );
  }

  return response.status === 204 ? (undefined as T) : response.json();
}

function withQuery(path: string, query?: Query) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== undefined && value !== null && value !== "") params.set(key, String(value));
  }
  return params.size ? `${path}?${params}` : path;
}

export const api = {
  get: <T>(path: string, query?: Query) => request<T>("GET", withQuery(path, query)),
  post: <T>(path: string, body?: unknown) => request<T>("POST", path, body),
  put: <T>(path: string, body: unknown) => request<T>("PUT", path, body),
};

export function errorMessage(error: unknown) {
  return error instanceof ApiError ? error.message : "Something went wrong. Please try again.";
}
