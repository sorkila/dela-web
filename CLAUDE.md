# Dela website

Marketing site for **Dela**, a puzzle game for iPhone and iPad. Hosted at https://playdela.com.

**Sentence case everywhere, including the name.** Write "Dela" (capital D) in all text, titles, meta, schema, llms.txt and mailto subjects, and the Pirata One wordmark renders "Dela". Headings and UI labels are sentence case ("How it plays", "The original Dela", "Return home"). This replaced the all-lowercase style of 1.x on 2026-09-27; don't reintroduce lowercase-only brand strings.

The site exists for three jobs, in order: satisfy App Store Connect's mandatory Privacy + Support URLs, serve press / editorial inquiries, and drive App Store downloads.

- **Live:** https://playdela.com
- **Repo:** github.com/sorkila/dela-web
- **iOS app source:** `~/Repositories/Dela` (2.0 work on branch `v2-twins`)

## Branches and 2.0

- `main` is the live 1.x site. **Every push to `main` deploys** (see Deployment).
- `v2` holds the Dela 2.0 site (twins redesign, free to try, sentence case, ink and gold). It merges to `main` on launch day, **Tue 17 Nov 2026**, when the 2.0 update goes live on the App Store. Never push it early: the live 1.x listing would contradict it (price, IAP, screenshots).
- Dates written for launch: privacy "Effective 17 November 2026", sitemap `lastmod` 2026-11-17, press fact sheet and llms.txt say 2.0 released 17 November 2026. If launch moves, update all four.
- Launch moved to the end of September (commit 2c15158) and `main` carries the 2.0 site. Sitemap `lastmod` is the date each page last changed, never a future date (fixed 2026-11-08: four URLs said 2026-11-17, which Google can discard).

## Stack

- Plain HTML + CSS. No framework, no JS bundler, no build step.
- One shared stylesheet (`/style.css`) plus inline `<style>` blocks per page for page-specific rules. `style.css` also owns the spotlight + grain + view-transition chrome that reaches every page.
- Vanilla JS on the home page (hero figure, cursor-follow spotlight, console egg) and on `/play/` (the browser sampler). Other subpages have no JS.
- **Self-hosted fonts** in `/fonts/`. No Google Fonts. The only outbound third-party request on the site is the Umami analytics script.
- `tools/` holds Python scripts that render images (see Tools). They are not part of the site and are excluded from deploy.

## Deployment

`.github/workflows/deploy.yml` runs `SamKirkland/FTP-Deploy-Action` on every push to `main`, deploying to `/public_html/` over plain FTP on port 21. Excluded: `**/*.md` (this file), `**/*.py`, `tools/**` and `**/.DS_Store`; the `exclude` list repeats the action's defaults (`**/.git*`, `**/.git*/**`, `**/node_modules/**`) because setting it replaces them. Any new dev-only file type needs a line there. 1.x deployed `CLAUDE.md` to the live root (it returned 200 on 2026-09-27); after the launch deploy, check `https://playdela.com/CLAUDE.md` is gone and delete it over FTP if the action left it.

GitHub secrets required:
- `FTP_SERVER`: `ftp.playdela.com`
- `FTP_USERNAME`: `admin@playdela.com` (cPanel-style; the inleed account is hosted on l14)
- `FTP_PASSWORD`: Inleed FTP password

Deploys finish in ~15s. Watch with `gh run list -R sorkila/dela-web` and `gh run watch <id>`.

## File map

