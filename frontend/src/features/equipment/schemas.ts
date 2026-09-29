import { z } from "zod";
import { CATEGORIES } from "@/lib/labels";

export const equipmentSchema = z.object({
  name: z.string().trim().min(2, "Use at least 2 characters").max(120, "Use at most 120 characters"),
  category: z.enum(CATEGORIES, "Choose a category"),
  available_quantity: z
    .number("Enter a quantity")
    .int("Use a whole number")
    .min(0, "Quantity cannot be negative")
    .max(100_000, "Quantity is too large"),
  description: z.string().trim().max(1000, "Use at most 1000 characters"),
});

export type EquipmentValues = z.infer<typeof equipmentSchema>;
