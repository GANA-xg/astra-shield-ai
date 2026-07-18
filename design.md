# Astra Shield Design System

## Overview

Adapted from Airbnb's design language for a cybersecurity platform. The core principles — generous whitespace, single accent color, clean typography hierarchy, soft shapes, and photography-first visual weight — are preserved while adapting to a dark security-optimized canvas.

### Design Philosophy

- **Single accent voltage:** Rausch red (#ff385c) carries every primary CTA, risk indicators, and brand moments. Used sparingly — most surfaces are dark neutral with one or two accent moments per viewport.
- **Generous whitespace:** 64px vertical sections, 16-24px card gutters. Dense information displays balanced with breathing room.
- **Soft shapes:** 8px radius for buttons, 14px for cards, fully rounded for pills and badges. No hard corners anywhere.
- **Modest typography weights:** Display headlines at 22-28px weight 500-600, body at 400. Trust signal numbers (risk scores, ratings) get the loudest treatment at 64px/700.
- **Single shadow tier:** `rgba(0,0,0,0.02) 0 0 0 1px, rgba(0,0,0,0.04) 0 2px 6px, rgba(0,0,0,0.1) 0 4px 8px` — applied on hover and dropdowns only.

## Colors

### Brand & Accent
- **Rausch** (#ff385c): Primary accent. Risk warnings, primary CTAs, heart states, brand links.
- **Rausch Active** (#e00b41): Press/pointer-down variant.
- **Rausch Disabled** (#ffd1da): Pale tint for disabled CTAs.

### Surface (Dark Theme)
- **Canvas** (#0f0f0f): Default page floor. Deep black for security monitoring.
- **Surface Soft** (#1a1a1a): Lightest fill — disabled fields, hover backgrounds.
- **Surface Strong** (#222222): Icon-button surfaces, elevated cards.
- **Surface Elevated** (#2a2a2a): Dropdowns, modals, sticky elements.

### Hairlines & Borders
- **Hairline** (#333333): Default 1px border — dividers, card borders, input outlines.
- **Hairline Soft** (#2a2a2a): Lighter divider for long-scrolling sections.
- **Border Strong** (#444444): Heavier stroke for focused/disabled states.

### Text
- **Ink** (#f5f5f5): Dominant text on dark surfaces. Headlines, body, nav links.
- **Body** (#cccccc): Secondary running text for long-form copy.
- **Muted** (#888888): Subtitles, inactive labels, placeholder text.
- **Muted Soft** (#666666): Disabled text.
- **On Primary** (#ffffff): White text on Rausch CTAs.

### Semantic
- **Error** (#ff385c): Risk indicators, error states. Matches Rausch for consistency.
- **Warning** (#f59e0b): Medium risk, caution states.
- **Success** (#10b981): Low risk, safe states.
- **Info** (#3b82f6): Informational highlights.

### Risk Level Mapping
- **CRITICAL:** #ff385c (Rausch red)
- **HIGH:** #f97316 (Orange)
- **MEDIUM:** #f59e0b (Amber)
- **LOW:** #10b981 (Emerald)

## Typography

### Font Family
**Inter** as primary (closest open-source substitute for Airbnb Cereal). Fallbacks: `-apple-system, system-ui, Roboto, "Helvetica Neue", sans-serif`.

### Hierarchy

| Token | Size | Weight | Line Height | Letter Spacing | Use |
|---|---|---|---|---|---|
| `rating-display` | 64px | 700 | 1.1 | -1px | Risk score display, key metrics |
| `display-xl` | 28px | 700 | 1.43 | 0 | Page titles, hero headlines |
| `display-lg` | 22px | 500 | 1.18 | -0.44px | Section headers, card titles |
| `display-md` | 21px | 700 | 1.43 | 0 | Sub-section heads |
| `display-sm` | 20px | 600 | 1.20 | -0.18px | Card titles, modal headers |
| `title-md` | 16px | 600 | 1.25 | 0 | Nav items, list titles |
| `title-sm` | 16px | 500 | 1.25 | 0 | Column heads, sidebar labels |
| `body-md` | 16px | 400 | 1.5 | 0 | Default body text |
| `body-sm` | 14px | 400 | 1.43 | 0 | Card meta, dates, prices |
| `caption` | 14px | 500 | 1.29 | 0 | Labels, field labels |
| `caption-sm` | 13px | 400 | 1.23 | 0 | Legal, timestamps |
| `badge` | 11px | 600 | 1.18 | 0 | Floating badges |
| `micro-label` | 12px | 700 | 1.33 | 0 | Status indicators |
| `uppercase-tag` | 8px | 700 | 1.25 | 0.32px | "NEW" badges, category tags |
| `button-md` | 16px | 500 | 1.25 | 0 | Primary CTA labels |
| `button-sm` | 14px | 500 | 1.29 | 0 | Pill button labels |
| `link` | 14px | 400 | 1.43 | 0 | Inline body links |
| `nav-link` | 16px | 600 | 1.25 | 0 | Top nav labels |

### Principles
- Display weights stay modest — photography and data visualization carry visual hierarchy.
- Risk scores and critical metrics get the loudest typographic treatment (rating-display).
- Body text at 400 weight for readability during long monitoring sessions.

## Spacing System

- **Base unit:** 4px (with 2px micro-step).
- **Tokens:**
  - `xxs`: 2px
  - `xs`: 4px
  - `sm`: 8px
  - `md`: 12px
  - `base`: 16px
  - `lg`: 24px
  - `xl`: 32px
  - `xxl`: 48px
  - `section`: 64px

### Usage
- **Section padding:** 64px vertical for major page bands.
- **Card internal padding:** 24px for dashboard cards, 16px for compact cards.
- **Gutters:** 16px between grid items, 24px inside sidebars.

## Border Radius

- **Buttons:** 8px (`rounded.sm`)
- **Cards:** 14px (`rounded.md`)
- **Pills/Badges:** 9999px (`rounded.full`)
- **Modal corners:** 16px (`rounded.lg`)

## Shadows

- **Flat (no shadow):** 95% of surfaces — body, hero, footer.
- **Card hover:** `box-shadow: rgba(0, 0, 0, 0.02) 0 0 0 1px, rgba(0, 0, 0, 0.04) 0 2px 6px 0, rgba(0, 0, 0, 0.1) 0 4px 8px 0` — applied on hover and dropdowns.
- **Modal scrim:** #000000 at 50% opacity.

## Components

### Buttons
- **button-primary:** Rausch fill, white text, 8px radius, 14×24px padding, 48px height, weight 500.
- **button-primary-active:** Background flips to Rausch Active (#e00b41).
- **button-primary-disabled:** Pale Rausch tint (#ffd1da), white text, cursor not-allowed.
- **button-secondary:** Surface fill with ink text and 1px border outline, 8px radius.
- **button-tertiary-text:** Plain ink text, no surface, no border. Underlined on hover.
- **button-pill:** Pill-shaped accent CTA — 9999px radius, 10×20px padding, 14px label.

### Cards
- **metric-card:** Photo/data-first card. 14px radius, surface-strong background, hover elevation.
- **stat-card:** Compact metric display with icon, value, and label.
- **detection-card:** Risk-focused card with severity indicator, input preview, and action buttons.

### Navigation
- **top-nav:** Surface background, 64px height, 1px bottom hairline.
- **sidebar-nav:** Surface background, 240px width, 1px right hairline.
- **nav-item:** 8px radius, active state uses accent underline or fill.

### Forms
- **text-input:** Surface fill, 1px border, 8px radius, 48px height. Focus: 2px accent border.
- **textarea:** Surface fill, 1px border, 8px radius, multi-line. Focus: 2px accent border.
- **select:** Surface fill, 1px border, 8px radius, 48px height.

### Data Display
- **risk-badge:** Pill-shaped badge with semantic color mapping.
- **risk-meter:** Horizontal progress bar with gradient fill.
- **data-table:** Striped rows, hover highlight, sortable headers.

## Responsive Behavior

| Name | Width | Key Changes |
|---|---|---|
| Mobile | < 744px | Sidebar collapses to hamburger; cards stack 1-up; tables scroll horizontally. |
| Tablet | 744–1128px | Sidebar visible; cards 2-up; content area fills remaining width. |
| Desktop | 1128–1440px | Full sidebar; cards 3-4 up; optimal data density. |
| Wide | > 1440px | Content width caps at 1440px; gutters absorb the rest. |

### Touch Targets
- Primary CTAs: minimum 48×48px (WCAG AAA).
- Nav items: 44×44px minimum.
- Interactive elements: 40×40px minimum.
