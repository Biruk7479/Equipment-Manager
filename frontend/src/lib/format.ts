const date = new Intl.DateTimeFormat("en", { dateStyle: "medium" });
const dateTime = new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" });
const number = new Intl.NumberFormat("en");

export const formatDate = (value: string) => date.format(new Date(value));
export const formatDateTime = (value: string) => dateTime.format(new Date(value));
export const formatNumber = (value: number) => number.format(value);
