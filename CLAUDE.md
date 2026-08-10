# dela-web

Marketing site for **dela**, a minimalist iOS puzzle game. Hosted at https://playdela.com.

**Brand name is always lowercase.** Write "dela" everywhere, including at the start of sentences and in titles. The exception is the iOS app source directory (`~/Documents/iOS/Dela/`) and any other path/identifier that already exists in capitalised form on a system Erik doesn't control. Apple's own listing carries whatever name App Store Connect resolves it to; the website's job is to render the brand as `dela` in every surface it owns.

The site exists for three jobs, in order: satisfy App Store Connect's mandatory Privacy + Support URLs, serve press / editorial inquiries, and drive App Store downloads.

- **Live:** https://playdela.com
- **Repo:** github.com/sorkila/dela-web
- **iOS app source:** `~/Documents/iOS/Dela/`

## Stack

- Plain HTML + CSS. No framework, no JS bundler, no build step.
- One shared stylesheet (`/style.css`) plus inline `<style>` blocks per page for page-specific rules. `style.css` also owns the spotlight + grain + view-transition chrome that reaches every page.
- ~210 lines of vanilla JS on the home page only (hero animation, shape rotation, drag-to-cut, cursor-follow spotlight, console egg). Subpages have no JS.
- **Self-hosted fonts** in `/fonts/`. No Google Fonts. The only outbound third-party request on the site is the Umami analytics script.

## Deployment

`.github/workflows/deploy.yml` runs `SamKirkland/FTP-Deploy-Action` on every push to `main`, deploying to `/public_html/` over plain FTP on port 21.

GitHub secrets required:
- `FTP_SERVER`: `ftp.playdela.com`
- `FTP_USERNAME`: `admin@playdela.com` (cPanel-style; the inleed account is hosted on l14)
- `FTP_PASSWORD`: Inleed FTP password

Deploys finish in ~15s. Watch with `gh run list -R sorkila/dela-web` and `gh run watch <id>`.

## File map

| Path | Purpose |
|---|---|
| `index.html` | Home. Single-screen hero (wordmark, tagline, animated figure, drag hint, badge, fineprint) + minimal footer. Vertically centred via flex column on `min-height: 100dvh`. |
| `privacy/index.html` | Privacy policy (App Store mandatory) |
| `support/index.html` | Support / FAQ (App Store mandatory) |
| `press/index.html` | Press kit + editorial contact |
| `404.html` | Branded 404 with CSS-only "didn't quite balance" figure (slowly oscillating). |
| `style.css` | Shared chrome. Palette, body, footer, links, type, focus, reduced motion. Owns the `body::before` spotlight, the `body::after` grain overlay, `@view-transition` cross-page fade, and the `@font-face` rules. |
| `.htaccess` | Force HTTPS, HSTS, X-CTO, Referrer-Policy, ErrorDocument 404, immutable cache on fonts + static images. |
| `sitemap.xml`, `robots.txt` | Allow indexing on `/`, `/privacy/`, `/support/`, `/press/` |
| `og.png` | 1200×630 OG image; Pirata One wordmark + italic tagline + hairline divider. **Deferred upgrade**: rebuild around the figure mid-separation. |
| `favicon.svg` + raster siblings | Adaptive 2×2 grid mark, light/dark via SVG `<style>` |
| `apple-touch-icon.png` | iOS home screen icon (full app-icon styling) |
| `fonts/inter-latin.woff2` | Variable Inter upright, 400-600 weight range, latin subset (~48KB) |
| `fonts/inter-latin-italic.woff2` | Variable Inter italic, 400-600 weight range, latin subset (~52KB). Loads as a separate `@font-face` so the tagline and `<em>` get real italic glyphs, not a synthesised slant. |
| `fonts/pirata-one-latin.woff2` | Pirata One Regular, latin subset (~9KB) |
| `googlee3f1ea143e31a388.html` | Google Search Console verification (verified) |

## Design system

### Palette

