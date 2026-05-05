# dela-web

Marketing site for **Dela**, a minimalist iOS puzzle game. Hosted at https://playdela.com.

The site exists for three jobs, in order: satisfy App Store Connect's mandatory Privacy + Support URLs, serve press / editorial inquiries, and drive App Store downloads.

- **Live:** https://playdela.com
- **Repo:** github.com/sorkila/dela-web
- **iOS app source:** `~/Documents/iOS/Dela/`

## Stack

- Plain HTML + CSS. No framework, no JS bundler, no build step.
- One shared stylesheet (`/style.css`) plus inline `<style>` blocks per page for page-specific rules.
- ~40 lines of vanilla JS on the home page (hero animation, drag-to-cut, console egg). No JS on subpages.
- **Self-hosted fonts** in `/fonts/`. No Google Fonts. The only outbound third-party request on the site is the Umami analytics script.

## Deployment

`.github/workflows/deploy.yml` runs `SamKirkland/FTP-Deploy-Action` on every push to `main`, deploying to `/public_html/` over plain FTP on port 21.

GitHub secrets required:
- `FTP_SERVER` — `ftp.playdela.com`
- `FTP_USERNAME` — `admin@playdela.com` (cPanel-style; the inleed account is hosted on l14)
- `FTP_PASSWORD` — Inleed FTP password

Deploys finish in ~15s. Watch with `gh run list -R sorkila/dela-web` and `gh run watch <id>`.

## File map

| Path | Purpose |
|---|---|
| `index.html` | Home — hero with multi-shape animation, prose, manifesto, colophon, footer |
| `privacy/index.html` | Privacy policy (App Store mandatory) |
| `support/index.html` | Support / FAQ (App Store mandatory) |
| `press/index.html` | Press kit + editorial contact |
| `coming-soon/index.html` | Pre-launch placeholder; App Store badge links here. Delete after launch. |
| `404.html` | Branded 404 with CSS-only "didn't quite balance" figure |
| `style.css` | Shared chrome — palette, body, footer, links, type, focus, reduced motion. `@font-face` rules live here. |
| `.htaccess` | Force HTTPS, HSTS, X-CTO, Referrer-Policy, ErrorDocument 404 |
| `sitemap.xml`, `robots.txt` | Allow indexing on `/`, `/privacy/`, `/support/`, `/press/` |
| `og.png` | 1200×630 OG image; Pirata One wordmark + italic tagline + hairline divider |
| `favicon.svg` + raster siblings | Adaptive 2×2 grid mark, light/dark via SVG `<style>` |
| `apple-touch-icon.png` | iOS home screen icon (full app-icon styling) |
| `fonts/inter-latin.woff2` | Variable Inter, 400-600 weight range, latin subset (~48KB) |
| `fonts/pirata-one-latin.woff2` | Pirata One Regular, latin subset (~9KB) |
| `googlee3f1ea143e31a388.html` | Google Search Console verification (verified) |

## Design system

### Palette

| Token | Dark (canonical) | Light |
|---|---|---|
| `--bg` | `#131110` | `#F5F4F0` |
| `--paper` | `#E8E6E1` | `#1A1A1A` |
| `--mid` | `#9A9590` | `#6B6655` |
| `--muted` | `#8B857C` (5.2:1, AA) | `#7C7766` |
| `--surface` | `#322F2C` | `#E0DDD4` |
| `--surface-2` | `#221F1D` | `#ECEAE2` |

`--paper-rgb` (an RGB tuple variable) tracks the palette for transparent rgba uses (spotlight glow, app-badge gradient, ::selection). Inverts in light mode automatically.

Light mode is opt-in via `prefers-color-scheme: light` and is treated as a courtesy variant. Dark is the canonical brand.

### Typography

**One Pirata One moment per site**: the home wordmark "dela". Nowhere else.

Subpage h1s render in **Inter SemiBold 32-44px** (clamp). The wordmark scale on home is `clamp(80px, 17vw, 180px)`.

Body is Inter Regular 17px / 1.65, paper colour. Subpage h2s are uppercase Inter SemiBold 13px in mid colour, letter-spaced 0.08em — a small-caps section divider style.

Don't add a third typeface. Don't reach for Pirata One on subpages.

### Easing

`--ease: cubic-bezier(0.16, 1, 0.3, 1)` (exponential ease-out). Used for entrance reveals, link transitions, and the rejoin/separate phases of the hero animation.

## Hero animation system (home page)

### Architecture

Twelve cells (six top, six bottom) live inside two `<g>` SVG groups. Three keyframed CSS animations run on the groups, plus a fourth on the cut line:

- `top-drift` / `bot-drift` — translate-only motion (no scale ever).
- `top-shadow` / `bot-shadow` — animated `drop-shadow` filter that intensifies during separation.
- `bot-flip` — animates the **fill** of the bottom group from `--paper` to `--mid` during separation, back to paper on rejoin. Inheritable via SVG, so child cells pick up the animated colour without per-cell desync after shape rebuilds.
- `cut-line` — animates `stroke-dashoffset` (line drawing) and opacity.

