# Full Buddhist Dialogue Dataset Review Sample

Sampled rows: `10`
Source dataset: `/Users/wewlad/GitHub/AI_Training_Tests/review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl`

## Review Example 1: Milinda Panha

- Record ID: `milinda-panha-txt:quoted_buddhist_next_reply_1:1618-1633:venerable-nagasena`
- Kind: `quoted_buddhist_next_reply`
- Lines: `Milinda Panha.txt:1618-1633`
- Target: `Participant B (Venerable Nagasena)`
- Target words: `27`

### User Prompt

```text
Conversation so far:
Participant A (King Milinda): Revered Nāgasena, will you converse with me?

Write Participant B's next reply.
```

### Assistant Target

```text
I will converse if you, sire, will converse in the speech of the learned, but if you converse in the speech of kings I will not converse.
```

## Review Example 2: The Gateless Gate

- Record ID: `gateless-gate-wikisource-raw-json:gateless_gate_koan_commentary_4:4-4:mumon`
- Kind: `gateless_gate_koan_commentary`
- Lines: `gateless_gate_wikisource_raw.json:4-4`
- Target: `Participant B (Mumon)`
- Target words: `55`

### User Prompt

```text
Conversation so far:
Participant A (Koan case 4: A Beardless Foreigner): Wakuan complained when he saw a picture of bearded Bodhidharma: "Why hasn't that fellow a beard?"

Write Participant B (Mumon)'s next reply.
```

### Assistant Target

```text
If you want to study Zen, you must study it with your heart. When you attain realization, it must be true realization. You yourself must have the face of the great Bodhidharma to see him. Just one such glimpse will be enough. But if you say you met him, you never saw him at all.
```

## Review Example 3: The Gateless Gate

- Record ID: `gateless-gate-wikisource-raw-json:gateless_gate_internal_dialogue_1_1:1-1:joshu`
- Kind: `gateless_gate_internal_dialogue`
- Lines: `gateless_gate_wikisource_raw.json:1-1`
- Target: `Participant B (Joshu)`
- Target words: `1`

### User Prompt

```text
Conversation so far:
Participant A (Monk): Has a dog Buddha-nature or not?

Write Participant B (Joshu)'s next reply.
```

### Assistant Target

```text
Mu.
```

## Review Example 4: The Diamond Sutra

- Record ID: `diamond-sutra-gutenberg-txt:diamond_sutra_subhuti_next_reply_98:2865-2973:subhuti`
- Kind: `diamond_sutra_subhuti_next_reply`
- Lines: `diamond_sutra_gutenberg.txt:2865-2973`
- Target: `Participant A (Subhuti)`
- Target words: `22`

### User Prompt

```text
Conversation so far:
Participant A (Subhuti): Honoured of the Worlds! it is improbable that the Lord Buddha can be perceived by means of any physical phenomena. And why? Because, what the Lord Buddha referred to as 'physical phenomena,' are not in reality 'physical phenomena,' these are merely termed 'physical phenomena.'
Participant B (Lord Buddha): Do not affirm that the Lord Buddha thinks thus within himself, 'I ought to promulgate a system of Law or doctrine.' Have no such irrelevant thought! And why? Because, if a disciple affirmed that the Lord Buddha promulgated a system of Law or doctrine, he would defame the Lord Buddha, being manifestly unable to understand the purport of my instruction. Subhuti, regarding the promulgation of a 'system of Law or doctrine,' there is in reality no 'system of Law or doctrine' to promulgate, it is merely termed a 'system of Law or doctrine.'
Participant A (Subhuti): Honoured of the Worlds! in ages to come, will sentient beings destined to hear this Law, engender within their minds the essential elements of faith?
Participant B (Lord Buddha): Subhuti, it cannot be asserted that these are sentient beings, or that these are not sentient beings. And why? Because, Subhuti, regarding 'sentient beings,' the Lord Buddha declared that in reality these are not 'sentient beings,' they are merely termed 'sentient beings.'

Write Participant A's ne...
```

