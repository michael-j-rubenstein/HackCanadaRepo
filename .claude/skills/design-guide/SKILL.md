---
name: mobile-ui
description: "Design and build clean, premium mobile app UI mockups as interactive HTML in the style of Wealthsimple. Use for any mobile UI, mockup, prototype, app screen, dashboard, or phone-frame UI request."
---

# Mobile UI Skill

Produces a **375×812px phone-frame HTML mockup** with:

- Dark mode AND light mode — both fully designed, toggle between them instantly
- SF Pro system font stack (feels native on Apple devices)
- Single accent color (`#10B981` teal-green default, easily swappable)
- Interactive color picker panel (preset swatches + hex input)
- Clean card-based layout with subtle borders and no glow effects

Default starting mode depends on context:

- User says "dark", "Wealthsimple-style", or nothing specified → **start in dark mode**
- User says "light", "clean white", "bright" → **start in light mode**
- Either way, the toggle is always present so the user can flip between them

---

## Design Philosophy

This style is inspired by Wealthsimple's UI: confident, quiet, premium. Works equally well
in both dark and light modes because the design language — not the darkness — is what makes
it feel premium.

**Rules to never break:**

1. No gradients on the accent color — flat fill only
2. No glows, shadows, or blur on interactive elements
3. One accent color, used for: progress indicators, active states, badges, CTAs only
4. Typography is weight-based hierarchy — no decorative fonts
5. Cards lift slightly from the background via color step, not shadow
6. Borders are thin (1px) and low-contrast — structural, not decorative
7. Icons are line-only SVG, no fill, stroke-width 1.7–1.8

---

## Color Tokens

### Dark Mode

```css
--bg: #191917; /* phone background */
--surface: #202020; /* nav bar, bottom bar */
--card: #252523; /* cards, stat boxes */
--border: #2c2c2a; /* all borders */
--accent: #10b981; /* THE accent */
--accent-dim: rgba(16, 185, 129, 0.13);
--text-primary: #f0efe9;
--text-secondary: #a09e96;
--text-muted: #5c5a54;
--ring-track: #2c2c2a;
--panel-bg: #161614;
--panel-border: #2a2a28;
--input-bg: #252523;
--input-border: #2c2c2a;
--tooltip-bg: #2a2a28;
```

Page background (outside phone): `#111110`

### Light Mode

```css
--bg: #fafaf9;
--surface: #f2f1ef;
--card: #ffffff;
--border: #e4e2dc;
--accent: #10b981; /* same accent in both modes */
--accent-dim: rgba(16, 185, 129, 0.13);
--text-primary: #1a1a18;
--text-secondary: #6b6860;
--text-muted: #a8a49c;
--ring-track: #e4e2dc;
--panel-bg: #f5f4f2;
--panel-border: #e0ded8;
--input-bg: #eceae6;
--input-border: #d8d6d0;
--tooltip-bg: #1a1a18;
```

Page background (outside phone): `#E8E6E1`

Apply light mode by adding class `light` to both `<html>` and `<body>`.

---

## Typography

```css
font-family:
  -apple-system, "SF Pro Display", "SF Pro Text", BlinkMacSystemFont,
  "Helvetica Neue", sans-serif;
```

| Use                    | Size | Weight  | Letter-spacing |
| ---------------------- | ---- | ------- | -------------- |
| Big number / hero stat | 36px | 700     | -0.04em        |
| Section heading        | 22px | 700     | -0.03em        |
| Card label (uppercase) | 11px | 400–500 | +0.02em        |
| Row / body text        | 14px | 500     | -0.01em        |
| Meta / muted           | 12px | 400     | normal         |
| Nav label              | 10px | 400     | +0.02em        |

---

## Layout Structure

```
body (flex row, centered, gap 32px)
├── .phone (375×812, border-radius 46px)
│   ├── .status-bar
│   ├── .scroll (flex:1, overflow-y auto, no scrollbar)
│   │   ├── .header (greeting + avatar)
│   │   ├── .hero-card (ring + big stat)
│   │   ├── .stats-row (2-col grid)
│   │   ├── .chart-card
│   │   └── .workout-list (divider-separated rows)
│   └── .bottom-nav
└── .panel (color picker, 230px wide, align-self: center)
```

---

## Component Patterns

### Hero Card (ring + number)

- SVG ring: `r=42`, `stroke-width=7`, `stroke-dasharray=264`
- Adjust `stroke-dashoffset` to control fill (0 = full, 264 = empty)
- Ring track stroke must be set as SVG attribute (not CSS var) so JS can swap it on mode change
- Large number: 36px, weight 700, letter-spacing -0.04em
- Progress bar: `height: 4px`, fill = `var(--accent)`

### Stat Cards (2-col grid)

