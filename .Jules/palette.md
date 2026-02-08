## 2026-02-08 - Icon-Only Button Accessibility Pattern
**Learning:** This codebase extensively uses icon-only `Button` components from `lucide-react` without `aria-label` attributes, which significantly impacts accessibility for screen reader users. The `Button` component correctly spreads props, so `aria-label` can be directly applied.
**Action:** When working on UI components, systematically check all icon-only buttons for `aria-label` or `sr-only` text.
