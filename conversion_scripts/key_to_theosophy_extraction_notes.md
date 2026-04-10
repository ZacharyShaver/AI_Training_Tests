# Key To Theosophy Extraction Notes

- Source file: `the_key-to-theosophy.txt`
- Extraction style: explicit dialogue-prefix extraction using speaker labels such as `ENQUIRER.` and `THEOSOPHIST.`
- Excluded material: title matter, table of contents, preface, glossary
- Speaker cue expansion supported in extractor: `ENQUIRER`, `INQUIRER`, `QUESTIONER`, `Q`, `THEOSOPHIST`, `ANSWERER`, `A`
- Confidence policy: `high` when an `Enquirer` turn is immediately followed by a `Theosophist` reply in the same section and subsection; `medium` when the reply crosses subsection boundaries

- Parsed turns: 995
- Q&A pairs: 390
- High-confidence pairs: 389

## Section Counts

- SECTION 10: ON THE NATURE OF OUR THINKING PRINCIPLE: 19
- SECTION 11: ON THE MYSTERIES OF RE- INCARNATION: 35
- SECTION 12: WHAT IS PRACTICAL THEOSOPHY?: 57
- SECTION 13: ON THE MISCONCEPTIONS ABOUT THE THEOSOPHICAL SOCIETY: 46
- SECTION 14: THE "THEOSOPHICAL MAHATMAS": 32
- SECTION 1: THEOSOPHY AND THE THEOSOPHICAL SOCIETY: 22
- SECTION 2: EXOTERIC AND ESOTERIC THEOSOPHY: 30
- SECTION 3: THE WORKING SYSTEM OF THE T. S.: 20
- SECTION 4: THE RELATIONS OF THE THEOSOPHICAL SOCIETY TO THEOSOPHY: 10
- SECTION 5: THE FUNDAMENTAL TEACHINGS OF THEOSOPHY: 29
- SECTION 6: THEOSOPHICAL TEACHINGS AS TO NATURE AND MAN: 18
- SECTION 7: ON THE VARIOUS POST MORTEM STATES: 15
- SECTION 8: ON RE-INCARNATION OR RE-BIRTH: 16
- SECTION 9: ON THE KAMA-LOKA AND DEVACHAN: 41

## Top Subsections

- ARE THEY "SPIRITS OF LIGHT" OR "GOBLINS DAMN'D"?: 24
- WHAT A THEOSOPHIST OUGHT NOT TO DO: 17
- WHY THEOSOPHISTS DO NOT BELIEVE IN THE RETURN OF PURE "SPIRITS": 14
- IS THE THEOSOPHICAL SOCIETY A MONEY-MAKING CONCERN?: 12
- WHY, THEN, IS THERE SO MUCH PREJUDICE AGAINST THE T. S.?: 12
- ON SELF-SACRIFICE: 11
- IS IT NECESSARY TO PRAY?: 10
- THE DOCTRINE IS TAUGHT IN ST JOHN'S GOSPEL: 10
- THE RELATIONS OF THE T. S. TO POLITICAL REFORMS: 10
- WHAT IS KARMA?: 10
- WHAT IS REALLY MEANT BY ANNIHILATION: 10
- ON POST-MORTEM AND POST-NATAL CONSCIOUSNESS 29: 9

## Caveats

- This text is unusually clean for extraction because most exchanges are explicitly prefixed with named speakers.
- Standalone numbered footnote blocks are stripped during parsing so they do not bleed into answer text.
- A few answers span multiple paragraphs or include quoted material inside the answer; these are preserved as single answer blocks for training usefulness.
- The extractor was written with broader prefix support so the same pattern family can be reused on similar dialogue texts with `Q.` / `A.` or `Questioner.` / `Answerer.` labels.