| Token | Dark (canonical) | Light |
|---|---|---|
| `--bg` | `#131110` | `#F5F4F0` |
| `--paper` | `#E8E6E1` | `#1A1A1A` |
| `--mid` | `#A8A39E` (AAA) | `#5C574A` (AAA) |
| `--muted` | `#8B857C` (5.2:1, AA) | `#7C7766` |
| `--surface` | `#322F2C` | `#E0DDD4` |
| `--surface-2` | `#221F1D` | `#ECEAE2` |

`--paper-rgb` (an RGB tuple variable) tracks the palette for transparent rgba uses (spotlight glow, app-badge gradient, ::selection, badge bevel). Inverts in light mode automatically.

`--spot-x` / `--spot-y` (default `50%` / `32%`) drive the position of the shared `body::before` radial gradient. On the home page, JS lerps these toward the cursor on pointer-fine devices for a damped ambient-follow feel. Subpages and touch devices keep the static defaults.

Light mode is opt-in via `prefers-color-scheme: light` and is treated as a courtesy variant. Dark is the canonical brand.

### Typography

**Pirata One on the home wordmark**, plus a small Pirata "dela" inside the subpage breadcrumb (the `.crumb .mark` span). Those are the only Pirata moments on the site; the crumb mark exists specifically to carry the wordmark identity into the rest of the site without a heavier intervention.

Subpage h1s render in **Inter SemiBold 32-44px** (clamp). The wordmark scale on home is `clamp(80px, 17vw, 180px)`.

Body is Inter Regular 17px / 1.65, paper colour. Subpage h2s are uppercase Inter SemiBold 13px tracked 0.08em in mid colour, with a 28px hairline rule (`var(--surface)`) sitting on the baseline before the label, set via `flex` + `::before`.

Real italic loads as a separate `@font-face` (Inter Italic, latin subset). Synthetic italics are an immediate craft tell on a minimal site; the `font-style: italic` font-face exists so the tagline, drag hint, and any `<em>` get actual italic glyphs.

Body has `font-kerning: normal`, `font-variant-ligatures: common-ligatures contextual`, `hanging-punctuation: first` (Safari progressive enhancement), and `-moz-osx-font-smoothing: grayscale`. The wordmark gets `text-rendering: geometricPrecision` so Pirata's curves stay crisp on retina.

Don't add a third typeface. Don't reach for Pirata One on subpages beyond the crumb mark.

### Punctuation

**No em-dashes anywhere** (titles, body copy, comments, commit messages, this file; the rule applies everywhere). Replacements: `:` for the home brand:tagline pattern, `·` for subpage `Page · dela` titles. Body copy uses curly quotes (`"…"`, `'…'`) and apostrophes; the codebase has been audited and any straight quote that lands in visible text is a regression.

### Easing

`--ease: cubic-bezier(0.16, 1, 0.3, 1)` (exponential ease-out). Used for entrance reveals, link transitions, and the rejoin/separate phases of the hero animation.

## Shared chrome (every page)

The following lives in `style.css` and applies to every surface (home, subpages, 404) so the brand world doesn't disappear when you click into a subpage:

- **`body::before`**: fixed-position radial spotlight at `var(--spot-x) var(--spot-y)`, two stacked gradients (1100×660 outer, 700×400 inner) at low alpha against `--paper-rgb`. Defaults to `50% 32%`.
- **`body::after`**: fixed-position SVG `feTurbulence` grain overlay, `mix-blend-mode: overlay`, opacity `0.025`, `z-index: 100`. Hidden under `prefers-reduced-transparency: reduce`.
- **`@view-transition: auto`**: every same-origin navigation gets a 240ms cross-fade in supporting browsers (Chromium, Safari). Falls back to a normal navigation in Firefox. Disabled under `prefers-reduced-motion`.

Pages need `position: relative; z-index: 1` on their main content container so it sits above `body::before`. `.wrap` already does this; 404 sets it on its `<main>`.

## Hero animation system (home page)

### Architecture

Twelve cells (six top, six bottom) live inside two `<g>` SVG groups. Three keyframed CSS animations run on the groups, plus a fourth on the cut line:

