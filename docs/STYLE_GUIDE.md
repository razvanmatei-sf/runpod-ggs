# SF AI Workbench Style Guide

> Design system inspired by RunPod's console UI (as of 2025)

## Color Palette

### Background Colors

| Variable | Hex | Usage |
|----------|-----|-------|
| `--bg-primary` | `#121212` | Main page background |
| `--bg-secondary` | `#181818` | Sidebar, header, cards |
| `--bg-tertiary` | `#1f1f1f` | Elevated cards, inputs |
| `--bg-hover` | `rgba(255,255,255,0.05)` | Hover states |
| `--bg-active` | `rgba(255,255,255,0.08)` | Active/selected states |

### Text Colors

| Variable | Hex/Value | Usage |
|----------|-----------|-------|
| `--text-primary` | `#ffffff` | Headings, important text |
| `--text-secondary` | `rgba(255,255,255,0.70)` | Body text, descriptions |
| `--text-muted` | `rgba(255,255,255,0.50)` | Labels, placeholders, hints |
| `--text-disabled` | `rgba(255,255,255,0.30)` | Disabled states |

### Accent Colors

| Variable | Hex | Usage |
|----------|-----|-------|
| `--accent-primary` | `#7C3AED` | Primary buttons, links, active states |
| `--accent-primary-hover` | `#6D28D9` | Primary button hover |
| `--accent-green` | `#22C55E` | Success, running status, create actions |
| `--accent-red` | `#EF4444` | Error, delete actions, stopped status |
| `--accent-orange` | `#F59E0B` | Warning, starting status |
| `--accent-blue` | `#3B82F6` | Info, links (alternative) |

### Border Colors

| Variable | Value | Usage |
|----------|-------|-------|
| `--border-default` | `rgba(255,255,255,0.08)` | Default borders |
| `--border-subtle` | `rgba(255,255,255,0.05)` | Subtle dividers |
| `--border-focus` | `#7C3AED` | Focus rings on inputs |

---

## Typography

### Font Family

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Font Sizes

| Name | Size | Usage |
|------|------|-------|
| `--text-xs` | `12px` | Badges, labels |
| `--text-sm` | `14px` | Body text, buttons |
| `--text-base` | `16px` | Default, inputs |
| `--text-lg` | `18px` | Section headers |
| `--text-xl` | `20px` | Page subtitles |
| `--text-2xl` | `24px` | Page titles |

### Font Weights

| Name | Weight | Usage |
|------|--------|-------|
| `--font-normal` | `400` | Body text |
| `--font-medium` | `500` | Buttons, labels |
| `--font-semibold` | `600` | Headers, emphasis |

---

## Spacing

Based on 4px grid:

| Name | Value |
|------|-------|
| `--space-1` | `4px` |
| `--space-2` | `8px` |
| `--space-3` | `12px` |
| `--space-4` | `16px` |
| `--space-5` | `20px` |
| `--space-6` | `24px` |
| `--space-8` | `32px` |
| `--space-10` | `40px` |

---

## Border Radius

| Name | Value | Usage |
|------|-------|-------|
| `--radius-sm` | `4px` | Small elements, badges |
| `--radius-md` | `6px` | Buttons, inputs |
| `--radius-lg` | `8px` | Cards, panels |
| `--radius-xl` | `12px` | Modals, large cards |
| `--radius-full` | `9999px` | Pills, avatars |

---

## Components

### Primary Button

```css
.btn-primary {
    background: var(--accent-primary);
    color: white;
    padding: 10px 16px;
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    border: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.btn-primary:hover {
    background: var(--accent-primary-hover);
}
```

**Pattern:** Action buttons often have a `+` icon prefix (e.g., "+ Deploy", "+ Create Secret")

### Secondary Button

```css
.btn-secondary {
    background: transparent;
    color: var(--text-secondary);
    padding: 10px 16px;
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    border: 1px solid var(--border-default);
    cursor: pointer;
}

.btn-secondary:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
}
```

### Danger Button

```css
.btn-danger {
    background: var(--accent-red);
    color: white;
    /* Same padding/radius as primary */
}
```

### Icon Button

```css
.btn-icon {
    width: 32px;
    height: 32px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: var(--radius-md);
    color: var(--text-muted);
    cursor: pointer;
}

.btn-icon:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
}

.btn-icon.danger:hover {
    background: rgba(239, 68, 68, 0.1);
    color: var(--accent-red);
}
```

### Input Fields

```css
.input {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: 10px 12px;
    font-size: var(--text-sm);
    color: var(--text-primary);
    width: 100%;
}

.input::placeholder {
    color: var(--text-muted);
}

.input:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 1px var(--accent-primary);
}
```

### Cards/Panels

```css
.card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
}
```

### Status Badges

```css
.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
}

.badge-default {
    background: rgba(255,255,255,0.08);
    color: var(--text-secondary);
}

.badge-success {
    background: rgba(34, 197, 94, 0.15);
    color: var(--accent-green);
}

.badge-danger {
    background: rgba(239, 68, 68, 0.15);
    color: var(--accent-red);
}
```

### Status Dot

```css
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.status-dot.running {
    background: var(--accent-green);
}

.status-dot.stopped {
    background: var(--text-muted);
}

.status-dot.starting {
    background: var(--accent-orange);
    animation: pulse 1.5s infinite;
}
```

---

## Layout

### Sidebar

- **Width:** `220px`
- **Background:** `var(--bg-secondary)`
- **Border:** `1px solid var(--border-default)` on right edge
- **Structure:**
  - Logo/brand at top
  - Grouped navigation sections with collapsible headers
  - Section headers are muted uppercase text
  - Nav items have icon + text
  - Active item: subtle background + left border accent (purple)

### Header

- **Height:** `56px`
- **Background:** `var(--bg-secondary)`
- **Border:** `1px solid var(--border-default)` on bottom
- **Contains:** Breadcrumbs (left), actions/user (right)

### Content Area

- **Background:** `var(--bg-primary)`
- **Padding:** `32px 40px`
- **Max width:** Consider `1400px` for readability

---

## Tables

- No visible row borders - use spacing and hover states
- Header row: muted text, uppercase optional
- Rows: subtle hover background
- Action buttons appear on row hover (or always visible)

```css
.table-row:hover {
    background: var(--bg-hover);
}
```

---

## Empty States

- Centered content
- Large heading (normal weight)
- Descriptive text in muted color
- Optional action button or link
- Links are purple with external icon when applicable

---

## Shadows

Minimal shadow usage. When needed:

```css
--shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
--shadow-md: 0 4px 6px rgba(0,0,0,0.3);
--shadow-lg: 0 10px 15px rgba(0,0,0,0.3);
```

---

## Transitions

Default transition for interactive elements:

```css
transition: all 0.15s ease;
```

Or for specific properties:

```css
transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
```

---

## Icons

- Style: Line icons (not filled)
- Stroke width: `1.5` to `2`
- Size: `16px` (small), `20px` (default), `24px` (large)
- Color: Inherits from text color

---

## Accessibility

- Focus states should be visible (use `--border-focus` color)
- Maintain sufficient color contrast
- Interactive elements should have hover states
- Use `aria-label` for icon-only buttons