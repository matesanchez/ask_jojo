# Product

## Register

product

## Users

Nurix Therapeutics scientists and staff (protein sciences, analytical chemistry, in-vivo pharmacology, discovery biology) plus the program owner. They use JoJo Bot on a workstation during focused work: looking up what the company already knows about a target, program, method, or compound; tracing a claim back to its source document; and generating quick artifacts (answers, tables, decks) grounded in the internal corpus. The job to be done is "get a trustworthy, cited answer from years of accumulated internal knowledge without hunting through SharePoint and the P: drive."

## Product Purpose

JoJo Bot is Nurix's internal knowledge assistant: a continuously LLM-compiled wiki built from the company's immutable source documents, with Q&A, browse, audit, graph, and rich-output surfaces on top. It exists to turn a 139k-document sprawl into a coherent, source-grounded understanding that compounds over time. Success is a scientist trusting JoJo's answer enough to act on it, because every claim links back to the exact document it came from.

## Brand Personality

Calm scientific authority. Three words: precise, trustworthy, understated. The voice is that of a meticulous senior colleague who never overstates, always cites, and says "I don't have a source for that" rather than guessing. The interface should feel like a high-end laboratory instrument: quiet, exact, and confidence-inspiring — not a chatty consumer app and not a flashy startup dashboard.

## Anti-references

- Generic AI-SaaS templates: Inter everywhere, purple-to-blue gradients, cards-in-cards, emoji headings, the rounded-icon-tile-above-every-title look.
- Chatbot toys: bubbly mascots, bouncy/elastic motion, exclamation-heavy copy.
- Over-dense enterprise BI dashboards: tiny gray text on busy backgrounds, chart-junk, no breathing room.
- Anything that reads as "untrustworthy" or "guessing" — the design must earn scientific trust.

## Design Principles

1. **Every claim is traceable.** The UI always makes provenance one click away; citations and source links are first-class, never an afterthought.
2. **Quiet confidence over decoration.** Restraint is the brand. Hierarchy comes from type, space, and a single decisive accent — not from borders, boxes, and color noise.
3. **Reading is the primary act.** Long-form wiki and source reading must be comfortable for minutes at a time — generous measure, calm contrast, real typography.
4. **Identity preserved.** Nurix navy and gold are the anchor; the facelift sharpens the existing identity rather than replacing it.
5. **Honest states.** Empty, loading, and error states tell the truth plainly and point to the next action.

## Accessibility & Inclusion

Target WCAG 2.1 AA: >=4.5:1 contrast for body text, >=3:1 for large text and UI. Full keyboard navigation with visible focus rings. Respect `prefers-reduced-motion` (motion is decorative, never load-bearing) and `prefers-color-scheme`. Light and dark themes both meet contrast targets. Never encode meaning in color alone (pair status colors with text/icon).
