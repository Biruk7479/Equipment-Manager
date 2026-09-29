const FALLBACK = "/dashboard";

export function nextPath(next: string | null) {
  const url = next ? URL.parse(next, window.location.origin) : null;
  return url?.origin === window.location.origin ? `${url.pathname}${url.search}` : FALLBACK;
}
