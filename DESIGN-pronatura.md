# Pronatura Noroeste — Style Reference
> Guardians of the Northwest Coast

**Theme:** light

The design feels like standing at the edge of the Sea of Cortez at dawn — a vast, luminous sky reflecting off still water, the horizon blurred between blue and sand. A warm off-white base (#f5f2ed) grounds the palette with the feeling of bleached limestone and dry arroyos, while a deep tidal blue-green (#1b5c5a) provides authority and depth. A single high-energy accent — the amber of a shorebird's bill (#e07c2a) — reserves all urgency for calls-to-action. Typography pairs a contemporary humanist sans-serif for all headlines (creating warmth without sentimentality) with a clean utilitarian face for body and UI. The contrast between full-bleed field photography and generous white space below creates a journey from the land itself to the people who protect it.

---

## Tokens — Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| Tide | `#1b5c5a` | `--color-tide` | Primary brand color. Navigation, section headers, key UI surfaces. |
| Amber | `#e07c2a` | `--color-amber` | Primary CTA buttons — the single warm accent in a cool-neutral palette. |
| Amber Soft | `#fbebd8` | `--color-amber-soft` | Hover states, secondary CTA backgrounds, warm highlights. |
| Dune | `#f5f2ed` | `--color-dune` | Outermost page background. Warm off-white suggesting sand and limestone. |
| Salt | `#ffffff` | `--color-salt` | Card surfaces, elevated containers, modal backgrounds. |
| Mangrove | `#0f3634` | `--color-mangrove` | Deep tonal variant. Footer, darkest UI surfaces, emphasis text on Tide. |
| Kelp | `#2e7b78` | `--color-kelp` | Secondary interactive tones. Active nav states, link hovers. |
| Fog | `#e8e4df` | `--color-fog` | Borders, dividers, subtle section separators. |
| Stone | `#6b6760` | `--color-stone` | Secondary text, captions, metadata, footer copy. |
| Ink | `#1e1c19` | `--color-ink` | Primary text on light backgrounds. Near-black, warm-tinted. |
| Pure White | `#ffffff` | `--color-pure-white` | Text on Tide and Amber CTA buttons. |

---

## Tokens — Typography

### Primary Face — Headlines & Display · `--font-display`
> Recommended: **Fraunces** (Google Fonts, free) — a contemporary optical-size serif with an outdoor, field-journal quality. Fallbacks: Georgia, 'Times New Roman', serif.
- **Weights used:** 300, 400, 600
- **Sizes:** 18px, 24px, 32px, 42px, 56px, 72px
- **Line height:** 1.10–1.20 for display; 1.25–1.35 for headings
- **Letter spacing:** Slightly negative at large sizes (–0.01em at 56px+), neutral at smaller sizes
- **Role:** Hero headlines, section titles, pull quotes, stat figures. The serif treatment signals deep institutional knowledge and connection to the natural world — not tech, not startup.

### Body & UI Face · `--font-sans`
> Recommended: **DM Sans** (Google Fonts, free) — a geometric humanist sans-serif, highly legible at small sizes, contemporary without being cold. Fallbacks: 'Helvetica Neue', Arial, sans-serif.
- **Weights used:** 400, 500, 600
- **Sizes:** 13px, 15px, 17px, 20px, 24px
- **Line height:** 1.5–1.65
- **Letter spacing:** 0.01–0.02em for legibility at small sizes; 0.08em uppercase tracking for labels
- **Role:** Body copy, navigation, UI labels, captions, button text, legal copy. The workhorse. Remains neutral so the serif display can carry personality.

### Type Scale

| Role | Size | Font | Weight | Line Height | Letter Spacing | Token |
|------|------|------|--------|-------------|----------------|-------|
| caption | 13px | DM Sans | 400 | 1.5 | 0.02em | `--text-caption` |
| label | 13px | DM Sans | 600 | 1.0 | 0.08em (uppercase) | `--text-label` |
| body-sm | 15px | DM Sans | 400 | 1.6 | 0.01em | `--text-body-sm` |
| body | 17px | DM Sans | 400 | 1.65 | 0.005em | `--text-body` |
| subheading | 20px | DM Sans | 500 | 1.4 | 0 | `--text-subheading` |
| heading-sm | 24px | Fraunces | 400 | 1.3 | 0 | `--text-heading-sm` |
| heading | 32px | Fraunces | 400 | 1.25 | –0.005em | `--text-heading` |
| heading-lg | 42px | Fraunces | 300 | 1.2 | –0.01em | `--text-heading-lg` |
| display | 56–72px | Fraunces | 300 | 1.1 | –0.015em | `--text-display` |
| stat | 56px | Fraunces | 600 | 1.0 | –0.02em | `--text-stat` |

---

## Tokens — Spacing & Shapes

**Base unit:** 4px

**Density:** spacious — conservation work deserves room to breathe.

### Spacing Scale

| Name | Value | Token |
|------|-------|-------|
| 4 | 4px | `--spacing-4` |
| 8 | 8px | `--spacing-8` |
| 12 | 12px | `--spacing-12` |
| 16 | 16px | `--spacing-16` |
| 24 | 24px | `--spacing-24` |
| 32 | 32px | `--spacing-32` |
| 48 | 48px | `--spacing-48` |
| 64 | 64px | `--spacing-64` |
| 80 | 80px | `--spacing-80` |
| 96 | 96px | `--spacing-96` |
| 128 | 128px | `--spacing-128` |
| 160 | 160px | `--spacing-160` |

### Border Radius

| Element | Value | Notes |
|---------|-------|-------|
| cards | 2px | Near-flat. Intentional — suggests a field notebook, a document. |
| inputs | 4px | Consistent with card radius — utilitarian. |
| buttons | 4px | Rectangular pill. Not fully rounded. Ground-level, not tech-startup. |
| tags/badges | 2px | Same language as cards. |
| image containers | 0px | Photography bleeds to edge, uncontained. |
| stat callouts | 0px | Raw numbers, no softening. |

> **Rationale on radius:** The Mercury reference uses aggressive pill shapes (32–40px). That signals fintech/SaaS. Pronatura is a field conservation NGO — 35 years of real work in demanding terrain. Sharp, grounded corners reinforce institutional credibility, not startup friendliness.

### Layout

- **Page max-width:** 1120px
- **Section gap:** 96–128px
- **Element gap:** 16–48px
- **Grid:** 12-column with 24px gutters
- **Hero:** Full-bleed to viewport edges, no max-width constraint

---

## Components

### Primary Button (Amber)
**Role:** Donate, contribute, primary site actions (CONTRIBUYE, INVOLÚCRATE).

Solid `--color-amber` (#e07c2a) background, `--color-pure-white` text. 4px corner radius. Padding 14px 28px. Font: DM Sans 600, 15px, uppercase tracking 0.06em. Hover: darken amber 8%, no scale transform.

### Secondary Button (Tide Outline)
**Role:** Secondary actions — learn more, see projects, navigation CTAs.

Transparent background with 1.5px `--color-tide` (#1b5c5a) border. `--color-tide` text. Same radius, padding as primary. Hover: `--color-tide` fill, `--color-pure-white` text.

### Navigation Bar
**Role:** Global site header.

`--color-mangrove` (#0f3634) background. Logo (white variant) left-aligned. Nav links: DM Sans 500, 15px, `--color-pure-white` at 85% opacity. Active/hover: 100% opacity + 1px `--color-amber` underline offset 4px. CTA button (Amber) right-aligned. Becomes sticky on scroll with subtle backdrop blur.

### Stat Callout
**Role:** The 8 impact figures (20 protected areas, 7 fisheries, 266,000 hectares…).

Large Fraunces 600 number at 56px in `--color-tide`. Label below in DM Sans 600 uppercase at 13px, `--color-stone`, letter-spacing 0.08em. Optional icon above in `--color-amber`. No card border. Sits on `--color-dune` background with generous space above and below.

### News Card
**Role:** Noticias / latest news items.

`--color-salt` background, 2px radius, no shadow. Top: full-bleed photograph (no radius). Body: 16px padding. Date in DM Sans 400 13px `--color-stone`. Title in Fraunces 400 20px `--color-ink`. Hover: translate Y –2px, add 1px `--color-fog` border, `--color-kelp` title color.

### Section Eyebrow
**Role:** Label above a section headline (e.g., "NUESTRO TRABAJO", "NOTICIAS").

DM Sans 600, 13px, `--color-amber`, uppercase, letter-spacing 0.1em. Left-aligned flush with content column. 12px margin below before the section headline.

### Footer Link
**Role:** Footer navigation.

DM Sans 400, 15px, `--color-fog` at 70% opacity. Hover: `--color-amber-soft`. No underline. `--color-mangrove` background.

### Inline Body Link
**Role:** In-text hyperlinks.

`--color-kelp` (#2e7b78) underline (text-decoration). Hover: `--color-tide`. No color change on the text itself — only the underline animates.

---

## Do's and Don'ts

### Do
- Use `--color-tide` as the primary brand presence: navigation, section titles, key UI backgrounds.
- Reserve `--color-amber` exclusively for CTAs and high-urgency actions — it should be the rarest warm element on any given view.
- Keep cards and buttons at near-flat corner radius (2–4px). This is a field organization, not a fintech app.
- Use Fraunces at light weight (300–400) for all major headlines. The optical size and warmth carry the brand.
- Bleed photography edge-to-edge within its container. Never crop it with a border-radius.
- Use the eyebrow label + Fraunces headline pairing for all section introductions.
- Provide generous vertical whitespace (96px+) between sections. The work deserves room.
- Write stat figures in Fraunces 600 — large numbers are the clearest evidence of 35 years of impact.

### Don't
- Don't use `--color-amber` for decorative elements, backgrounds, or borders. One accent, used sparingly.
- Don't round buttons or inputs beyond 4px. Pill shapes signal SaaS, not NGO.
- Don't use heavy font weights (Fraunces > 600, DM Sans > 600) for any typography.
- Don't add drop shadows for elevation. Use background color shift (`--color-dune` → `--color-salt` → `--color-fog`) instead.
- Don't introduce new saturated colors. The palette is warm neutrals + one teal brand + one amber accent.
- Don't center body text beyond pull quotes. Left-aligned text is easier to scan and more institutional.
- Don't use `--color-tide` for body text on `--color-dune`. Contrast is insufficient for large paragraphs — use `--color-ink`.
- Don't use all-caps for anything beyond labels/eyebrows (13px, high tracking). Larger uppercase text reads as shouting.

---

## Surfaces

| Level | Name | Value | Purpose |
|-------|------|-------|---------|
| 0 | Dune | `#f5f2ed` | Base page background. Warm off-white. |
| 1 | Salt | `#ffffff` | Card, modal, and elevated section surfaces. |
| 2 | Fog | `#e8e4df` | Table rows, hover backgrounds, input fills. |
| 3 | Tide | `#1b5c5a` | Dark surface sections (e.g., footer CTA, feature blocks). |
| 4 | Mangrove | `#0f3634` | Navigation bar, page footer. Deepest layer. |

---

## Elevation

Elevation is achieved through background contrast, not shadow. Moving from Dune to Salt to Fog creates the feel of a card lifting off the page under natural light. On dark surfaces (Tide, Mangrove), interactive elements brighten toward Kelp (#2e7b78) on hover. The one exception: news cards receive a 1px border on hover to add tactile feedback without shadow.

---

## Imagery

Two distinct visual registers. The hero opens with a full-bleed atmospheric photograph of the field — coastline, estuary, or desert landscape of the Baja-Sonora region — establishing the physical reality of the work before any UI. This image occupies the full viewport; the headline and CTA overlay it with sufficient contrast treatment (dark scrim at 40% over the lower third). Beyond the hero, the site is photography-rich but structured: news cards carry cropped field photographs, the map section shows the 9-state coverage area, and the stats section uses simple line icons in `--color-tide`. No illustration. No stock photography of people in offices.

---

## Layout

Full-bleed hero at 100vh with centered headline and CTA pair. Below, content transitions to a max-width 1120px centered layout on `--color-dune`. Stats section uses an 8-column responsive grid on `--color-dune`. News section uses a 3-column card grid. Footer spans full width on `--color-mangrove`, with a CTA band above in `--color-tide`. Navigation is sticky at the top on `--color-mangrove`. All sections use a consistent left edge aligned to the content column — no centered text blocks except pull quotes.

---

## Signature Element

The single memorable design choice: **the stat figures use Fraunces optical-size serif at 56px, set directly on the page background with no containing card, no icon frame, no decorative underline — just the number, then the label, then empty space.** The numbers are the argument. Framing them would diminish them. This treatment echoes how field data appears in a scientific report: blunt, unapologetic, already justified by 35 years of work.

---

## Similar Organizations (Tone Reference)

- **The Nature Conservancy** — Similar light, photography-forward approach with a restrained green-dominant palette.
- **WWF** — Strong use of a single accent (orange) in a largely neutral palette; high photography density.
- **Rewilding Europe** — Contemporary serif + clean sans pairing; full-bleed imagery that centers on place, not people.
- **Monterey Bay Aquarium** — Teal brand color, clear typographic hierarchy, institutional authority without formality.

---

## Agent Prompt Guide

### Quick Color Reference
- **Page Background:** Dune (#f5f2ed)
- **Primary Brand:** Tide (#1b5c5a)
- **Primary Text:** Ink (#1e1c19)
- **Secondary Text:** Stone (#6b6760)
- **Primary CTA:** Amber (#e07c2a)
- **Border/Divider:** Fog (#e8e4df)
- **Dark Surface (Nav/Footer):** Mangrove (#0f3634)

### Example Component Prompts

1. `Build a hero section with a full-bleed field photograph of the Baja California coast. Overlay a dark scrim (rgba 0,0,0,0.35) on the lower half. Center a display headline at 64px Fraunces weight 300, color #ffffff. Below it a subheading at 20px DM Sans weight 400. Then two buttons side by side: primary Amber (#e07c2a) "Conoce nuestros proyectos" and secondary outline "Sobre nosotros" in white border.`

2. `Design a stats grid section on Dune (#f5f2ed) background. 4-column layout. Each cell: an icon in Tide (#1b5c5a) 32px, below it a stat number in Fraunces 600 56px Tide color, below it a label in DM Sans 600 uppercase 13px Stone (#6b6760) with 0.08em tracking. No card borders. 64px vertical padding per cell.`

3. `Create a news section eyebrow + headline: eyebrow "ÚLTIMAS NOTICIAS" in DM Sans 600 13px Amber (#e07c2a) uppercase with 0.1em tracking. Below it, section headline "Historias desde el campo" in Fraunces 400 42px Ink (#1e1c19). Then 3 cards on Salt (#ffffff) backgrounds, 2px radius, with a field photograph at top (no radius on image), date in Stone, title in Fraunces 400 20px Ink, hover state translates card –2px Y and shifts title to Kelp (#2e7b78).`

---

## CSS Custom Properties

```css
:root {
  /* Colors */
  --color-tide: #1b5c5a;
  --color-amber: #e07c2a;
  --color-amber-soft: #fbebd8;
  --color-dune: #f5f2ed;
  --color-salt: #ffffff;
  --color-mangrove: #0f3634;
  --color-kelp: #2e7b78;
  --color-fog: #e8e4df;
  --color-stone: #6b6760;
  --color-ink: #1e1c19;
  --color-pure-white: #ffffff;

  /* Typography — Font Families */
  --font-display: 'Fraunces', Georgia, 'Times New Roman', serif;
  --font-sans: 'DM Sans', 'Helvetica Neue', Arial, sans-serif;

  /* Typography — Scale */
  --text-caption: 13px;
  --leading-caption: 1.5;
  --tracking-caption: 0.02em;

  --text-label: 13px;
  --leading-label: 1.0;
  --tracking-label: 0.08em;

  --text-body-sm: 15px;
  --leading-body-sm: 1.6;
  --tracking-body-sm: 0.01em;

  --text-body: 17px;
  --leading-body: 1.65;
  --tracking-body: 0.005em;

  --text-subheading: 20px;
  --leading-subheading: 1.4;

  --text-heading-sm: 24px;
  --leading-heading-sm: 1.3;

  --text-heading: 32px;
  --leading-heading: 1.25;
  --tracking-heading: -0.005em;

  --text-heading-lg: 42px;
  --leading-heading-lg: 1.2;
  --tracking-heading-lg: -0.01em;

  --text-display: 64px;
  --leading-display: 1.1;
  --tracking-display: -0.015em;

  --text-stat: 56px;
  --leading-stat: 1.0;
  --tracking-stat: -0.02em;

  /* Typography — Weights */
  --font-weight-light: 300;
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;

  /* Spacing */
  --spacing-unit: 4px;
  --spacing-4: 4px;
  --spacing-8: 8px;
  --spacing-12: 12px;
  --spacing-16: 16px;
  --spacing-24: 24px;
  --spacing-32: 32px;
  --spacing-48: 48px;
  --spacing-64: 64px;
  --spacing-80: 80px;
  --spacing-96: 96px;
  --spacing-128: 128px;
  --spacing-160: 160px;

  /* Layout */
  --page-max-width: 1120px;
  --section-gap-sm: 96px;
  --section-gap-lg: 128px;
  --element-gap: 16px;
  --grid-columns: 12;
  --grid-gutter: 24px;

  /* Border Radius */
  --radius-none: 0px;
  --radius-sm: 2px;
  --radius-md: 4px;

  /* Named Radii */
  --radius-card: 2px;
  --radius-button: 4px;
  --radius-input: 4px;
  --radius-badge: 2px;
  --radius-image: 0px;

  /* Surfaces */
  --surface-base: #f5f2ed;
  --surface-raised: #ffffff;
  --surface-subtle: #e8e4df;
  --surface-dark: #1b5c5a;
  --surface-darkest: #0f3634;
}
```

### Tailwind v4

```css
@theme {
  /* Colors */
  --color-tide: #1b5c5a;
  --color-amber: #e07c2a;
  --color-amber-soft: #fbebd8;
  --color-dune: #f5f2ed;
  --color-salt: #ffffff;
  --color-mangrove: #0f3634;
  --color-kelp: #2e7b78;
  --color-fog: #e8e4df;
  --color-stone: #6b6760;
  --color-ink: #1e1c19;

  /* Typography */
  --font-display: 'Fraunces', Georgia, 'Times New Roman', serif;
  --font-sans: 'DM Sans', 'Helvetica Neue', Arial, sans-serif;

  /* Typography — Scale */
  --text-caption: 13px;
  --leading-caption: 1.5;
  --text-label: 13px;
  --text-body-sm: 15px;
  --leading-body-sm: 1.6;
  --text-body: 17px;
  --leading-body: 1.65;
  --text-subheading: 20px;
  --leading-subheading: 1.4;
  --text-heading-sm: 24px;
  --leading-heading-sm: 1.3;
  --text-heading: 32px;
  --leading-heading: 1.25;
  --text-heading-lg: 42px;
  --leading-heading-lg: 1.2;
  --text-display: 64px;
  --leading-display: 1.1;
  --text-stat: 56px;
  --leading-stat: 1.0;

  /* Spacing */
  --spacing-4: 4px;
  --spacing-8: 8px;
  --spacing-12: 12px;
  --spacing-16: 16px;
  --spacing-24: 24px;
  --spacing-32: 32px;
  --spacing-48: 48px;
  --spacing-64: 64px;
  --spacing-80: 80px;
  --spacing-96: 96px;
  --spacing-128: 128px;
  --spacing-160: 160px;

  /* Border Radius */
  --radius-sm: 2px;
  --radius-md: 4px;
}
```

### Google Fonts Import

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;1,9..144,300&display=swap" rel="stylesheet">
```

---

---

# Dashboard Extension
> Internal Monitoring & Reporting Tool

This section extends the base Pronatura Noroeste design system for the internal data tool. Where rules conflict, this section wins. The marketing site and the dashboard share brand DNA — color origin, typeface, spacing unit — but are different surfaces with different jobs.

**Core principle:** Staff use this tool for hours at a time. Every decision optimizes for low fatigue, fast scanning, and confident data entry. Brand expression is secondary to functional clarity.

---

## Overrides from Base System

| Property | Base (Marketing) | Dashboard |
|----------|-----------------|-----------|
| Primary font | Fraunces + DM Sans | DM Sans only |
| Default density | Spacious (96–128px section gaps) | Default (8–16px row gaps) |
| Primary CTA color | Amber (#e07c2a) | Tide (#1b5c5a) |
| Amber role | Primary action | Warning/caution state only |
| Page background | Dune (#f5f2ed) | Shell (#f0f0ed) — slightly cooler |
| Body text size | 17px | 14px |
| Section gaps | 96–128px | 24–48px |
| Shadows | None | One elevation shadow permitted |

---

## Dashboard Color Tokens

Extends base tokens. Do not redefine base tokens — reference them.

### Semantic / State Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| Action | `#1b5c5a` | `--color-action` | Alias for `--color-tide`. Primary buttons, active states, focus rings inside the dashboard. |
| Action Hover | `#164d4b` | `--color-action-hover` | Darkened Tide for button hover. |
| Action Soft | `#e8f3f2` | `--color-action-soft` | Light tint of Tide. Selected row backgrounds, active nav item fills. |
| Warning | `#e07c2a` | `--color-warning` | Alias for `--color-amber`. Caution badges, overdue indicators, pending review states. |
| Warning Soft | `#fbebd8` | `--color-warning-soft` | Alias for `--color-amber-soft`. Warning row highlights, caution banner backgrounds. |
| Danger | `#b83c2b` | `--color-danger` | Destructive actions (rare), critical alerts, validation errors. |
| Danger Soft | `#fbeae7` | `--color-danger-soft` | Error input backgrounds, error banner fills. |
| Success | `#2e7b78` | `--color-success` | Alias for `--color-kelp`. Confirmed entries, completed status, valid input feedback. |
| Success Soft | `#e5f3f2` | `--color-success-soft` | Success row highlights, confirmation banner backgrounds. |
| Info | `#4a6fa5` | `--color-info` | Informational banners, neutral status badges. |
| Info Soft | `#eaeff7` | `--color-info-soft` | Info banner backgrounds. |

### Dashboard Surface Tokens

| Name | Value | Token | Purpose |
|------|-------|-------|---------|
| Shell | `#f0f0ed` | `--surface-shell` | Outermost app background. Slightly cooler than Dune to reduce warmth fatigue. |
| Canvas | `#ffffff` | `--surface-canvas` | Main content area background. Tables, forms, cards live here. |
| Sidebar | `#1b5c5a` | `--surface-sidebar` | Left navigation panel. Uses Tide directly — the one place brand color dominates. |
| Sidebar Active | `#164d4b` | `--surface-sidebar-active` | Active nav item background on the sidebar. |
| Header | `#ffffff` | `--surface-header` | Top app bar. White with a 1px `--color-fog` bottom border. |
| Overlay | `rgba(15,18,17,0.48)` | `--surface-overlay` | Modal/drawer scrim. |

---

## Dashboard Typography

Fraunces is **retired inside the dashboard** except for the app name in the sidebar and top-level page titles. Everything else is DM Sans.

### Dashboard Type Scale

| Role | Size | Weight | Line Height | Usage |
|------|------|--------|-------------|-------|
| page-title | 22px | 600 | 1.3 | H1 of each dashboard page (e.g., "Entradas de Monitoreo") |
| section-title | 16px | 600 | 1.4 | Card headers, table section labels |
| label | 12px | 600 | 1.0 | Form labels, table column headers. Uppercase, 0.06em tracking. |
| body | 14px | 400 | 1.5 | Table cell content, form helper text, descriptions |
| body-strong | 14px | 500 | 1.5 | Emphasized cell values, key field values in forms |
| caption | 12px | 400 | 1.4 | Metadata, timestamps, secondary identifiers |
| button | 14px | 600 | 1.0 | All button labels. Sentence case, no uppercase. |
| input | 14px | 400 | 1.5 | Form input values and placeholders |
| badge | 11px | 600 | 1.0 | Status badges. Uppercase, 0.05em tracking. |

> Body text drops from 17px (marketing) to 14px here. At default zoom, 14px is the standard density for data-heavy tools. Going smaller (12–13px) creates strain over long sessions. Do not go below 13px for any content the user needs to read carefully.

---

## Dashboard Spacing & Density

### Density Scale

Three density modes. Use **default** for everything unless specified.

| Mode | Row Height | Cell Padding (V/H) | Input Height | Use Case |
|------|-----------|-------------------|--------------|----------|
| compact | 32px | 6px / 12px | 28px | High-row-count tables when user needs maximum data on screen |
| default | 40px | 10px / 16px | 36px | Standard — all tables, forms, most UI |
| spacious | 48px | 14px / 20px | 44px | Summary cards, stat callouts at page top |

### Component Spacing

| Element | Value | Token |
|---------|-------|-------|
| Sidebar width (expanded) | 232px | `--sidebar-width` |
| Sidebar width (collapsed) | 56px | `--sidebar-width-collapsed` |
| Top header height | 56px | `--header-height` |
| Page content padding (H) | 32px | `--content-padding-h` |
| Page content padding (V) | 32px | `--content-padding-v` |
| Card padding | 24px | `--card-padding` |
| Section gap (within page) | 24px | `--section-gap` |
| Form field gap | 20px | `--field-gap` |
| Table header padding | 10px 16px | `--table-header-padding` |
| Table cell padding (default) | 10px 16px | `--table-cell-padding` |

---

## Dashboard Shapes

| Element | Radius | Notes |
|---------|--------|-------|
| Cards / panels | 6px | Slightly more rounded than marketing to feel lighter inside a dense interface |
| Buttons | 4px | Inherits from base |
| Inputs / selects | 4px | Inherits from base |
| Badges / status tags | 3px | Near-flat, not pill |
| Modals | 8px | Slightly more rounded to distinguish from flat page surfaces |
| Tooltips | 4px | |
| Dropdown menus | 6px | |

> Do not use pill shapes (≥16px radius) on any dashboard component. A badge that looks like a pill reads as a marketing element, not a data label.

---

## Elevation

One shadow value only. Use it exclusively for floating elements.

```css
--shadow-float: 0 4px 16px rgba(15, 18, 17, 0.10);
--shadow-modal: 0 8px 32px rgba(15, 18, 17, 0.16);
```

| Element | Shadow | Notes |
|---------|--------|-------|
| Cards on Shell background | none | Cards on white canvas need no shadow — border suffices |
| Dropdown menus | `--shadow-float` | Must appear above page content |
| Modals / drawers | `--shadow-modal` | Combined with `--surface-overlay` scrim |
| Tooltips | `--shadow-float` | |
| Sticky table header | `0 2px 4px rgba(15,18,17,0.06)` | Subtle separator on scroll |
| Sidebar | none | Background color difference is sufficient |

---

## Dashboard Layout Shell

```
┌─────────────────────────────────────────────────────┐
│ HEADER (56px, --surface-header, 1px fog border bot) │
├────────────┬────────────────────────────────────────┤
│            │  PAGE HEADER (page title + actions)     │
│  SIDEBAR   │  ───────────────────────────────────── │
│  (232px,   │  CONTENT AREA                          │
│  --surface │  (fluid width, --surface-canvas,       │
│  -sidebar) │   32px padding H/V)                    │
│            │                                        │
│            │                                        │
└────────────┴────────────────────────────────────────┘
```

- Sidebar is fixed, not scrollable with content
- Content area scrolls independently
- Header is sticky — stays visible while content scrolls
- On screens < 768px: sidebar collapses to 56px icon-only rail

---

## Components

### Primary Action Button
**Role:** Submit entry, run report, confirm action.

`--color-action` (#1b5c5a) background, white text, 4px radius, 8px 16px padding. DM Sans 600 14px. Hover: `--color-action-hover`. Focus: 2px `--color-action` outline offset 2px. Disabled: 40% opacity, no pointer events.

> This is Tide, not Amber. Amber is a warning color inside the dashboard.

### Secondary Button
**Role:** Cancel, secondary options, non-destructive alternatives.

`--surface-canvas` background, 1px `--color-fog` border, `--color-ink` text. Same size as primary. Hover: `--surface-shell` background.

### Danger Button
**Role:** Only for irreversible actions, used sparingly.

`--color-danger` background, white text. Same size. Only appears in confirmation dialogs, never inline in tables.

### Data Table
**Role:** The primary UI component. Central to every page.

- Container: `--surface-canvas` background, 1px `--color-fog` border, 6px radius
- Column headers: DM Sans 600 12px, `--color-stone`, uppercase, 0.06em tracking. `--surface-shell` background. 1px `--color-fog` bottom border. Sortable columns show a sort icon on hover.
- Rows: 40px height (default density). `--color-ink` 14px body text. Alternating row tint: odd rows `--surface-canvas`, even rows `#fafaf8` (1% tint — barely visible, just enough to aid scanning).
- Selected row: `--color-action-soft` background, 1px `--color-action` left border.
- Hover row: `#f5f5f2` background.
- Cell padding: 10px 16px.
- Last column: always the action column (edit, view detail). Right-aligned. Icons only until hover reveals label.
- Empty state: centered in table body. Icon (outline, 32px, `--color-fog`), primary message in DM Sans 500 14px `--color-stone`, secondary message in 13px `--color-stone` 70%, optional action button.

### Status Badge
**Role:** Entry status — Completo, Pendiente, Revisión, Error.

11px DM Sans 600 uppercase, 0.05em tracking. 3px radius. 3px 8px padding. Color variants:

| Status | Background | Text |
|--------|-----------|------|
| Completo | `--color-success-soft` | `--color-success` |
| Pendiente | `--color-warning-soft` | `--color-warning` |
| Revisión | `--color-info-soft` | `--color-info` |
| Error | `--color-danger-soft` | `--color-danger` |

Never use colored backgrounds on the full table row to indicate status — that is visual noise at scale. Use badges in a dedicated Status column instead. The one exception: a `--color-warning-soft` row tint is acceptable for overdue entries where the user needs to notice the entire row at a glance.

### Form — Entry Modal / Slide-over
**Role:** New monitoring entry or editing an existing record.

Delivered as a right-side slide-over panel (480px wide) rather than a centered modal. Reason: the user often needs to reference the table behind the form while entering data. A slide-over keeps the table partially visible.

- Panel background: `--surface-canvas`
- Header: 56px, panel title in DM Sans 600 16px `--color-ink`, close icon right
- Body: 24px padding, fields stacked with 20px gap
- Footer: sticky at panel bottom, 1px `--color-fog` top border, 16px padding. Primary button right, secondary (Cancel) left.
- Form labels: DM Sans 600 12px `--color-stone` uppercase, 0.06em tracking, 6px below label to input
- Input fields: 36px height, 4px radius, 1px `--color-fog` border, `--surface-canvas` background. Focus: 2px `--color-action` outline offset –1px (replaces border on focus, do not stack both). Placeholder: `--color-stone` 60%.
- Helper text: 12px DM Sans 400 `--color-stone`, 4px below input
- Error text: 12px DM Sans 400 `--color-danger`, 4px below input. Input border becomes 1px `--color-danger` on error.
- Required indicator: `--color-danger` asterisk after label. No asterisk for optional fields; mark optional fields with "(opcional)" in Stone instead.

### Sidebar Navigation
**Role:** Primary app navigation.

`--surface-sidebar` (#1b5c5a) background, full viewport height minus header. Fixed position.

- App name: DM Sans 600 15px white, 24px from top, 20px left padding. Can use Fraunces here only.
- Nav items: 40px height, 20px left padding, DM Sans 500 14px white at 80% opacity. Icon (20px) left of label, 10px gap. Hover: white 100% opacity, `--surface-sidebar-active` background. Active: white 100% opacity, `--surface-sidebar-active` background, 3px `--color-amber` left border.
- Section dividers: 1px `rgba(255,255,255,0.12)` line with 8px vertical margin. Section label in DM Sans 600 11px white 45% opacity uppercase above the divider group.
- Collapsed state (56px): icons only, no labels. Tooltip on hover shows label.

> The sidebar uses Tide as its background — this is the one place the brand color dominates. It creates a clear structural separation between navigation and content without using a border or shadow. The amber left border on active items is the only warm element on an otherwise cool surface.

### Page Header
**Role:** Top of each content page. Title, subtitle, and page-level actions.

32px padding, `--surface-canvas` background, 1px `--color-fog` bottom border. 56px total height.

- Page title: DM Sans 600 22px `--color-ink`, left-aligned
- Subtitle (optional): DM Sans 400 14px `--color-stone`, 4px below title
- Actions: right-aligned, flex row. Primary button + optional secondary button + optional icon-only buttons (filter, export)

### Filter Bar
**Role:** Narrows table data. Sits between page header and table.

Full width of content area. `--surface-shell` background, 1px `--color-fog` border, 6px radius, 12px padding. Flex row with 12px gap between filter controls.

- Each filter: a labeled select or date input at default density (36px height)
- Active filter count badge: `--color-action-soft` background, `--color-action` text, shows total active filter count
- "Limpiar filtros" text button: DM Sans 500 14px `--color-action`, no border, no background. Only visible when at least one filter is active.
- Search input: 240px minimum width, left-most in the row. Magnifier icon inside left edge.

### Report Generator Panel
**Role:** Configure and trigger report output (PDF).

A full-width card on a dedicated Reports page. Not a modal. Reason: report configuration may have several parameters (date range, site, species filter, format) and deserves a real page, not a cramped overlay.

- Card: `--surface-canvas`, 6px radius, 1px `--color-fog` border, 24px padding
- Parameters in a 2-column form grid with 20px gap
- "Generar reporte" primary button at bottom right. Full width is not appropriate here — it should be a standard-width button.
- Below the form: a "Reportes recientes" table showing the last 10 generated reports with filename, date, parameters summary, and a download icon. This is read-only, compact density (32px rows).

### Empty State
**Role:** Table or page has no data matching current filters or no data yet.

Centered vertically and horizontally in the table body or content area. No illustration — a single outline icon (32px, `--color-fog`) from the Lucide or Phosphor icon set. Primary message: DM Sans 500 14px `--color-stone`. Secondary message: 13px `--color-stone` 65%. Optional action button below (e.g., "Nueva entrada").

### Toast Notification
**Role:** Non-blocking feedback after an action (saved, exported, error).

Fixed bottom-right, 320px wide, 6px radius, `--shadow-float`. Stacks upward if multiple. Auto-dismisses after 4 seconds (errors: 6 seconds, require manual dismiss).

| Type | Background | Left border (4px) | Icon color |
|------|-----------|-------------------|------------|
| Success | `--surface-canvas` | `--color-success` | `--color-success` |
| Warning | `--surface-canvas` | `--color-warning` | `--color-warning` |
| Error | `--surface-canvas` | `--color-danger` | `--color-danger` |
| Info | `--surface-canvas` | `--color-info` | `--color-info` |

White background for all — not colored fills. The left border carries the semantic weight. Colored fill toasts are visually alarming and distract from the work.

---

## Do's and Don'ts (Dashboard)

### Do
- Use `--color-action` (Tide) for all primary buttons inside the dashboard. Amber is a warning color here.
- Keep table rows at 40px default density. Only drop to compact when the user explicitly needs to see more rows.
- Use status badges in a dedicated column, not row-level background colors (except overdue warnings).
- Use a slide-over panel for entry forms so the table stays partially visible.
- Keep the sidebar Tide-colored and navigation labels in white — this is the brand's one dominant presence in the UI.
- Reserve Fraunces for the app name in the sidebar and page-level H1 titles only. Everything else is DM Sans.
- Write all form labels in uppercase 12px DM Sans 600 with tracking. Consistent with the marketing label style, legible at small sizes.
- Show an empty state in every table — never leave an empty container unexplained.

### Don't
- Don't use Amber (#e07c2a) for action buttons. It now means "this needs your attention."
- Don't use pill-shaped badges or buttons. 3–4px radius maximum.
- Don't use Fraunces in table headers, form labels, nav items, or buttons.
- Don't put destructive (danger) buttons inline in table rows. Require a confirmation step.
- Don't use colored row backgrounds for status — that's noise at scale. Use badges.
- Don't use the marketing section gaps (96–128px) anywhere inside the dashboard.
- Don't show shadows on cards sitting on the canvas — the 1px border is enough. Shadow only for floating elements (dropdowns, modals, tooltips).
- Don't use centered text layouts inside the dashboard except for empty states.

---

## Dashboard CSS Extension

```css
:root {
  /* Semantic Colors */
  --color-action: #1b5c5a;
  --color-action-hover: #164d4b;
  --color-action-soft: #e8f3f2;
  --color-warning: #e07c2a;
  --color-warning-soft: #fbebd8;
  --color-danger: #b83c2b;
  --color-danger-soft: #fbeae7;
  --color-success: #2e7b78;
  --color-success-soft: #e5f3f2;
  --color-info: #4a6fa5;
  --color-info-soft: #eaeff7;

  /* Dashboard Surfaces */
  --surface-shell: #f0f0ed;
  --surface-canvas: #ffffff;
  --surface-sidebar: #1b5c5a;
  --surface-sidebar-active: #164d4b;
  --surface-header: #ffffff;
  --surface-overlay: rgba(15, 18, 17, 0.48);

  /* Elevation */
  --shadow-float: 0 4px 16px rgba(15, 18, 17, 0.10);
  --shadow-modal: 0 8px 32px rgba(15, 18, 17, 0.16);
  --shadow-sticky: 0 2px 4px rgba(15, 18, 17, 0.06);

  /* Layout Shell */
  --sidebar-width: 232px;
  --sidebar-width-collapsed: 56px;
  --header-height: 56px;
  --content-padding-h: 32px;
  --content-padding-v: 32px;

  /* Component Spacing */
  --card-padding: 24px;
  --section-gap: 24px;
  --field-gap: 20px;
  --table-header-padding: 10px 16px;
  --table-cell-padding: 10px 16px;
  --table-cell-padding-compact: 6px 12px;

  /* Density — Row Heights */
  --row-height-compact: 32px;
  --row-height-default: 40px;
  --row-height-spacious: 48px;

  /* Density — Input Heights */
  --input-height-compact: 28px;
  --input-height-default: 36px;
  --input-height-spacious: 44px;

  /* Dashboard Typography */
  --text-page-title: 22px;
  --text-section-title: 16px;
  --text-dashboard-body: 14px;
  --text-dashboard-caption: 12px;
  --text-badge: 11px;
  --leading-dashboard-body: 1.5;
  --tracking-label-upper: 0.06em;
  --tracking-badge-upper: 0.05em;

  /* Border Radius — Dashboard */
  --radius-card-dashboard: 6px;
  --radius-modal: 8px;
  --radius-badge: 3px;
  --radius-dropdown: 6px;
  --radius-tooltip: 4px;
}
```