- `top-drift` / `bot-drift`: translate-only motion (no scale ever).
- `top-shadow` / `bot-shadow`: animated layered `drop-shadow` filter (see "Layered shadow stack" below) that intensifies during separation.
- `bot-flip`: animates the **fill** of the bottom group from `--paper` to `--mid` during separation, back to paper on rejoin. Inheritable via SVG, so child cells pick up the animated colour without per-cell desync after shape rebuilds.
- `cut-line`: animates `stroke-dashoffset` (line drawing) and opacity. Stroke width is `1.0` (was `0.8` before the polish pass).

All four animations share an 11s cycle. They start with `animation-delay: -2.75s` so first paint lands at the cut-drawing moment (no 2.5s static rest before the visitor sees motion).

### Layered shadow stack

The cells use **two stacked `drop-shadow` filters** rather than one: a tight contact shadow (small offset, dark) plus a wide ambient cast (large offset, soft). At rest the contact dominates; during separation the ambient grows to 16px/32px while the contact tightens and darkens. Two layers moving at independent rates is what reads as physical paper hovering above paper rather than a single drawing-program drop shadow. This pattern is mirrored in:

- `top-shadow` / `bot-shadow` keyframes (auto-loop)
- The drag-to-cut `paint()` function in JS (manual mode)
- The `prefers-reduced-motion` static held-apart pose

Every place a dela cell exists, it uses the same shadow formula. Don't replace either layer in isolation.

### Wordmark entrance

The wordmark (`.wordmark`) gets its own keyframe (`wordmark-settle`, 1.4s) that animates `letter-spacing` from `0.012em` down to the resting `0.005em` alongside `opacity` and `translateY`. The letterforms read as "finding their place" rather than just fading in.

The `.wordmark.reveal` selector (specificity `0,2,0`) overrides the generic `.reveal { animation: reveal … }` (`0,1,0`), so the standard `.r1` / `animation-delay` cascade doesn't apply. The reduced-motion block has an explicit `.wordmark.reveal { animation: none; … }` reset because the generic `.reveal { animation: none }` rule would otherwise lose the specificity battle.

### Cursor-follow spotlight

The shared `body::before` reads `var(--spot-x) var(--spot-y)` for its gradient origin. Home-only JS lerps these toward the cursor with a 0.06 damping factor on `requestAnimationFrame`, idling cleanly when settled. Gated behind `(pointer: fine) and (prefers-reduced-motion: no-preference)`, so touch and reduced-motion never run the loop.

### Six narrative phases per cycle

| Phase | Time | What happens |
|---|---|---|
| Rest | 0-22% | Cells closed, cut line invisible |
| Cut draws | 22-28% | `stroke-dashoffset` traces the cut from left to right |
| Separate | 28-45% | Halves drift apart with exponential ease-out; bot fill shifts to mid |
| Held apart | 45-64% | Stillness; the moment of "balanced" |
| Rejoin | 64-73% | Halves return; cut line fades; bot fill returns to paper |
| Settle | 73-82% | 1.5px elastic recoil at contact (paper-on-paper compression), then rest |

### Multi-shape rotation

Three shapes rotate on each `top-drift` `animationiteration` boundary:

- **Hourglass**: 12 cells, mirror-symmetric, 4+2/2+4
- **Plus**: 12 cells, inverted hourglass, 2+4/4+2
- **Diagonal staircase**: 10 cells, asymmetric

Shapes are defined as `[col, row]` arrays in JS at the top of the home `<script>`. JS rebuilds the SVG cells on each iteration; the group-level animations continue uninterrupted.

### Per-cell reveal stagger

Each `.cell` has an opacity reveal driven by a per-cell `--reveal-delay` custom property (60ms apart). On first paint, all twelve fade in sequentially. On every shape swap, the new cells fade in sequentially again, so the new shape "places itself" rather than appearing as a block.

### Drag-to-cut interaction

Pointer events on the figure pause the auto-loop and let the visitor produce the cut themselves. JS sets `data-mode="manual"`, painting transform / fill / shadow / cut-line based on drag distance (cleared after release). Uses `pointer-capture` and `touch-action: none` so the page doesn't scroll mid-drag.

