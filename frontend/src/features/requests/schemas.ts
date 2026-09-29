import { z } from "zod";

export const requestSchema = z.object({
  equipment_id: z.number("Choose the equipment you need").int().positive("Choose the equipment you need"),
  quantity: z
    .number("Enter a quantity")
    .int("Use a whole number")
    .min(1, "Request at least 1")
    .max(1000, "Quantity is too large"),
  justification: z
    .string()
    .trim()
    .min(10, "Explain in at least 10 characters why you need it")
    .max(1000, "Use at most 1000 characters"),
});

export type RequestValues = z.infer<typeof requestSchema>;