| Path | Purpose |
|---|---|
| `index.html` | Home. One-screen hero (wordmark, tagline, lede, animated figure, App Store badge, fineprint, scroll cue), then How it plays (five steps with board crops), Chapters (plaques), Price, Questions (FAQ with FAQPage schema), closing manifesto + second badge, footer. |
| `play/index.html` | The browser sampler: ten boards (four from chapter I, six from chapter II) on a canvas, then an end card with the App Store badge. See Play. |
| `privacy/index.html` | Privacy policy (App Store mandatory) |
| `support/index.html` | Support / FAQ (App Store mandatory), in three groups: Playing, Purchases, Your data. FAQPage schema. |
| `press/index.html` | Press TL;DR, fact sheet, press kit download, contact |
| `404.html` | Branded 404: an ivory bar and a gold bar that aren't twins, the gold one slowly rocking. |
| `style.css` | Shared chrome. Palette, body, footer, links, type, focus, reduced motion. Owns the `body::before` spotlight, the `body::after` grain overlay, the `@view-transition` cut-open navigation, and the `@font-face` rules. |
| `shots/*.webp` | Board crops for How it plays: `stroke`, `halves`, `landing`, `miss`, `hint` (660×825, WebP q80, ~20-35 KB each). Cropped from the 2.0 store captures in `Dela/store_assets/v2/raw_iphone/` by `tools/screens.py`. |
| `badges/app-store-black.svg` | Apple's official App Store badge (see App Store badge). |
| `og.png` | 1200×630 OG image: gold Pirata "Dela" and "One line, two identical halves." beside an ivory and a gold-leaf twin, parted along a staircase cut, on the warm table. Rendered by `tools/brand.py`. |
| `favicon.svg` + `favicon-16x16.png`, `favicon-32x32.png`, `favicon.ico` (16/32/48) | Pirata One capital 'D' in gold on a rounded `#131110` tile (outlined glyph path, no font dependency). The tile keeps it legible on light and dark tab bars. Rendered by `tools/brand.py`. |
| `apple-touch-icon.png` | The 2.0 app icon (ivory and gold twins), 180×180, resized from `Dela/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon.png` by `tools/brand.py --touch-icon`. |
| `press-kit.zip` | 2.0 press kit (~23 MB), built by `tools/presskit.py`: `dela-press-kit/` with `icon/dela-icon-1024.png`, `screenshots/iphone/` (6.9", 1320×2868), `screenshots/ipad/` (13", 2064×2752), `screenshots/framed-iphone/` (captioned store shots), each six in store order, and `fact-sheet.txt`. Screenshots are pngquant-quantised to stay under 25 MB. If the size changes, update the press page's Assets line. |
| `llms.txt` | Plain-text fact sheet for AI assistants. Keep in sync with the press fact sheet. |
| `tools/brand.py` | Renders the favicons, `og.png` and (with `--touch-icon`) the touch icon from `/fonts/` (fontTools + Pillow). |
| `tools/screens.py` | `name=path` pairs → `shots/<name>.webp` board crops. |
| `tools/presskit.py` | Builds `press-kit.zip` from `Dela/store_assets/v2/` and the app icon. Needs `pngquant` (brew). The fact sheet text lives in the script; keep it in sync with the press page and llms.txt. |
| `.htaccess` | Force HTTPS, HSTS, X-CTO, Referrer-Policy, ErrorDocument 404, immutable cache on fonts + static images. |
| `sitemap.xml`, `robots.txt` | Allow indexing on `/`, `/privacy/`, `/support/`, `/press/` |
| `fonts/inter-latin.woff2` | Variable Inter upright, 400-600 weight range, latin subset (~48KB) |
| `fonts/inter-latin-italic.woff2` | Variable Inter italic, 400-600, latin subset (~52KB). Separate `@font-face` so the tagline and `<em>` get real italics. |
| `fonts/pirata-one-latin.woff2` | Pirata One Regular, latin subset (~9KB) |
| `googlee3f1ea143e31a388.html` | Google Search Console verification (verified) |

## Tools

```bash
python3 tools/brand.py --touch-icon ~/Repositories/Dela/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon.png
R=~/Repositories/Dela/store_assets/v2/raw_iphone
python3 tools/screens.py stroke=$R/stroke.png halves=$R/halves.png landing=$R/landing.png miss=$R/miss.png hint=$R/hint.png
python3 tools/presskit.py   # press-kit.zip
```

`screens.py` crops a 4:5 band centred at 49.5% of the screen height (the board), which leaves out the status bar, header and footer copy. Rerun `brand.py` after palette or wordmark changes.

**Image cache gotcha:** `.htaccess` serves images with `immutable` for a year. Replacing a file that has already been deployed under the same name leaves returning visitors on the old one. Before launch that doesn't matter (nothing on `v2` is live); after launch, rename (for example `shots/landing-2.webp`) and update the `src`.

## Design system

### Palette (ink and gold, dark only)

The app is dark only, and so is the site since 2.0. `:root` sets `color-scheme: dark`; pages carry one `theme-color` (`#131110`) and `color-scheme: dark`. There is no light variant any more.

