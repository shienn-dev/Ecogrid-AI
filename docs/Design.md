# EcoGrid AI — Design System

> Light enterprise, calm, data-first, premium, technical.  
> References: Stripe Dashboard (layout), Linear (navigation), IBM Carbon (analytics), Vercel (typography), Material 3 (color), Tailwind UI (components), Lucide/FontAwesome (icons).

---

## Principles

- **Data-first**: KPI numbers dominate, chrome recedes.
- **Calm**: Muted palette, no neon/glow, soft shadows only (`--shadow-card`).
- **Professional**: 4px spacing grid, 8/12/16 radius, consistent border `1px #e5e7eb`.
- **Honest**: No fake AI decorations, no glassmorphism, no cyber gradients.
- **Accessible**: Contrast AA, focus ring `2px #0f766e`, keyboard, aria-live, reduced-motion.

---

## Tokens (`frontend/css/tokens.css`)

### Surfaces
- `--bg: #f8fafc` (page), `--surface: #fff` (cards), `--surface-2: #f1f5f9`, `--border: #e5e7eb`

### Brand
- `--primary: #0f766e` (teal-700), `--primary-50: #f0fdfa`, `--secondary: #0e7490` (cyan-700)
- Hover `--primary-hover: #115e59`, ring `rgba(15,118,110,0.24)`

### Semantic
- Success `#059669` / bg `#ecfdf5`, Warning `#d97706` / bg `#fffbeb`, Danger `#dc2626` / bg `#fef2f2`, Info `#0284c7` / bg `#f0f9ff`

### Typography
- `--font-sans: Inter, system-ui` — headings 24/20/16, body 14, label 12 uppercase tracking 0.04em, tabular numbers on data (`font-variant-numeric: tabular-nums`)

### Motion
- `--ease-out: cubic-bezier(0.16,1,0.3,1)`, 150/250ms; `prefers-reduced-motion` disables animation.

### Shadows
- `--shadow-sm: 0 1px 2px rgba(15,23,42,.06)`, `--shadow-card: 0 1px 2px + 0 4px 12px rgba(15,23,42,.06)` — no glow.

### Layout
- `--container-max: 1280px`, `--header-h: 64px`, sticky config `top: calc(var(--header-h)+24px)` at ≥1024px.

---

## Color Usage

- KPI left accent 3px (`--kpi-accent`): energy/teal, cost/amber, carbon/slate, score/teal.
- Chart palette muted: `#0f766e, #0e7490, #475569, #d97706, #059669, #94a3b8`, grid `#f1f5f9`, tick `#64748b`.
- Insight left border 3px by type: danger `#dc2626`, warning `#d97706`, info `#0284c7`, success `#059669`.

---

## Components

### Topbar
- Sticky, `rgba(255,255,255,.92)` + `blur(8px)`, border-bottom, 36px brand-mark gradient teal→cyan, nav links 500 weight, badge Soon muted.

### Card
- `background var(--surface)`, `1px var(--border)`, `radius 16`, `shadow-card`, pad 24. Header flex with title (14 semibold) + subtitle (12 tertiary).

### KPI
- 4-col at 1280, 2-col at 640, 1-col mobile. Value 25.6px 700 tabular, sub 12 tertiary, foot icon 12 secondary.

### Device Card
- Border 1px, radius 12, pad 16, head dashed border, title 14 semibold with teal plug icon, remove 32px danger outline.

### Input
- 44px height, 1px border, radius 8, icon left 12px, badge right, focus `border teal + ring 3px`, error `border danger + ring red`.

### Ranking
- Item border + pad 16, top flex name 14 semibold / meta 12 tertiary tabular, badge rank 11 700, progress 8px track `surface-2` with gradient fill (low teal→cyan, mid cyan→amber, high amber→red) animated 700ms.

### Score
- 48px value 800, badge pill 12 700 with type colors, bar 6px track.

### Insight
- Left border 3px type, bg tinted, head 14 700 colored, desc 14 secondary.

### Charts
- Card with title 14 semibold, canvas 260px, tooltip tabular, grid `#f1f5f9`, reduced-motion disables.

### Empty / Loading
- Empty 56px icon in `surface-2` border, title 14 semibold, desc 14 secondary max 44ch. Skeleton shimmer `surface-2 → #e2e8f0`.

### Toast
- Fixed bottom-right, max 380px, card border + left accent 3px, shadow-lg.

---

## Layout

- **Header**: sticky 64px.
- **Page head**: title 24 700, desc 14 secondary 68ch.
- **App grid**: 1-col mobile, `420px | 1fr` at 1024px with sticky left. KPI 1→2→4 cols, analytics `1.2fr 0.8fr` at 1024, charts 1→2 at 768.
- **Responsive**: topbar hides nav at <1024, container pad 24→16, KPI value 22.4 on mobile, flow column at 640.

---

## Accessibility

- Labels `for`/`id`, `aria-describedby` errors, `aria-live=polite` on results, `role=status` on toasts, `aria-current=page`, keyboard add/remove, focus ring 2px teal offset 2, contrast AA, `prefers-reduced-motion`, tabular numbers.

---

## What Not To Do

- No `backdrop-filter: blur(16px)` cards, no orb glows, no neon gradients, no excessive shadows, no decorative glass.
- No cyberpunk, no AI startup generic dashboards.

---

## Implementation Files

- `frontend/css/tokens.css`, `base.css`, `layout.css`, `components.css`, `dashboard.css`, `responsive.css`
- `frontend/js/dashboard.js` + modules
- Icons: FontAwesome 6.5 (consider Lucide future)

