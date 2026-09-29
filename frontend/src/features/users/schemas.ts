import { z } from "zod";

export const userSchema = z.object({
  full_name: z.string().trim().min(1, "Enter a full name").max(100),
  email: z.email("Enter a valid email address"),
  password: z.string().min(8, "Use at least 8 characters").max(128, "Use at most 128 characters"),
  role: z.enum(["employee", "manager"], "Choose a role"),
});

export type UserValues = z.infer<typeof userSchema>;
