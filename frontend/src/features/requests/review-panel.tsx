"use client";

import { TriangleAlert } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/feedback";
import { Field, Textarea } from "@/components/ui/form";
import { Panel } from "@/components/ui/panel";
import { useEquipment } from "@/features/equipment/api";
import { errorMessage } from "@/lib/api";
import { formatNumber } from "@/lib/format";
import type { EquipmentRequest } from "@/lib/types";
import { type ReviewInput, useReviewRequest } from "./api";

export function ReviewPanel({ request }: { request: EquipmentRequest }) {
  const stock = useEquipment(request.equipment.id);
  const review = useReviewRequest(request.id);
  const [comment, setComment] = useState("");
  const [commentError, setCommentError] = useState<string>();

  const available = stock.data?.available_quantity;
  const insufficient = available !== undefined && available < request.quantity;

  function submit(decision: ReviewInput["decision"]) {
    const trimmed = comment.trim();
    if (decision === "reject" && !trimmed) {
      setCommentError("Add a comment explaining why the request is rejected.");
      return;
    }
    setCommentError(undefined);
    review.mutate({ decision, comment: trimmed || null });
  }

  return (
    <Panel title="Review" description="Approving deducts the quantity from stock.">
      <div className="space-y-4 p-5">
        <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-md border border-line bg-line">
          <div className="bg-canvas px-3 py-2.5">
            <dt className="text-[13px] text-ink-muted">Requested</dt>
            <dd className="mt-0.5 text-base font-semibold">{formatNumber(request.quantity)}</dd>
          </div>
          <div className="bg-canvas px-3 py-2.5">
            <dt className="text-[13px] text-ink-muted">In stock</dt>
            <dd className="mt-0.5 text-base font-semibold">
              {available === undefined ? "–" : formatNumber(available)}
            </dd>
          </div>
        </dl>
        {insufficient && (
          <p className="flex gap-2 rounded-md bg-pending-soft px-3 py-2.5 text-[13px] text-pending">
            <TriangleAlert className="mt-px size-4 shrink-0" aria-hidden />
            Not enough stock to approve. Update the equipment quantity or reject the request.
          </p>
        )}
        {review.error && <ErrorMessage message={errorMessage(review.error)} />}
        <Field
          label="Comment"
          htmlFor="review-comment"
          error={commentError}
          hint="Required when rejecting."
        >
          <Textarea
            id="review-comment"
            rows={4}
            value={comment}
            onChange={(event) => setComment(event.target.value)}
            aria-invalid={!!commentError}
          />
        </Field>
        <div className="grid grid-cols-2 gap-2">
          <Button
            onClick={() => submit("approve")}
            disabled={insufficient || review.isPending}
            loading={review.isPending && review.variables.decision === "approve"}
          >
            Approve
          </Button>
          <Button
            variant="secondary"
            className="text-danger"
            onClick={() => submit("reject")}
            disabled={review.isPending}
            loading={review.isPending && review.variables.decision === "reject"}
          >
            Reject
          </Button>
        </div>
      </div>
    </Panel>
  );
}