### Assistant Target

```text
Honoured of the Worlds! did the Lord Buddha, in attaining to supreme spiritual wisdom, obtain nothing of a real or tangible nature?
```

## Review Example 5: Udana

- Record ID: `udana-txt:udana_blessed_one_exclamation_8-6:5647-5831:blessed-one`
- Kind: `udana_blessed_one_exclamation`
- Lines: `udana.txt:5647-5831`
- Target: `Participant B (Blessed One)`
- Target words: `23`

### User Prompt

```text
Conversation so far:
Participant A (Narrator): I have heard that on one occasion, while the Blessed One was wandering among the Magadhans with a large community of monks, he arrived at Patali Village. The lay followers of Patali Village heard, "The Blessed One, they say, while wandering among the Magadhans with a large community of monks, has reached Patali Village." So they went to the Blessed One and, on arrival, having bowed down to him, sat to one side. As they were sitting there, they said to him, "Lord, may the Blessed One acquiesce to (the use of) the rest-house hall." The Blessed One acquiesced with silence. Sensing his acquiescence, the lay followers of Patali Village got up from their seats, bowed down to him, circled him to the right, and then went to the rest-house hall. On arrival, they spread it all over with felt rugs, arranged seats, set out a water vessel, and raised an oil lamp. Then they went to the Blessed One and, on arrival, having bowed down, stood to one side. As they were standing there they said to him, "Lord, the resthouse hall has been covered all over with felt rugs, seats have been arranged, a water vessel has been set out, and an oil lamp raised. May the Blessed One do what you think it is now time to do." So the Blessed One, adjusting his under robe and - carrying his bowl & robes - went together with a community of monks to the rest-house hal...
```

### Assistant Target

```text
Those
who cross the foaming flood,
having made a bridge, avoiding the swamps
- while people are binding rafts -
have already crossed
: the wise.
```

## Review Example 6: Majjhima Nikaya

