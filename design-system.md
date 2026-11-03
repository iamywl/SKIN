# Price Service Design System & Agent Guidelines

## 1. Core Principles & Philosophy
- **Aesthetic**: Data-dense, Utilitarian, Trustworthy, Financial terminal-grade.
- **Goal**: Maximize legibility and comparison speed per pixel. Eliminate consumer tech "AI fluff".
- **Strictly Prohibited**:
  - Arbitrary HEX values in component files (`text-[#...]`, `bg-[#...]`, inline `style={{ color: ... }}`).
  - Pastel card gradients, heavy drop shadows (`shadow-xl`), and neon glow effects.
  - Floating center-aligned cards that waste vertical scanning real estate.
  - Non-functional 3D assets, emojis as status markers, or decorative illustrations.

---

## 2. Semantic Color System (Strict Token Mapping)

*Rule: All components must use semantic utility classes. Raw HEX values will fail review. Colors must gracefully support both Light and Dark modes.*

| Semantic Role | Tailwind Light Class | Tailwind Dark Class | Purpose |
| :--- | :--- | :--- | :--- |
| **Surface Base** | `bg-white` | `dark:bg-slate-950` | Primary application canvas |
| **Surface Muted** | `bg-slate-50` | `dark:bg-slate-900` | Table headers, filter bar, badge base |
| **Surface Accent** | `bg-slate-100` | `dark:bg-slate-800` | Hover states, active row highlight |
| **Border Subtle** | `border-slate-200` | `dark:border-slate-800` | Card borders, table dividers, input borders |
| **Border Strong** | `border-slate-300` | `dark:border-slate-700` | Interactive control borders, active focus |
| **Text Primary** | `text-slate-900` | `dark:text-slate-100` | Product titles, main prices, table headers |
| **Text Muted** | `text-slate-500` | `dark:text-slate-400` | Timestamps, units, category paths, subtitles |
| **Trend: Drop / All-Time Low** | `text-emerald-700 bg-emerald-50 border-emerald-200` | `dark:text-emerald-400 dark:bg-emerald-950/40 dark:border-emerald-800` | Price decrease, lowest price record, buy signal |
| **Trend: Hike / Warning** | `text-rose-700 bg-rose-50 border-rose-200` | `dark:text-rose-400 dark:bg-rose-950/40 dark:border-rose-800` | Price increase, out of stock, overpriced |
| **Action Primary** | `bg-slate-900 text-white hover:bg-slate-800` | `dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-200` | Direct purchase links, alert setting CTA |

---

## 3. Typography & Numerical Rules

- **Base Font Family**: `Pretendard Variable`, `-apple-system`, `system-ui`, sans-serif.
- **Data & Price Font Family**: `Geist Mono`, `JetBrains Mono`, or Tailwind's `font-mono`.
- **Tabular Alignment**: Every price, discount rate, stock count, and timestamp **must** include `tabular-nums` to prevent layout shift during sorting or live polling.

### Scale & Hierarchy
- **Header 1 (Page / Product Title)**: `text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100`
- **Section Title**: `text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wide`
- **Primary Deal Price**: `text-xl font-bold font-mono tracking-tight tabular-nums text-slate-900 dark:text-slate-100`
- **Original / MSRP Price**: `text-xs font-mono line-through text-slate-400 dark:text-slate-500 tabular-nums`
- **Table Cell Text**: `text-sm leading-5 text-slate-700 dark:text-slate-300`
- **Metadata / Unit**: `text-xs text-slate-500 dark:text-slate-400 font-normal`

---

## 4. Spacing, Borders, and Structure

- **Base Unit**: 4px standard grid (`p-1`, `p-2`, `p-3`, `p-4`, `p-6`). Avoid arbitrary spacing (`p-[13px]`).
- **Corner Radii**: Strictly bounded to small radii.
  - Buttons / Inputs / Badges: `rounded-md` (6px)
  - Cards / Tables / Modals: `rounded-lg` (8px)
  - Never use: `rounded-2xl`, `rounded-3xl`, or `rounded-full` (except for 1:1 circular avatar icons).
- **Shadows**:
  - Default: `shadow-none` with explicit `border border-slate-200 dark:border-slate-800`.
  - Dropdown / Flyouts: `shadow-sm` or `shadow-md` max. Never use heavy diffuse shadows.

---

## 5. Component Construction Rules

### A. Price Comparison Data Table
- Headers: `h-9 px-3 text-xs font-medium uppercase text-slate-500 bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800`
- Rows: `h-11 px-3 border-b border-slate-100 dark:border-slate-800/60 hover:bg-slate-50/80 dark:hover:bg-slate-900/50 transition-colors`
- **Alignment Rule**:
  - Retailer name, status, product specs: **Left-aligned (`text-left`)**
  - Historical dates, delivery conditions: **Center-aligned (`text-center`)**
  - Current price, discount rate, price difference: **Right-aligned (`text-right font-mono tabular-nums`)**

### B. Status Badges & Price Tags
- Structure: Fixed compact padding (`px-1.5 py-0.5 text-xs font-medium border rounded-md`).
- Example Drop Badge: `<span className="inline-flex items-center text-xs font-mono font-medium px-1.5 py-0.5 rounded-md border border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-400 tabular-nums">-14.2%</span>`

### C. Price Charts & Sparklines
- Chart Line: Clean 1.5px stroke width. No glowing gradient under-fills.
- Reference Line: Dashed 1px line (`stroke-slate-300 dark:stroke-slate-700`) for "30-day average" or "All-time low".
- Tooltip: Compact box (`bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-2 shadow-sm rounded-md text-xs font-mono`).

---

## 6. Nationwide Expansion Agent Guidelines
- To add new regions (e.g., Seoul Gangnam, Busan Seomyeon), agents must follow `expand_region.py`.
- The new dataset must preserve this terminal-grade utilitarian UI and strict tabular alignment.

---

## 7. Implementation Checklist for Agents
Before generating or refactoring any component:
1. [x] Did I remove any hardcoded `#hex` or `rgb()` color codes?
2. [x] Are all numeric and price figures using `tabular-nums font-mono`?
3. [x] Are table numeric columns strictly right-aligned?
4. [x] Are borders thin (`border border-slate-200 dark:border-slate-800`) and shadows suppressed (`shadow-none` or `shadow-sm`)?
5. [x] Does this layout prioritize immediate scanning over decorative space?