All four animations share an 11s cycle. They start with `animation-delay: -2.75s` so first paint lands at the cut-drawing moment (no 2.5s static rest before the visitor sees motion).

### Six narrative phases per cycle

| Phase | Time | What happens |
|---|---|---|
| Rest | 0-22% | Cells closed, cut line invisible |
| Cut draws | 22-28% | `stroke-dashoffset` traces the cut from left to right |
| Separate | 28-45% | Halves drift apart with exponential ease-out; bot fill shifts to mid |
| Held apart | 45-64% | Stillness — the moment of "balanced" |
| Rejoin | 64-73% | Halves return; cut line fades; bot fill returns to paper |
| Settle | 73-82% | 1.5px elastic recoil at contact (paper-on-paper compression), then rest |

### Multi-shape rotation

Three shapes rotate on each `top-drift` `animationiteration` boundary:

- **Hourglass** — 12 cells, mirror-symmetric, 4+2/2+4
- **Plus** — 12 cells, inverted hourglass, 2+4/4+2
- **Diagonal staircase** — 10 cells, asymmetric

Shapes are defined as `[col, row]` arrays in JS at the top of the home `<script>`. JS rebuilds the SVG cells on each iteration; the group-level animations continue uninterrupted.

### Per-cell reveal stagger

Each `.cell` has an opacity reveal driven by a per-cell `--reveal-delay` custom property (60ms apart). On first paint, all twelve fade in sequentially. On every shape swap, the new cells fade in sequentially again — the new shape "places itself" rather than appearing as a block.

### Drag-to-cut interaction

Pointer events on the figure pause the auto-loop and let the visitor produce the cut themselves. JS sets `data-mode="manual"`, painting transform / fill / shadow / cut-line based on drag distance (cleared after release). Uses `pointer-capture` and `touch-action: none` so the page doesn't scroll mid-drag.

A small "drag to cut" caption fades in 6 seconds after page load if the visitor hasn't yet dragged. Dismissed forever (per `sessionStorage`) the first time anyone touches the figure.

Both the auto-loop and the drag interaction are disabled under `prefers-reduced-motion`. The figure still renders in a static held-apart pose with the cut line visible at 0.4 opacity.

### Why the implementation looks complex

It's a deliberate sandwich: CSS handles the auto-loop because CSS animations don't drift on tab-throttle; JS handles the manual override because pointer interaction needs frame-by-frame control. The handoff goes through inline-style overrides (`animation: none` while `data-mode="manual"`, transitions for smooth release). On release, `clearInline()` resets `animationDelay` to `0s` so the auto-loop resumes from the closed state cleanly.

## Page structure

### Home

Hero (wordmark, tagline, figure, drag hint, badge, fineprint) → descriptive prose (verb + structure) → manifesto (position) → italic colophon → footer.

The hero is centered. Body sections are centered columns at variable widths (520 prose, 580 manifesto). Vertical rhythm tightens within the hero block (40-64px) and expands toward the colophon (112-160px).

### Privacy / Support / Press

`<main class="wrap wrap--narrow">` with a small "← dela" crumb, Inter SemiBold h1, uppercase Inter h2 section dividers, body copy, footer. Each subpage has a staggered page-entrance fade.

Privacy includes an "About this website" section disclosing Umami. Support uses `<dl>/<dt>/<dd>` for the FAQ (semantically correct). Press has a download button styled like the App Store badge.

### App Store badge

Currently a `<a href="/coming-soon/">` placeholder using a non-Apple icon. **Swap to Apple's official "Download on the App Store" badge and the live App Store URL after launch.** Apple's marketing guidelines say "do not modify the badge artwork."

## Brand and content rules

### Voice

- Lowercase by default. Only proper nouns capitalised.
- Short sentences. Period-terminated. No exclamation marks.
- "We" is fine for the maker (singular, not corporate).
- **No em-dashes.** Use hyphens, colons, or rephrase. This is a strong personal preference of Erik's, applies everywhere — copy, comments, commit messages.

### Pricing position

- Dela is **$2.99 USD** (Apple price tier 3), single premium upfront purchase.
- The website **never shows the price** — Apple's badge handles that live per region.
- Never add a "buy now" CTA. The App Store badge is the only purchase path.
- Never add "limited time", "sale", "money-back guarantee", or "we'll let you know when Dela goes on sale" newsletter copy.

### The five-clause line

The home hero carries this verbatim: `no ads · no IAP · no cookies · no login · one price`. Middle-dot separators, lowercase, mid-grey caption.

The original brief said `no tracking` for clause 3. After Umami was added, that clause was substituted to `no cookies` — factually accurate, since Umami is cookieless. Don't revert without also reconciling the privacy policy.

### Apple Arcade fallback