A small "drag to cut" caption fades in 4 seconds after page load if the visitor hasn't yet dragged. Dismissed forever (per `sessionStorage`) the first time anyone touches the figure.

Both the auto-loop and the drag interaction are disabled under `prefers-reduced-motion`. The figure still renders in a static held-apart pose with the cut line visible at 0.4 opacity.

### Why the implementation looks complex

It's a deliberate sandwich: CSS handles the auto-loop because CSS animations don't drift on tab-throttle; JS handles the manual override because pointer interaction needs frame-by-frame control. The handoff goes through inline-style overrides (`animation: none` while `data-mode="manual"`, transitions for smooth release). On release, `clearInline()` resets `animationDelay` to `0s` so the auto-loop resumes from the closed state cleanly.

## Page structure

### Home

Single-screen layout: wordmark → tagline → animated figure → drag hint → App Store badge → fineprint → minimal footer. No descriptive prose, no manifesto, no colophon; those were stripped to land the page at one screen.

`.wrap--home` is `min-height: 100dvh`, flex column. The `<header class="hero">` gets `margin: auto 0` so it vertically centres in the available space; the footer pins to the bottom. Reveal stagger is `r1` wordmark (0.05s) → `r2` tagline (0.20s) → `r3` figure (0.40s) → `r4` badge + fineprint (0.65s) → `r5` footer (1.30s, well after the figure has revealed).

The footer on home is overridden via `.wrap--home > footer` to be smaller (13px), borderless, centered; visually quieter than the subpage footer with its top divider.

### Privacy / Support / Press

`<main class="wrap wrap--narrow">` with a Pirata "dela" crumb, Inter SemiBold h1, hairline-prefixed Inter h2 section dividers, body copy, footer. Each subpage has a staggered page-entrance fade with a decelerating curve through `nth-child(8)` (then plateaus at 0.44s for any further children).

The crumb structure is `<p class="crumb"><a><span class="arr">←</span><span class="mark">dela</span></a></p>`. The `.arr` translates left 3px on hover; the `.mark` is Pirata 20px. This is the cheapest possible cross-page identity carry: a 20px wordmark on every subpage for ~20 lines of CSS.

Privacy includes an "About this website" section disclosing Umami. Support uses `<dl>/<dt>/<dd>` for the FAQ (semantically correct). Press has a download button (`.download`) styled at the same craft level as the home App Store badge: inset top-edge highlight, ambient cast on hover, `translateY(-1px)` lift.

### 404

Two paper bars, the right one slightly low and `--mid` coloured, slowly oscillating on a 5s loop (`.unbalanced .r` runs the `tip` keyframe). Reads as "still searching for balance" rather than a static drawing. Imports `style.css`.

### App Store badge

Links to `https://apps.apple.com/app/dela-the-art-of-dividing/id6766864158` (region-neutral; Apple resolves locale per visitor). Reads "Download on the / App Store" with a custom non-Apple glyph icon. The badge has an inset `0 1px 0` top-edge highlight that brightens on hover, plus an outer cast that appears on hover (`0 4px 14px rgba(0,0,0,0.22)`) and a `translateY(-1px)` lift.

**Outstanding:** swap the custom glyph for Apple's official "Download on the App Store" SVG badge (downloadable from `tools.applemediaservices.com/app-store/`). Apple's marketing guidelines say "do not modify the badge artwork", so the current bespoke version is technically off-spec. Not blocking; visually defensible until the swap.

## Brand and content rules

### Voice

- Lowercase by default. Most proper nouns (Erik Nielsen, Apple, App Store, iOS, Inter, Pirata One) follow normal capitalisation; the brand "dela" is the explicit exception, always lowercase (see the brand-name rule at the top of this file).
- Short sentences. Period-terminated. No exclamation marks.
- "We" is fine for the maker (singular, not corporate).
- **No em-dashes.** Use hyphens, colons, or rephrase. This is a strong personal preference of Erik's; applies everywhere (copy, comments, commit messages, this file).

### Pricing position

