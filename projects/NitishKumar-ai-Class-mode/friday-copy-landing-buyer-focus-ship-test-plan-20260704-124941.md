# Ship Test Plan — copy/landing-buyer-focus

Branch: copy/landing-buyer-focus (working tree = shipped content)
Date: 2026-07-04
Scope: Marketing landing-page rework (buyer/principal-focused copy + new interactive demos)

## Affected Pages/Routes

- `/` — landing page (unauthenticated only; authed users redirect to /dashboard, client/src/App.tsx:311)
- `client/index.html` — new `<title>` and meta description (affects every route's initial load / SEO)

## Key Interactions to Verify

- **AI-tutor WhatsApp demo** (`DemoWidget`, cta.tsx): auto-plays a 4-message scripted conversation on load (timers at 1s/3.5s/5.5s/7.5s/9.5s/12.5s); clicking a study topic cancels pending timers and restarts the thread; "typing…" header + TypingDots bubble alternate between school/parent.
- **Contact form validation** (`ContactForm`, cta.tsx): requires trimmed name AND (phone OR email); success resets all six fields. KNOWN BUG: sonner toasts never render (no sonner `<Toaster/>` mounted) — user sees no feedback. KNOWN GAP: form data is never sent to any backend.
- **Nav anchors**: navbar links #demo/#journey/#for-schools/#pricing/#contact; hero CTAs scroll to #contact and #demo; Pricing "Request a pilot" and Journey "Start with step one →" scroll to #contact; Sign in → /login.
- **Theme toggle**: `ThemeToggle` in navbar (desktop only) — verify demo widgets' hardcoded WhatsApp greens/zinc palettes stay legible in dark mode.
- **Hero storytelling mockup**: 4-step loop every 4.5s (present→absent click→WhatsApp alert→mum reply + dashboard delta flip).

## Edge Cases

- Switch demo topic mid-typing-indicator: pending setTimeouts from old topic must not resurrect old messages (covered: e2e "switching topic mid-conversation").
- Rapid-fire topic clicks: timers cleared each click via `clearTimers()`; keyed AnimatePresence entries (`${activeId}-${i}`) must not collide.
- Unmount during animation (navigate to /login mid-demo): cleanup in useEffect return — not directly assertable without component-test infra (absent by design).
- Whitespace-only name in contact form → rejected (covered).
- Name + email but no phone → accepted (covered).
- Mobile menu (375px): toggle open, link tap closes menu and scrolls (covered); mobile Sign in button variant untested.
- Chat auto-scroll: newest bubble kept in view via scrollTo on shownCount/typingFrom — visual, untested.

## Critical Paths

1. **Hero CTA → contact form scroll → valid submit → form resets** (primary conversion path; covered by e2e/web/landing.spec.ts). NOTE: conversion is currently theater — no toast visible, no lead persisted (see spawned tasks).
2. Hero "See how it works" → demo section → topic interaction.
3. Navbar/footer anchor integrity after section rework (features.tsx deleted; #for-schools now served by what-school-gains).

## Coverage

- New spec: `e2e/web/landing.spec.ts` — 14 tests, all passing against dev server on :5001.
- Component-test infra absent (vitest is node-env, server/tests only; no @testing-library/jsdom) — intentionally not bolted on for marketing UI.
- COVERAGE: 15/20 behavior paths (75%). Remaining gaps are animation/visual-only or infra-blocked.