| Token | Value | Source |
|---|---|---|
| `--bg` | `#131110` | `Theme.background`, the table |
| `--paper` | `#E8E6E1` | bone text (`Theme.groupA`) |
| `--mid` | `#A8A39E` | secondary text (AAA on bg) |
| `--muted` | `#8B857C` | tertiary text (AA) |
| `--surface` / `--surface-2` | `#322F2C` / `#221F1D` | hairlines, borders |
| `--gold` | `#E8CF8B` | `Theme.gold`: wordmark, crumb mark, numerals, accents |
| `--gold-deep` | `#C9A95C` | `Theme.goldDeep`: link underline on hover |
| `--ivory` | `#EDE6D6` | the resting half (`ivoryTop`) |
| `--light-rgb` | `255, 222, 170` | the warm lamp in the spotlight |

`--paper-rgb` and `--gold-rgb` are RGB tuples for rgba uses. Material gradients in the hero SVG and 404 come from `LacquerBoard.swift`: lacquer `#2E2823 → #141110`, ivory `#EDE6D6 → #BDB09C`, gold leaf `#FAE094 / #DBA847 / #8C5E1C / #CC993D / #F2D17A` at 0 / 0.3 / 0.58 / 0.8 / 1.

`--spot-x` / `--spot-y` (default `50%` / `32%`) drive the shared `body::before` warm radial light. On the home page, JS lerps these toward the cursor on pointer-fine devices.

### Typography

**Pirata One** for the gold home wordmark, the gold "Dela" crumb mark on subpages, the 404 numeral, and on the home page only: step titles in How it plays, chapter numerals and names on the plaques, and the closing manifesto. These echo the app's plaques. Subpages use Pirata only for the crumb mark. Capital Roman numerals only (lowercase Pirata numerals read badly: "iv" looks like "ib").

Subpage h1s render in **Inter SemiBold 32-44px** (clamp). The wordmark scale on home is `clamp(80px, 17vw, 180px)`. Body is Inter Regular 17px / 1.65. Section labels (subpage h2s and home section h2s) are uppercase Inter SemiBold 13px tracked 0.08em in mid colour with a 28px hairline before them (gold at 45% on home). Home section intros are Inter Medium 22-28px in paper.

Real italic loads as a separate `@font-face` (Inter Italic). Don't add a third typeface.

### Punctuation

**No em-dashes anywhere** (titles, body copy, comments, commit messages, this file). Home title uses `:` (`Dela: The art of dividing`); subpages use `·` (`Privacy · Dela`). Body copy uses curly quotes and apostrophes.

### Easing

`--ease: cubic-bezier(0.16, 1, 0.3, 1)` (exponential ease-out) for entrance reveals and link transitions.

## Shared chrome (every page)

- **`body::before`**: fixed warm radial spotlight at `var(--spot-x) var(--spot-y)`, two stacked gradients at low alpha against `--light-rgb`.
- **`body::after`**: fixed SVG `feTurbulence` grain overlay, `mix-blend-mode: overlay`, opacity `0.025`, `z-index: 100`. Hidden under `prefers-reduced-transparency: reduce`.
- **`@view-transition: auto`**: same-origin navigations open the new page along a horizontal clip-path cut at the viewport centre (360ms) while the old page dims beneath. Disabled under `prefers-reduced-motion`.
- Link underlines turn `--gold-deep` on hover; focus rings are `--gold`; `::selection` is gold at 28%.

Pages need `position: relative; z-index: 1` on their main content container so it sits above `body::before`. `.wrap` already does this; 404 sets it on its `<main>`.

## Hero figure (home page)

The 2.0 loop in miniature, one SVG (`viewBox 0 0 200 200`, cell = 30 units) built by the script at the end of `index.html`:

Timing follows the app's landing (`TableScene.landing`): about 5 s a board.

