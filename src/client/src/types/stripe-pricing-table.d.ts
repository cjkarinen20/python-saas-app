
import type { DetailedHTMLProps, HTMLAttributes } from "react";

declare global {
  namespace JSX {
    interface IntrinsicElements {
      // Props defined by Stripe; include publishable key, pricing table id, 
      // and optional customer context.
      "stripe-pricing-table": DetailedHTMLProps<
        HTMLAttributes<HTMLElement>,
        HTMLElement
      > & {
        "pricing-table-id"?: string;
        "publishable-key"?: string;
        "client-reference-id"?: string;
        "customer-email"?: string;
      };
    }
  }
}

export {};
