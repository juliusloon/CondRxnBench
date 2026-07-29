# Translation Notes

## Status

- Mode: draft reader
- Source: `/Users/juliusloon/Documents/Files/data/CondRxnBench/Buchwald-Hartwig-HTE/Buchwald-Hartwig-HTE.html`
- Source format detected: `html`
- Coverage: the current HTML contains one front-matter summary block, one abstract-like block, and the main body paragraphs extracted into paired English/Chinese spans.

## What was recoverable

- Rebuilt 14 stable source blocks (`S001-S014`) into `paper.md`.
- Preserved a full bilingual reader at paragraph level for all substantive text currently extractable from the HTML.
- Built `source_map.json` so later discussion can cite exact block IDs.

## Missing or weakly grounded content

- No figure images, table markup, or supplementary assets were embedded in this local HTML file, so no `assets/` figure/table cards could be reconstructed.
- Author affiliations are incomplete in the HTML (`07033, USA.` appears without the full institution line), so they were not promoted into the main bilingual body.
- The source appears to be a previously processed or OCR-touched HTML rather than the publisher-native article page.

## Normalizations and corrections

- In `paper.md`, a few obviously broken tokenizations from the HTML were normalized for readability, for example:
  - `cross-couplingof` -> `cross-coupling of`
  - `ovarius potentially ihibitory` -> `various potentially inhibitory`
  - `Using hese descriptors as inputs and reaction yield as ut` -> `Using these descriptors as inputs and reaction yield as output`
  - `anout-sample prediction` -> `and out-of-sample prediction`
  - `syntheticmethodology` -> `synthetic methodology`
  - `highthroughput` -> `high-throughput`
- A few chemistry strings in the Chinese side of the source HTML were also regularized in the rebuilt reader where the original local translation was clearly garbled, especially around `异噁唑`, `Buchwald-Hartwig`, and NMR notation.

## Reading caution

- Because the local HTML is not the raw publisher page, the rebuilt reader should be treated as a source-grounded study copy, not a forensic reproduction of the published layout.
- If you want, the next best upgrade is to pair this reader with the original paper PDF or the Science HTML page so I can restore figures, captions, and supplementary cross-references.
