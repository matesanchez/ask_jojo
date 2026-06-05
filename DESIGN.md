# Design

Visual system for JoJo Bot. Register: **product** (design serves the tool). Personality: **calm scientific authority** — precise, trustworthy, understated. Identity is preserved: Nurix navy + gold, sharpened.

## Theme

Light and dark, switchable via a header toggle. Light is the default for long-form reading; dark is a "lab instrument" mode. Theme is stored in `localStorage` and falls back to `prefers-color-scheme`. All colors are authored in **OKLCH** as semantic tokens; components reference tokens, never raw hex, so both themes stay in sync.

## Color palette

Anchored on the Nurix brand, expressed in OKLCH. Brand hue ~262 (navy), accent hue ~80 (gold).

Brand (constant across themes):
- Navy `oklch(0.226 0.101 262)` — primary brand surface (header), brand ink.
- Navy-dark `oklch(0.178 0.072 260)`, Navy-light `oklch(0.309 0.163 263)`.
- Gold (primary accent) `oklch(0.821 0.169 80)`; hover `oklch(0.761 0.158 80)`. Text on gold = navy ink.
- Accent red `oklch(0.646 0.208 13)`; success green `oklch(0.523 0.135 144)`.

Light theme neutrals (navy-tinted, never pure gray):
- bg `oklch(0.985 0.004 262)`, surface `oklch(0.995 0.003 262)`, surface-2 `oklch(0.966 0.006 262)`
- ink `oklch(0.25 0.03 262)`, ink-2 `oklch(0.50 0.03 262)`, ink-3 `oklch(0.62 0.025 262)`
- border `oklch(0.90 0.008 262)`, border-strong `oklch(0.82 0.012 262)`

Dark theme neutrals (deep navy, lifted surfaces):
- bg `oklch(0.19 0.03 262)`, surface `oklch(0.235 0.035 262)`, surface-2 `oklch(0.285 0.04 262)`
- ink `oklch(0.94 0.012 262)`, ink-2 `oklch(0.74 0.02 262)`, ink-3 `oklch(0.60 0.02 262)`
- border `oklch(0.33 0.03 262)`, border-strong `oklch(0.42 0.035 262)`

Contrast: body ink on bg exceeds 4.5:1 in both themes. Status is never color-only (always paired with text/icon).

## Typography

**IBM Plex** superfamily — distinctive, technical, authoritative, and a coherent system; deliberately NOT Inter/Roboto/Geist/system defaults. Self-hosted at build time via `next/font/google`, so it is bundled into the exe and works offline.

- **IBM Plex Sans** — UI, headings, and body. Headings use weight 600 with tightened tracking (-0.01em to -0.02em) at large sizes; body 400/450 at ~16px, line-height 1.6, max measure ~70ch for reading surfaces.
- **IBM Plex Mono** — code, hashes, IDs, source paths, metadata, and badges (the "instrument readout" voice).
- Modular type scale (~1.2 minor third): 12.8 / 14 / 16 / 19.2 / 24 / 30 / 37.5 px.

## Spacing & shape

- 4px base spacing scale: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64.
- Radius: sm 6px, md 10px, lg 14px (cards). Consistent, never mixed arbitrarily.
- Elevation: soft, low-spread navy-tinted shadows (no hard black). One or two levels only.

## Motion

Restrained, in service of orientation (calm authority). Durations 120-220ms; easing `cubic-bezier(0.2, 0, 0, 1)` (no bounce/elastic — that anti-pattern is banned). Tab/route changes and hovers get subtle transitions; nothing animates on load that isn't communicating state. All motion gated behind `prefers-reduced-motion`.

## Components & layout

- **App shell**: navy header (brand, constant in both themes) with the JoJo mark, version, primary nav (underline-on-active in gold), and the theme toggle on the right. Content in a centered column, generous padding.
- **Cards/panels**: surface token, 1px border token, md radius, soft shadow. No thick one-side accent borders (the "side-tab" AI tell is removed).
- **Accent discipline**: gold is the single decisive accent (active nav, primary action, focus). Used sparingly so it stays meaningful.
- **Focus**: visible 2px gold focus ring with offset on all interactive elements.

## Anti-patterns explicitly avoided

Overused fonts; pure black/gray (always navy-tinted); gradients-as-decoration; cards nested in cards; thick side-accent borders; bounce/elastic easing; gray text on colored backgrounds; emoji/eyebrow-chip/numbered-marker scaffolding.
