# Accessibility Architecture & WCAG 2.1 AA Compliance

## 1. Principles & Standards
NyayaLens is designed to adhere to WCAG 2.1 Level AA accessibility standards.

## 2. Implemented Accessibility Controls
* **Semantic HTML**: Proper `<header>`, `<main>`, `<nav>`, `<footer>`, `<h1>`-`<h4>` heading hierarchy across all views.
* **Keyboard Navigability**: Every interactive element (tabs, document cards, citation badges, checkboxes) includes full keyboard focus management and responds to `Enter` and `Space`.
* **Visible Focus Indicators**: High-contrast, custom 2px focus outlines (`:focus-visible`) ensure keyboard users know their active cursor position.
* **Color Contrast**: Text and badge colors exceed the 4.5:1 minimum contrast ratio against dark backgrounds.
* **Reduced Motion**: Full support for `prefers-reduced-motion: reduce` query, zeroing out non-essential animations for users with vestibular sensitivities.
* **Screen Reader Descriptions**: ARIA roles, `aria-label`, and `aria-checked` states are provided for all asynchronous and custom controls.