- Record ID: `mn35-html:majjhima_nikaya_next_reply_35_14:220-224:the-buddha`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN35.html:220-224`
- Target: `Participant B (The Buddha)`
- Target words: `30`

### User Prompt

```text
Conversation so far:
Participant B (The Buddha): What does this great multitude have to do with you? Please focus just on your own assertion.
Participant A (Ven. Assaji): Yes, Master Gotama, I'm saying that 'Form is my self, feeling is my self, perception is my self, fabrications are my self, consciousness is my self.'
Participant B (The Buddha): Very well then, Aggivessana, I will cross-question you on this matter. Answer as you see fit. What do you think? Would a consecrated, noble-warrior king-such as King Pasenadi of Kosala or King Ajātasattu Vedehiputta of Magadha-wield the power in his own domain to execute those (he has) sentenced to be executed, to fine those (he has) sentenced to be fined, or to banish those (he has) sentenced to be banished?
Participant A (Ven. Assaji): Yes, Master Gotama, he would wield the power in his own domain to execute those (he has) sentenced to be executed, to fine those (he has) sentenced to be fined, or to banish those (he has) sentenced to be banished. Even these oligarchic groups, such as the Vajjians & Mallans, wield the power in their own domains to execute those (they've) sentenced to be executed, to fine those (they've) sentenced to be fined, or to banish those (they've) sentenced to be banished, to say nothing of a consecrated, noble-warrior king such as King Pasenadi of Kosala, or King Ajātasattu Vedehiputta of Magadha. He would...
```

### Assistant Target

```text
What do you think, Aggivessana? When you say, 'Form is my self,' do you wield power over that form: 'May my form be thus, may my form not be thus'?
```

## Review Example 7: Majjhima Nikaya

- Record ID: `mn82-html:majjhima_nikaya_next_reply_82_32:322-327:ven-ra-hap-la`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN82.html:322-327`
- Target: `Participant B (Ven. Raṭṭhapāla)`
- Target words: `106`

### User Prompt

```text
Conversation so far:
Participant B (Ven. Raṭṭhapāla): It was in reference to this, great king, that the Blessed One who knows & sees, worthy & rightly self-awakened, said: 'The world is without ownership. One has to pass on, leaving everything behind.' Having known & seen & heard this, I went forth from the home life into homelessness.
Participant A (King Koravya): Now, Master Raṭṭhapāla, you say, 'The world is insufficient, insatiable, a slave to craving.' How is the meaning of this statement to be understood?
Participant B (Ven. Raṭṭhapāla): What do you think, great king? Do you now rule over the prosperous country of Kuru?
Participant A (King Koravya): That is so, Master Raṭṭhapāla. I rule over the prosperous country of Kuru.

Write Participant B's next reply.
```

### Assistant Target

```text
What do you think, great king? Suppose a trustworthy, reliable man of yours were to come to you from the east. On arrival he would say to you, 'May it please your majesty to know, I have come from the east. There I saw a great country, powerful & prosperous, populous & crowded with people. Plenty are the elephant troops there, plenty the cavalry troops, chariot troops, & infantry troops. Plenty is the ivory-work there, plenty the gold & silver, both worked & unworked. Plenty are the women for the taking. It is possible, with the forces you now have, to conquer it. Conquer it, great king!' What would you do?
```

## Review Example 8: Itivuttaka

- Record ID: `itivuttaka-thanissaro-txt:itivuttaka_prose_to_verse_36:989-1021:blessed-one`
- Kind: `itivuttaka_prose_to_verse`
- Lines: `itivuttaka_thanissaro.txt:989-1021`
- Target: `Participant B (Blessed One)`
- Target words: `55`

### User Prompt

```text
Itivuttaka section 36

Prose teaching:
Monks, this holy life is lived, not for the sake of deceiving people, not for the sake of inveigling people, not for the sake of the rewards of gain, offerings, & tribute, nor with the thought, 'Thus may people know me.' This holy life is lived for the sake of direct knowledge & full comprehension.

Write the verse summary attached to this teaching.
```

### Assistant Target

```text
For the sake of direct knowledge & full
comprehension,
he, the Blessed One, taught
a holy life not handed down,
coming ashore
in Unbinding.
This path is pursued
by those great in purpose,
great seers.
Those who follow it,
as taught by the One Awakened,
heeding the Teacher's message,
will put an end
to suffering & stress.
```

## Review Example 9: Zen Koans Database

- Record ID: `zen-koans-database:zen_koans_database_clean_dialogue_just_go_to_sleep_4:1-7:gasan`
- Kind: `zen_koans_database_clean_dialogue`
- Lines: `just_go_to_sleep.html:1-7`
- Target: `Participant B (Gasan)`
- Target words: `9`

### User Prompt

```text
Conversation so far:
Participant B (Gasan): When your sickness is over we want you to speak there,
Participant B (Gasan): Then we will get someone else,
Participant A (Tekisui): Suppose you cannot find anyone?

Write Participant B (Gasan)'s next reply.
```

### Assistant Target

```text
Don't ask such foolish questions. Just go to sleep.
```

## Review Example 10: Vimalakirti Nirdesa Sutra

- Record ID: `vimalakirti-nirdesa-sutra-txt:vimalakirti_next_reply:4745-4755:the-buddha`
- Kind: `vimalakirti_next_reply`
- Lines: `vimalakirti_nirdesa_sutra.txt:4745-4755`
- Target: `Participant B (The Buddha)`
- Target words: `27`

### User Prompt

```text
Conversation so far:
Participant B (The Buddha): Receive then, Ánanda, this expression of the teaching of the Dharma. Remember it, and teach it widely and correctly to others!
Participant A (Ánanda): I have memorized, Lord, this expression of the teaching of the Dharma. But what is the name of this teaching, and how should I remember it?

Write Participant B's next reply.
```

### Assistant Target

```text
Ánanda, this exposition of the Dharma is called 'The Teaching of Vimalakirti,' or 'The Reconciliation of Dichotomies,' or even 'Section of the Inconceivable Liberation.' Remember it thus!
```