- Label: uppercase, 11px, `var(--text-muted)`
- Value: 24px bold, -0.04em tracking
- Unit suffix: 13px, `var(--text-secondary)`, `margin-left: 2px`
- Badge: `background: var(--accent-dim); color: var(--accent)` pill, `border-radius: 999px`

### Chart Bars

- Inactive: `var(--border)` fill
- Active bar: `var(--accent)` — mark column with class `active`
- Day labels: 10px, `var(--text-muted)`

### Workout / List Rows

- Transparent background rows separated by `border-bottom: 1px solid var(--border)`
- Left icon: 38px circle, `background: var(--card)`, `border: 1px solid var(--border)`, line SVG inside
- Last row: `border-bottom: none`

### Bottom Nav

- `background: var(--surface)`, `border-top: 1px solid var(--border)`
- Active: label + SVG stroke = `var(--accent)`
- Inactive SVGs: `stroke: var(--text-muted); fill: none; stroke-width: 1.7`

---

## Dark/Light Mode Toggle

The toggle sits at the top of the `.panel`. On click it:

1. Toggles `light` class on `<html>` and `<body>`
2. Toggles `.on` class on the track element (slides the thumb via CSS transform)
3. Swaps ring track SVG stroke attribute directly (CSS vars don't reach SVG attributes)
4. Updates icon (🌙 / ☀️) and label text

```js
toggle.addEventListener("click", () => {
  isLight = !isLight;
  document.documentElement.classList.toggle("light", isLight);
  document.body.classList.toggle("light", isLight);
  toggle.classList.toggle("on", isLight);
  modeIcon.textContent = isLight ? "☀️" : "🌙";
  modeLabelText.textContent = isLight ? "Light mode" : "Dark mode";
  ringTrackEl.setAttribute("stroke", isLight ? "#E4E2DC" : "#2C2C2A");
});
```

Toggle track CSS:

```css
.toggle-track {
  width: 44px;
  height: 26px;
  background: var(--border);
  border-radius: 999px;
  position: relative;
  cursor: pointer;
}
.toggle-track.on {
  background: var(--accent);
}
.toggle-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
}
.toggle-track.on .toggle-thumb {
  transform: translateX(18px);
}
```

All phone elements use `transition: color 0.3s, background 0.3s, border-color 0.3s` for smooth switching.

---

## Color Picker Panel

Panel order (top to bottom):

1. **"Appearance"** section label
2. Mode toggle row (icon + label + iOS toggle)
3. Divider
4. **"Accent Color"** section label
5. Hex input row (color preview dot + `#` + text input)
6. Apply button (full width, accent background)
7. Divider
8. Swatch groups: Greens → Blues → Warm → Neutral

**Preset swatches:**

| Group   | Hex       | Name       |
| ------- | --------- | ---------- |
| Greens  | `#10B981` | Teal       |
|         | `#16A34A` | Forest     |
|         | `#22C55E` | Emerald    |
|         | `#4ADE80` | Mint       |
|         | `#C6F135` | Lime       |
| Blues   | `#3B82F6` | Blue       |
|         | `#06B6D4` | Cyan       |
|         | `#6366F1` | Indigo     |
|         | `#38BDF8` | Sky        |
|         | `#818CF8` | Periwinkle |
| Warm    | `#F97316` | Orange     |
|         | `#EF4444` | Red        |
|         | `#F59E0B` | Amber      |
|         | `#EC4899` | Pink       |
|         | `#FBBF24` | Gold       |
| Neutral | `#A3A3A3` | Silver     |
|         | `#D4D4D4` | Light      |
|         | `#94A3B8` | Slate      |
|         | `#CBD5E1` | Mist       |
|         | `#F1F5F9` | White      |

**`applyAccent(hex)` updates:** `--accent`, `--accent-dim`, ring SVG stroke, hex preview dot,
apply button bg, selected swatch ring. Hex input auto-applies at 6 chars typed.

---

## Adapting to New App Types

Swap content while keeping all design tokens identical:

- **Finance** → balance as hero number, transaction list rows, sparkline chart
- **Fitness** → steps/calories/time, ring progress, workout rows ✓ (reference app)
- **Productivity** → task count, completion ring, task list rows
- **Food/Lifestyle** → streak count, meal log rows, weekly bar chart

Suggested default accent by category:

- Finance → `#10B981` (teal) or `#3B82F6` (blue)
- Fitness → `#10B981` (teal) or `#22C55E` (emerald)
- Productivity → `#6366F1` (indigo) or `#3B82F6` (blue)
- Food/Lifestyle → `#F97316` (orange) or `#EC4899` (pink)

---

## Full Working Reference

See `/references/pulse-app.html` for the complete working implementation (fitness app).
Use it as a copy-paste starting point and modify the content sections only.