1. A lacquer shape sets down from a slight lift (traced outline with rounded corners, sheen, lit rim, faint hairlines between cells, layered contact + ambient drop shadows).
2. A molten gold line draws along the grid, edge to edge, bends included: three stacked strokes (blurred glow, gold core, hot white core) via `stroke-dashoffset`, with a glowing tip riding the leading end. The tip sheds sparks, a burst at each bend; `timeAt` inverts the draw easing so each spark leaves exactly when the tip passes.
3. The split: the whole crossfades to two halves that tint ivory (rests) and gold leaf (travels) and part a hair (0.06 cell / a third of that, as in the app). The line cools from the inside out: white core, gold core, glow.
4. The gold half lifts off a recess (`.fig-tray`), carries on a short arc (`bArc`) while it turns or flips, and slams onto its twin (one keyframed timeline on `bMove`).
5. The thud: a small table shake (`rig`), a squash, a gold flash and halo, a shockwave ring (`.fig-ring`, reach sized to the board as `ringReach`), dust off the landed outline; the tray lets go.
6. The pair settles to the centre of the figure and a light band (`#g-band`, clipped to the landed outline) crosses it. Hold, sink and fade, next board.

On pointer-fine devices the spotlight loop also lights the figure: `#g-sheen` follows the cursor and `#g-gold` turns a few degrees, like the app's tilt light.

Boards are real chapter II boards from `Dela/Sources/LevelsTwins.swift` (2003, 2011, 2004, 2013) in the app's row codec with the answer line as grid vertices. The script flood-fills the split, finds the flip/turn that maps the gold half onto the ivory one (so any twin board can be added), and warns in the console if a board has no twin fit. The half nearer the top left rests.