If Erik's Apple Arcade application is accepted, the line changes to `exclusive to Apple Arcade. no ads, no IAP, no tracking.` and the App Store badge link becomes Arcade-specific. Default is the $2.99 premium messaging until Erik says otherwise.

## Privacy & analytics

The site uses **Umami Cloud** for aggregate, cookieless visit counting:

- Script: `<script defer src="https://cloud.umami.is/script.js" data-website-id="6dcc31dc-88bf-40f4-b641-b362c6f1867d"></script>`
- Dashboard: cloud.umami.is (Erik's account)
- Disclosed in `/privacy` under "About this website"

Don't add additional analytics, pixels, or tracking SDKs. The privacy disclosure must stay aligned with whatever the site actually does.

## SEO / metadata

Every page has `<link rel="canonical">`, full Open Graph (`og:type`, `og:title`, `og:description`, `og:url`, `og:image`, `og:site_name`), Twitter Card meta, and adaptive `theme-color` for light/dark. The home page also ships a JSON-LD `SoftwareApplication` schema (no `offers.price` per the no-hardcoded-pricing rule).

`apple-itunes-app` smart banner meta is **deliberately omitted** until Erik provides the Apple App ID. A placeholder ID would silently fail. Add this when the App Store listing is live.

`/sitemap.xml` lists `/`, `/privacy/`, `/support/`, `/press/`. `/coming-soon/` and `/404.html` carry `<meta name="robots" content="noindex">`.

Google Search Console is verified via `googlee3f1ea143e31a388.html` (file lives at the repo root).

## Server config (`.htaccess`)

Inleed runs nginx in front of Apache. The `.htaccess` applies on the Apache layer:

- Force HTTPS via `mod_rewrite` (verified live)
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (verified live)
- `X-Content-Type-Options: nosniff` (verified live)
- `Referrer-Policy: strict-origin-when-cross-origin` (verified live)
- `ErrorDocument 404 /404.html` (verified live — branded 404 serves on bad paths)

If a directive ever stops working, the same setting can be toggled in the Inleed cPanel-equivalent control panel.

## Conventions

- **Edit `style.css` for shared chrome.** Edit the inline `<style>` block in a page for that page's specifics. Avoid duplicating shared rules.
- **One H1 per page.** Home's H1 is the wordmark; subpages use the page title. Visually-hidden `<h2>`s give the home a logical document outline for screen readers.
- **Animations must respect `prefers-reduced-motion`.** The home page has a substantial reduced-motion block at the end of its `<style>`; mirror that pattern for any new animations.
- **Hover styles must be gated behind `@media (hover: hover)`.** Otherwise touch devices get sticky hover after tap.
- **Tap targets ≥ 40px.** Footer links are padded for this.
- **Safe-area insets on `.wrap`.** Notched iPhones in landscape get clipped without `env(safe-area-inset-*)`.
- **No PWA manifest.** Dela is an iOS app; this site is a marketing surface, not an installable app.
- **No newsletter, no contact form, no live chat.** Email or nothing — `mailto:erik@sorkila.com` with an appropriate `?subject=` per page.
- **Don't introduce a build step.** Static HTML is the brief. If you need to add JS, keep it inline at the end of the page that needs it.

## Pre-launch checklist (App Store Connect)

The App Store submission's URL fields point at:

- Privacy URL: `https://playdela.com/privacy/` ✓
- Support URL: `https://playdela.com/support/` ✓
- Marketing URL: `https://playdela.com/` ✓

All three return 200 and render with JS disabled. HSTS is set, HTTP redirects to HTTPS, custom 404 serves. Apple EULA URL in the footer matches `https://www.apple.com/legal/internet-services/itunes/dev/stdeula/`.

## Post-launch (do these in order once the App Store listing exists)

1. Wrap the App Store badge `href` with the live App Store URL (`https://apps.apple.com/app/idXXXXXXXXX`).
2. Replace the placeholder Apple icon with Apple's official "Download on the App Store" SVG badge.
3. Add `<meta name="apple-itunes-app" content="app-id=XXXXXXXXX">` to the home (and optionally other pages) for the Safari smart banner.
4. Delete `/coming-soon/`.
5. Submit `/sitemap.xml` to Google Search Console.

## Outstanding

- **Domain choice.** Original brief recommended `dela.app`. Currently parked on a different IP. If Erik migrates, swap all canonicals + og URLs back to `https://dela.app/`.
- **Screenshots.** Erik will deliver 4-6 in-game shots at iPhone 6.7" resolution. They'll need a layout treatment (current layout had 2×2 phone bezels; removed when assets weren't ready).
- **Press kit zip.** `/press` links to `/press-kit.zip` which is currently a 404. Build the zip when assets are ready.
- **Brief level-count discrepancy.** The marketing brief says "34 hand-crafted levels"; the iOS curriculum currently has 22. Confirm with Erik which number to publish before launch.
