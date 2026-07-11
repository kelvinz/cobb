# Imagery Mode

Use this mode for non-interactive visual artifacts such as posters, editorial covers, art sheets, one-page compositions, and animated SVG compositions.

## Output Types

Produce:

1. A design philosophy `.md`.
2. One `.png` or `.pdf` artifact unless multi-page output is requested; one `.svg` when the request is an animated composition.

## Generation Mechanism

1. Default: generate the artifact with an available image-generation tool or model (e.g. GPT image generation). Drive it with a prompt built from the philosophy, conceptual thread, palette, typography intent, and composition plan — not the raw user request.
2. Animated SVG requests: author the SVG markup directly instead of using image generation; keep animation declarative (SMIL/CSS) and respect reduced-motion.
3. For `.pdf` delivery, produce the raster image first, then convert or wrap it to PDF at the required DPI with a locally available tool.
4. If no image-generation tool is available, deliver the philosophy plus an SVG or HTML source rendition of the composition and the exact conversion command, and state clearly that final rendering is pending.

## Delivery Contract

For each imagery request, deliver:

1. Philosophy markdown with a named movement and four to six paragraphs.
2. Final artifact path and format.
3. Canvas dimensions/orientation and why they fit the composition.
4. Palette summary (three to five colors) and typography choices.
5. One-sentence alt text describing the final composition.

## Step 1: Create the Visual Philosophy

Write the philosophy before drawing:

1. Name the movement in one or two words.
2. Write four to six concise paragraphs covering form, space, color, rhythm, hierarchy, and material feel.
3. Emphasize craftsmanship and refinement.
4. Keep language visual-first.
5. Leave room for interpretation while staying specific.

### Example Philosophy

```markdown
# Tectonic Stillness

Form emerges from pressure held in check. Each shape suggests mass
without heaviness — slabs of muted mineral color stacked with deliberate
asymmetry, as though the composition settled under its own weight.

Space is structural. Generous margins frame dense clusters of type and
geometry, creating silence that amplifies the focal element. Nothing
floats; every edge implies a ledge or seam.

Color stays earthbound — slate, graphite, oxidised copper — with one
controlled moment of cooled blue that reads as sky glimpsed through
architecture. Saturation is low; contrast does the heavy lifting.

Rhythm is geological: slow horizontal bands interrupted by a single
vertical cut. Typography follows the same logic — wide tracking,
medium weight, uppercase — sitting flush against hard edges as though
carved in.
```

## Step 2: Extract a Conceptual Thread

Derive a subtle non-literal thread from the brief:

1. Keep it recognizable to context-aware viewers.
2. Keep it compelling to viewers without context.
3. Embed it through form, color, rhythm, and composition instead of explicit explanation.

## Step 3: Compose the Artifact

Default to one page unless the request says otherwise.

1. Prioritize composition, shape, pattern, atmosphere, and spatial hierarchy.
2. Keep text minimal and treat text as visual material.
3. Keep all elements inside canvas boundaries with deliberate margins.
4. Avoid overlap and cropping mistakes.
5. Use a limited, intentional palette.
6. Reuse motifs to build coherence.
7. Choose typography intentionally and avoid generic defaults.
8. Keep sophistication high even for pop-culture subjects.

When local fonts are available, prefer curated sets under a project-local `fonts/` directory.

## Step 4: Run a Mandatory Refinement Pass

Run one extra polish pass before delivery:

1. Tighten alignment and spacing rhythm.
2. Improve contrast hierarchy and readability.
3. Remove clutter and weak details.
4. Increase crispness and finish quality.

If the instinct is to add new elements, attempt to improve the existing composition first.

## Export and Licensing Checklist

Run before delivering the final artifact:

1. For `.pdf`: confirm DPI (default 300 for print, 72 for screen), embed all fonts, and include bleed/crop marks when the output is for physical production.
2. For `.png`: confirm resolution and dimensions suit the target medium.
3. Fonts: use only project-local fonts from `fonts/` or openly licensed typefaces. State the licence for each typeface used.
4. Images and textures: confirm licensing allows the intended use. Prefer project-local or openly licensed assets.
5. Color profile: use sRGB for screen, CMYK for print. State which profile was applied.

## Multi-Page Extension

When multiple pages are requested:

1. Preserve one shared philosophy.
2. Vary pacing, composition, and focal strategy.
3. Make each page distinct but clearly part of one series.
