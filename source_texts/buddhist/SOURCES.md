# Buddhist Source Texts

## The Gateless Gate / Mumonkan

- Source: Wikisource MediaWiki API export of `The Gateless Gate/*` pages.
- URL: `https://en.wikisource.org/wiki/The_Gateless_Gate`
- Raw API pattern: `https://en.wikisource.org/w/api.php?action=query&generator=allpages&gapfrom=The%20Gateless%20Gate/&gapprefix=The%20Gateless%20Gate/&gaplimit=100&prop=revisions&rvprop=content&rvslots=main&format=json`
- Translation: Nyogen Senzaki and Paul Reps, 1934.
- License/status note: Wikisource hosts this as public domain in the United States.
- Local file: `gateless_gate_wikisource_raw.json`

## The Diamond Sutra

- Source: Project Gutenberg ebook 64623.
- URL: `https://www.gutenberg.org/ebooks/64623`
- Plain text URL used: `https://www.gutenberg.org/files/64623/64623-0.txt`
- Translation: William Gemmell, 1912.
- License/status note: Project Gutenberg texts are public domain in the United States.
- Local file: `diamond_sutra_gutenberg.txt`

## The Blue Cliff Record / Odes to a Classic Hundred Standards

- Source: archived web page by Alan Gregory Wonderwheel.
- URL: `https://web.archive.org/web/20150623133457/http://home.pon.net/wildrose/BCR-Eng.htm`
- Translation/source note: English rendering of Xuedou's `Odes to a Classic Hundred Standards`
  from the Blue Cliff Record tradition.
- License/status note: personal/local-only project source; do not treat this as a
  clean public-domain English translation unless a clearer license is found.
- Local file: `raw/blue_cliff_record_wonderwheel_wayback.html`

## User-Supplied Buddhist PDFs

These files were placed in `source_texts/buddhist/raw/` and converted locally with
`pdftotext -layout` into `source_texts/buddhist/clean/` for parser development.

- `Vimalakirti-Nirdesa-Sutra.pdf`
  - Extracted text: `vimalakirti_nirdesa_sutra.txt`
  - Note: Robert A. F. Thurman translation; likely copyrighted. Prefer review before
    using in any reusable dataset.
- `Bhikkhu Pesala_Dhammapada and Commentary.pdf`
  - Extracted text: `dhammapada_pesala_commentary.txt`
  - Note: PDF states personal printing is allowed and other rights reserved.
- `SuttaNipata210221.pdf`
  - Extracted text: `sutta_nipata.txt`
  - Note: Thanissaro Bhikkhu translation, CC BY-NC 4.0 per PDF title page.
- `udana.pdf`
  - Extracted text: `udana.txt`
  - Note: PDF allows copying/reprinting for free distribution, otherwise all rights
    reserved.
- `Dhamma-Verses-Comm.pdf`
  - Extracted text: `dhamma_verses_commentary.txt`
  - Note: large commentary source; parser not yet built.
- `iti-than.pdf`
  - Extracted text: `itivuttaka_thanissaro.txt`
  - Note: PDF allows copying/reprinting for free distribution, otherwise all rights
    reserved.