- dela is **$2.99 USD** (Apple price tier 3), single premium upfront purchase.
- The website **never shows the price**; Apple's badge handles that live per region.
- Never add a "buy now" CTA. The App Store badge is the only purchase path.
- Never add "limited time", "sale", "money-back guarantee", or "we'll let you know when dela goes on sale" newsletter copy.

### The five-clause line

The home hero carries this verbatim: `no ads · no IAP · no cookies · no login · one price`. Middle-dot separators, lowercase, mid-grey caption.

The original brief said `no tracking` for clause 3. After Umami was added, that clause was substituted to `no cookies`; factually accurate, since Umami is cookieless. Don't revert without also reconciling the privacy policy.

### Apple Arcade fallback

If Erik's Apple Arcade application is accepted, the line changes to `exclusive to Apple Arcade. no ads, no IAP, no tracking.` and the App Store badge link becomes Arcade-specific. Default is the $2.99 premium messaging until Erik says otherwise.

## Privacy & analytics

The site uses **Umami Cloud** for aggregate, cookieless visit counting:

- Script: `<script defer src="https://cloud.umami.is/script.js" data-website-id="6dcc31dc-88bf-40f4-b641-b362c6f1867d"></script>`
- Dashboard: cloud.umami.is (Erik's account)
- Disclosed in `/privacy` under "About this website"

Don't add additional analytics, pixels, or tracking SDKs. The privacy disclosure must stay aligned with whatever the site actually does.

### iOS app behaviour the site asserts

The privacy and support pages make specific claims about how the shipping iOS app behaves. App Store reviewers read these pages, so the claims must match the build. If the iOS app changes, update the page first.

**Privacy page (`/privacy/`) asserts:**

- No user accounts.
- No server connection. Fully offline.
- No third-party analytics or advertising SDKs.
- UserDefaults stores only: level progress and best scores; saved cuts on the level currently being played; in-app preferences.
- No system permissions requested: not photos, contacts, location, microphone, camera, or network.
- Deleting the app removes all stored data.

The original brief mentioned MetricKit; the live page does not, because the shipping app does not transmit diagnostic data and the disclosure was unnecessary. Don't reintroduce MetricKit copy unless the app actually opts into transmitting.

**Support page (`/support/`) asserts the app has:**

- Drag-to-cut input that snaps to the nearest horizontal or vertical grid line.
- Tap a cut to remove it.
- A "back" button at the bottom of the screen for undo.
- No cross-device sync (local only).

**Curriculum (confirmed 2026-08-10, app v1.04):** 137 levels total. 53 hand-authored (bands A-E) + 72 procedurally-generated and brute-force-validated (band F) + 8 hand-authored band G levels (added in v1.01) + 4 hand-authored anchor levels (tree, fish, mountain, boat). Daily mode and endless mode existed in earlier briefs but were removed from the iOS build before launch; never reintroduce that copy without confirmation.

**Canonical contact email:** `hello@sorkila.com`. Used on privacy, support, press, and as the site-wide convention for any new mailto.

## SEO / metadata

Every page has `<link rel="canonical">`, full Open Graph (`og:type`, `og:title`, `og:description`, `og:url`, `og:image`, `og:site_name`), Twitter Card meta, and adaptive `theme-color` for light/dark. The home page also ships a JSON-LD `["SoftwareApplication","VideoGame"]` schema with an `offers` node ($2.99 USD, added 2026-08-10 for search and AI-assistant visibility). This is a deliberate, Erik-approved exception to the no-hardcoded-pricing rule: structured data is machine-readable metadata, not visible UI, and the page itself still never shows the price. If the App Store tier changes (or the Apple Arcade fallback fires), update the `offers` node in `index.html` by hand.

Title separators follow the no-em-dash rule: home uses `:` for the brand:tagline pattern (`dela: the art of dividing`); subpages use `·` (`Privacy · dela`, `Support · dela`, `Press · dela`, `Not found · dela`).

`apple-itunes-app` smart banner meta carries the live App ID (`6766864158`) on the home page, so Safari users get the in-app banner offering to open the App Store listing.

`/sitemap.xml` lists `/`, `/privacy/`, `/support/`, `/press/`. `/404.html` carries `<meta name="robots" content="noindex">`.

Google Search Console is verified via `googlee3f1ea143e31a388.html` (file lives at the repo root).

### Font preload

Every page includes preload tags for the fonts it actually uses on first paint. Without these, `font-display: swap` causes a brief flash of fallback (Times/serif) on the Pirata wordmark, which is the brand's most distinctive moment.

```html
<link rel="preload" as="font" type="font/woff2" href="/fonts/inter-latin.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="/fonts/pirata-one-latin.woff2" crossorigin>
```

Home also preloads `inter-latin-italic.woff2` (its tagline is italic on first paint). Subpages skip italic preload because italic isn't load-bearing in their initial frame.

## Server config (`.htaccess`)

Inleed runs nginx in front of Apache. The `.htaccess` applies on the Apache layer:

- Force HTTPS via `mod_rewrite` (verified live)
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (verified live)
- `X-Content-Type-Options: nosniff` (verified live)
- `Referrer-Policy: strict-origin-when-cross-origin` (verified live)
- `ErrorDocument 404 /404.html` (verified live; branded 404 serves on bad paths)
- `Cache-Control: public, max-age=31536000, immutable` on fonts (`woff2/woff/ttf/otf/eot`) and static images (`png/jpg/jpeg/gif/svg/ico/webp/avif`). HTML and CSS are deliberately omitted so copy / style edits propagate immediately on deploy.

If a directive ever stops working, the same setting can be toggled in the Inleed cPanel-equivalent control panel.

## Conventions

- **Edit `style.css` for shared chrome.** Edit the inline `<style>` block in a page for that page's specifics. Avoid duplicating shared rules. The spotlight, grain, view transitions, palette tokens, font-faces, body type, footer base, link styles, focus, crumb, h1/h2 styles, and reveal stagger all live in `style.css` and are loaded by every page (including 404).
- **One H1 per page.** Home's H1 is the wordmark; subpages use the page title. Visually-hidden `<h2>`s give the home a logical document outline for screen readers.
- **Animations must respect `prefers-reduced-motion`.** The home page has a substantial reduced-motion block at the end of its `<style>`; mirror that pattern for any new animations. The `.wordmark.reveal` selector has higher specificity than the generic `.reveal` reduced-motion override, so any element-specific reveal animation needs an explicit reduced-motion reset (see the existing `.wordmark.reveal { animation: none; }` rule).
- **Transparency under `prefers-reduced-transparency`.** The grain overlay (`body::after`) hides under this query. Any future overlay-style chrome should follow.
- **Hover styles must be gated behind `@media (hover: hover)`.** Otherwise touch devices get sticky hover after tap.
- **Tap targets ≥ 40px.** Footer links are padded for this.
- **Safe-area insets on `.wrap`.** Notched iPhones in landscape get clipped without `env(safe-area-inset-*)`.
- **`position: relative; z-index: 1` on main content containers** so they sit above the fixed-position `body::before` spotlight. `.wrap` already has this; standalone pages (404) set it on their `<main>`.
- **No PWA manifest.** dela is an iOS app; this site is a marketing surface, not an installable app.
- **No newsletter, no contact form, no live chat.** Email or nothing: `mailto:hello@sorkila.com` with an appropriate `?subject=` per page.
- **Don't introduce a build step.** Static HTML is the brief. If you need to add JS, keep it inline at the end of the page that needs it.

## Launch state

App went live on the App Store on **2026-05-07**.

- **App ID:** `6766864158`
- **App Store URL:** `https://apps.apple.com/app/dela-the-art-of-dividing/id6766864158` (region-neutral; Apple resolves locale per visitor)
- **Marketing URL:** `https://playdela.com/`
- **Privacy URL:** `https://playdela.com/privacy/` (App Store Connect required)
- **Support URL:** `https://playdela.com/support/` (App Store Connect required)
- **Apple EULA URL** in the footer matches `https://www.apple.com/legal/internet-services/itunes/dev/stdeula/`

All three required URLs return 200 and render with JS disabled. HSTS set, HTTP redirects to HTTPS, custom 404 serves.

### Done at launch

- Brand styling flipped to lowercase across the site (titles, meta, og/twitter, JSON-LD, body, aria, mailto subjects).
- App Store badge `href` updated to the live URL.
- Badge text flipped from "Coming soon / App Store" to "Download on the / App Store".
- `<meta name="apple-itunes-app" content="app-id=6766864158">` added to the home for the Safari smart banner.
- `/coming-soon/` deleted.

### Still to do

- **Official Apple badge artwork.** Replace the custom Apple-glyph icon in the home `.app-badge` with Apple's official "Download on the App Store" SVG badge (download from `tools.applemediaservices.com/app-store/`). Apple's marketing guidelines say "do not modify the badge artwork."
- **Sitemap submission.** Submit `/sitemap.xml` to Google Search Console.

## Outstanding

### Pre-launch blockers / open content questions

- **Domain choice.** Original brief recommended `dela.app`. Currently parked on a different IP. If Erik migrates, swap all canonicals + og URLs back to `https://dela.app/`.
- **Screenshots.** Press copy publishes "six in-game screenshots at iPhone 6.7\" resolution"; Erik will deliver these. They're currently absent from the home page (hero is figure-only) and absent from `/press-kit.zip`.
- **Press kit zip.** `/press` links to `/press-kit.zip` which is currently a 404. Build the zip when assets are ready.
- **Level count.** Shipping curriculum is **137 levels** as of app v1.01+: 53 hand-authored (bands A-E), 72 procedurally-generated and brute-force-validated (band F), 8 hand-authored band G, 4 hand-authored anchor levels (tree, fish, mountain, boat). Press copy says "137 hand-tuned levels" (updated 2026-08-10 on /press/ and in llms.txt; keep both in sync with the app repo's CLAUDE.md when the curriculum changes).

### Deferred design work (audit conclusions, not yet shipped)

These were identified in the principal-team audit. None are shipping until Erik says go:

- **OG image rebuild** around the figure mid-separation. Current OG is wordmark + tagline + hairline divider; reads as a font sample, not a dela image.
- **Favicon swap to the Pirata 'd'.** Current favicon is the 2×2 grid mark; the wordmark's 'd' is more ownable at 16×16.
- **Apple touch icon as the figure mid-separation.** Current is the 2×2 grid; figure-as-icon would stand out on iOS home screens.
- **Wordmark optical margin compensation** for Pirata's heavy 'd' descender (sits slightly low optically). Needs visual eyeballing before shipping.
- **Drag-to-cut release anticipation overshoot.** A tiny over-separation (1–2px) before the rejoin, mirroring `bot-drift`'s settle physics.
- **Privacy section consolidation** (7 sections to 3). Content rewrite, not styling.
- **Custom logotype** drawn for dela rather than Pirata One. The single most consequential investment in the site's identity. ~3 weeks lead time, ~$3-8k.
- **Cut-themed page transitions.** Replace the 240ms cross-fade with a horizontal cut: top half slides up, bottom half slides down, new page slides in from the cut. ~30 lines of CSS using `::view-transition-old(root)` / `::view-transition-new(root)` keyframes.
- **Wordmark cuts itself, synchronized with the figure.** Clip-path on the wordmark animated alongside the figure's keyframe schedule, so wordmark and figure tell the same metaphor at the same moment.
- **Generative shape rotation.** Currently 3 hand-designed polyominoes loop every 33s; visitors notice. Replace with a JS generator producing valid balanced shapes on the fly.
- **Sound design.** Subtle paper-tear whisper on cut moments + ambient room tone. Defaulted off, opt-in via small `♪` toggle.
- **Photographic paper-grain.** Replace the SVG `feTurbulence` overlay with a real photograph of paper under raking light, tiled at 240×240 WebP.
- **Playable balance-check on the figure.** Port the iOS game's balance-checking math to JS so visitors can draw arbitrary cuts and see whether they balance. Highest impact for App Store conversion; biggest engineering lift.