Every step is a Web Animation (`element.animate`, `fill: 'forwards'`), so a cycle is `Promise.all` of their `finished` and nothing drifts on tab throttling. Gotchas: animations on the same property of the same element must not use `fill: 'both'` (a later one's backward fill overrides an earlier one); transforms use `transform-box: view-box; transform-origin: 0 0` and coordinates are baked into absolute viewBox units; parent groups (`rig`, `settle`, `squash`) only translate or scale about baked points, so the children's maths still holds; the light band's clip path is in the referencing group's space, so it moves with `settle`; a `clip-path` isolates its group, so `mix-blend-mode` inside it blends with nothing (the band uses plain opacity); the drop-shadow filter sits on an outer group and the transform on an inner one so the shadow doesn't turn with the piece.

`prefers-reduced-motion`: no loop; the first board is shown split, tinted, halves parted by 5 units. The 1.x drag-to-cut interaction and "drag to cut" hint were removed with the 2.0 figure.

## Play (`/play/`)

Ten real boards from the app, playable with mouse or touch, for posts and press that shouldn't need an install. One self-contained page: inline style and script, no library.

- **Logic** is a line-for-line port of `Dela/Sources/Twins.swift`: `split` (flood fill across cut edges), `outline`, `centroid`, `fit` (the eight symmetries in doubled coordinates, same scoring). Boards are copied from `LevelsHalves.swift` / `LevelsTwins.swift` in the row codec. Check a changed board with the node snippet in the commit that added the page, or by solving it.
- **Stroke** follows `TableScene.follow`: the head steps one grid edge at a time; a step back needs 0.22 of a cell, a bend 0.3, straight on 0.36, release snaps at 0.5.
- **Choreography** follows `TableScene` (part, carry, slam, settle; miss with misfit and bare cells; halves parted; unequal halves as a balance), on a small clip/cue timeline. Reduced motion swaps carries for fades.
- **Teaching:** board 1 draws a ghost of its line until the first touch; the first twins board (2003) draws its decoy and plays the miss before handing over, like the app's rehearsal. A hint button appears after three misses: the line's ends, then the whole line.
- **Sound** is synthesized with Web Audio (tick, lift, thud, chord, knock), off with the header toggle; `navigator.vibrate` where it exists.
- **Storage:** `dela.web.board`, `dela.web.sound`, `dela.web.done` in localStorage (disclosed on `/privacy/`).
- **Umami events:** `app-store-click` (see Privacy & analytics), `play-start`, `board-solved` (board id, position, misses), `hint`, `play-complete`, `share`, `store-click` (`where`: foot or end). This is the funnel to watch after a post.
- Home links it under the hero badge ("Or play ten boards in your browser") and under the closing badge.

## Page structure

### Home

- **Hero** fills the first screen (`min-height: calc(100svh - 2 * top padding)`, flex column centred): wordmark → tagline "The art of dividing." → lede "One line, two identical halves. / A puzzle game for iPhone and iPad." → figure → App Store badge → fineprint → chevron to `#how`. Reveal stagger `r1`-`r5`.
- **How it plays**: intro "The mechanic is simple. The decisions are not.", five steps (One line, Two halves, Twins, The reason why, Hints that wait), each a board crop beside the words, alternating sides from 640px; on phones the crop is 40% wide.
- **Chapters**: plaques for I Halves and II Twins (gold rim, "Free"), III-VII (dim, "December"), and The original Dela ("Unlock").
- **Price**: the fairness statement (see Pricing).
- **Questions**: six Q&As, mirrored in the FAQPage JSON-LD in `<head>`. Keep both in sync.
- **Closing**: the manifesto line in Pirata and a second App Store badge.

### Privacy / Support / Press

`<main class="wrap wrap--narrow">` with the crumb (`<p class="crumb"><a><span class="arr">←</span><span class="mark">Dela</span></a></p>`, gold Pirata mark), Inter SemiBold h1, hairline-prefixed h2 dividers, body copy, footer. Staggered page-entrance fade.

Support uses `<dl>/<dt>/<dd>` in three groups and ships a FAQPage schema that mirrors the visible answers. Press has a TL;DR, a fact-sheet `<dl class="facts">` (two columns, stacks under 480px), the press kit button, contact, embargo, about.

### App Store badge

Apple's official black "Download on the App Store" badge, `badges/app-store-black.svg`, downloaded unmodified from Apple Marketing Tools (`https://toolbox.marketingtools.apple.com/api/v2/badges/download-on-the-app-store/black/en-us`; the old `tools.applemarketingtools.com` host no longer resolves). Shown at 50px high as an `<img>` inside the link to `https://apps.apple.com/app/dela-the-art-of-dividing/id6766864158`, in the hero and the closing section. Never recolour, restyle or redraw it: only its size, a 1px lift + drop shadow on hover and the gold focus ring are ours. Apple's rules: at least 40px high on screen, clear space of a quarter of its height (`.badge-row` pads 12px).

## Brand and content rules

### Voice

Spare, confident, a little poetic. Short sentences, period-terminated. No exclamation marks. "We" is fine for the maker. No em-dashes. Keep the site consistent with the store copy draft in `Dela/store_assets/v2/store_copy.md` (for example "turned or mirrored", "Hints wait until you've had a real go").

### Pricing position (2.0)

- Free to download. Chapters I and II free. One non-consumable in-app purchase (planned $4.99) unlocks the original Dela and the later chapters; an optional supporter tier ($7.99) unlocks the same. People who bought 1.x keep everything (grandfathered).
- The website **never shows a price**; the App Store shows it per region. Say "one purchase", "the unlock", "the supporter option".
- Never add "buy now" CTAs, "limited time", "sale", or newsletter copy. The App Store badge is the only path.
- Hero fineprint: `Free to try · No ads · No subscription · No login` (each clause `nowrap`). The 1.x line (`no ads · no IAP · no cookies · no login · one price`) is retired: IAP exists now. "No tracking" is used only about the app ("The app collects no data"), because the site runs Umami.

### Daily

The daily mode was removed from the app in September 2026. The site has no daily page, no `/d/<n>` route and no daily, streak or "Dela #n" copy. Don't add any without Erik's say-so.

## Privacy & analytics

The site uses **Umami Cloud** for aggregate, cookieless visit counting (`<script defer src="https://cloud.umami.is/script.js" data-website-id="6dcc31dc-88bf-40f4-b641-b362c6f1867d">`), disclosed in `/privacy` under "About this website". Don't add other analytics, pixels, or tracking.

`/track.js` (2026-11-08) sends `app-store-click` (`page`, `placement` from the link's `data-where`) for every `apps.apple.com` link, on every page that has one (home, play, press): add the script tag to any new page with a store link. It is getvelm.com's pattern, a capture-phase listener calling `umami.track`, never `data-umami-event`, whose handler navigates from script and breaks the iOS hand-off to the App Store app. The portfolio dash (`projects.json`) reads this event name.

### iOS app behaviour the site asserts (2.0)

App Store reviewers read these pages, so the claims must match the build. If the app changes, update the page first.

**Privacy (`/privacy/`):** no accounts; no server of its own; no third-party analytics or advertising SDKs; UserDefaults holds only progress (chapters and the original Dela), the original Dela's best scores and saved cuts, whether Dela is unlocked, and preferences; purchases go through Apple, and the app asks StoreKit whether the Apple Account owns the unlock or bought Dela before (the answer stays on device); no system permissions; device tilt (Core Motion, `TiltLight`) moves the light on the tiles, on device, not recorded; deleting the app removes all data.

**Support (`/support/`):** one continuous line along the grid from edge to edge, bends allowed, lift to cut; chapter I equal area, chapter II same shape turned or mirrored; a wrong line shows why and slides back; hints appear as a mark at the bottom after you've been stuck, each nudge shows more, set to Off / Patient / Eager in home (grid icon) under Feel; The original Dela is in home under Classic (drag to cut, tap a cut to remove, Back to undo); restore from the unlock screen ("Restore purchase"); no sync; refunds via reportaproblem.apple.com.

**Content (confirmed 2026-09-27, app 2.0 build 13):** chapter I Halves 12 boards, chapter II Twins 13 boards, chapters III-VII (Seeds, Apart, Two of everything, Thirds, The exception) "in December", The original Dela 137 boards. iOS 17 or later, iPhone and iPad.

**Canonical contact email:** `hello@sorkila.com`, with `?subject=Dela%20support` / `Dela%20privacy` / `Dela%20press`.

## SEO / metadata

Every page has `<link rel="canonical">`, Open Graph (`og:site_name` "Dela"), Twitter Card meta, one `theme-color` and `color-scheme: dark`. Home ships two JSON-LD blocks: `["SoftwareApplication","VideoGame"]` with `offers` at price `0` USD plus a description of the in-app unlock, and a FAQPage mirroring the visible Questions. Support ships its own FAQPage. Structured data is the only place a price appears (zero), per the pricing rule.

`apple-itunes-app` smart banner meta (`6766864158`) is on the home page. `/404.html` carries `noindex`. Google Search Console is verified via `googlee3f1ea143e31a388.html`.

### Font preload

Every page preloads the fonts it uses on first paint (Inter upright + Pirata; home also Inter italic) to avoid a fallback flash on the wordmark.

## Server config (`.htaccess`)

www.playdela.com 301s to the apex (added 2026-11-08), force HTTPS, HSTS (1 year), `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `ErrorDocument 404 /404.html`, and `Cache-Control: public, max-age=31536000, immutable` on fonts and static images. HTML and CSS are deliberately not cached so copy and style edits propagate on deploy.

## Conventions

- **Edit `style.css` for shared chrome**, the inline `<style>` for page specifics.
- **One H1 per page.** Home's H1 is the wordmark.
- **Animations respect `prefers-reduced-motion`.** `.wordmark.reveal` needs its own reduced-motion reset (specificity).
- **Overlays hide under `prefers-reduced-transparency`.**
- **Hover styles behind `@media (hover: hover)`.**
- **Tap targets ≥ 40px.**
- **Safe-area insets on `.wrap`.**
- **Mobile-first; check at 375px.** No horizontal page scroll.
- **No PWA manifest, no newsletter, no contact form.** Email or nothing.
- **Don't introduce a build step.** Scripts in `tools/` render assets that are committed; the site itself stays static.

## Launch state

1.x went live on **2026-05-07** (App ID `6766864158`). Dela 2.0 ships **2026-11-17** as an update to the same listing; the `v2` branch is the site for it.

- **App Store URL:** `https://apps.apple.com/app/dela-the-art-of-dividing/id6766864158`
- **Store title / subtitle (2.0):** "Dela: The art of dividing" / "One line, two identical halves"
- **Privacy URL:** `https://playdela.com/privacy/`, **Support URL:** `https://playdela.com/support/`
- **Apple EULA** in the footer: `https://www.apple.com/legal/internet-services/itunes/dev/stdeula/`

## Outstanding

- **Press kit extras** (optional): a Pirata "Dela" wordmark PNG + SVG (the site renders it as text, so there is no file to ship yet) and the App Preview. Rerun `tools/presskit.py` if the store screenshots are recaptured.
- **App Preview on the site** (optional): `Dela/store_assets/v2/preview_iphone.mp4` could run muted, looping and lazy-loaded if re-encoded to ~2-3 MB at 540 wide without audio. Not added yet.
- **Sitemap submission** to Google Search Console.
- **Stale CLAUDE.md on the server**: excluded from deploy since 2026-09-27, but 1.x put a copy in `/public_html/`. Confirm it's gone after the launch deploy.
- **Custom logotype** drawn for Dela rather than Pirata One (deferred, costly).
