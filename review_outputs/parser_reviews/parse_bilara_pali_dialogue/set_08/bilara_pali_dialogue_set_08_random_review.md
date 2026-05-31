# Random Sample Review Packet

Source JSONL: `review_outputs/parser_reviews/parse_bilara_pali_dialogue/set_08/bilara_pali_dialogue_set_08.jsonl`
Rows: `10`

## Reviewer Criteria

- Prompt and reply preserve source continuity.
- Speaker labels are coherent and not malformed.
- Assistant target is the next reply only.
- No page headers, footnotes, OCR bleed, or commentary contamination.

## Rows

### Row 1

- Record ID: `sn1-20:bilara_dialogue_4:0-0:a-deity`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn1.20`
- Source lines: `['sn1.20:6.1', 'sn1.20:6.2']`
- Assistant target: `Participant B (a deity)`

#### Prompt

```text
Conversation so far:
Participant B (a deity): Mendicant, you seek alms before you eat; you don't seek alms after eating. But you should eat first, then seek alms: don't let the time pass you by.
Participant A (The Buddha): I actually don't know the time; it's hidden and unseen. That's why I seek alms before eating, so that the time may not pass me by!
Participant B (a deity): You've gone forth while young, mendicant. With pristine black hair, you're blessed with youth, in the prime of life, and you've never flirted with sensual pleasures. Enjoy human sensual pleasures! Don't give up what is apparent in the present to chase after what takes effect over time.
Participant A (The Buddha): I'm not, reverend. I'm giving up what takes effect over time to chase after what is apparent in the present. For the Buddha has said that sensual pleasures take effect over time, with much suffering and distress, and they're all the more full of drawbacks. But this teaching is apparent in the present life, immediately effective, inviting inspection, relevant, so that sensible people can know it for themselves.

Write Participant B's next reply.
```

#### Assistant Target

```text
But in what way, mendicant, has the Buddha said that sensual pleasures take effect over time, with much suffering and distress, and they're all the more full of drawbacks? And how is this teaching apparent in the present life, immediately effective, inviting inspection, relevant, so that sensible people can know it for themselves?
```

### Row 2

- Record ID: `sn1-20:bilara_dialogue_10:0-0:the-buddha`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn1.20`
- Source lines: `['sn1.20:20.1', 'sn1.20:21.5']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant A (a deity): Ask, mendicant, ask! For I have arrived.

Write Participant B's next reply.
```

#### Assistant Target

```text
Sentient beings who perceive the communicable, become established in the communicable. Not understanding the communicable, they fall under the yoke of Death. But having fully understood the communicable, they don't conceive a communicator, for they have nothing by which they might be described. Tell me if you understand, spirit.
```

### Row 3

- Record ID: `sn4-8:bilara_dialogue_1:0-0:the-buddha`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn4.8`
- Source lines: `['sn4.8:3.1', 'sn4.8:3.4']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant A (Māra the Wicked): Children bring you delight! Cattle also bring you delight! For attachments are a man's delight; without attachments there's no delight.

Write Participant B's next reply.
```

#### Assistant Target

```text
Your children bring you sorrow. Your cattle also bring you sorrow. For attachments are a man's sorrow; without attachments there are no sorrows.
```

### Row 4

- Record ID: `dn11:bilara_dialogue_5:0-0:the-buddha`
- Source: `Digha Nikaya`
- Source file: `bilara:dn11`
- Source lines: `['dn11:5.7', 'dn11:6.0']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant B (The Buddha): Kevaḍḍha, I do not teach Dhamma to the mendicants like this: 'Come now, mendicants, perform a superhuman demonstration of psychic power for the white-clothed laypeople.'
Participant A (Kevaḍḍha): Sir, I am not teaching you the Dhamma, but nonetheless I say: 'Sir, this Nāḷandā is successful and prosperous, populous, full of people. Please direct a mendicant to perform a superhuman demonstration of psychic power. Then Nāḷandā will become even more devoted to the Buddha!'
Participant B (The Buddha): Kevaḍḍha, there are three kinds of demonstration, which I declare having realized them with my own insight. What three? The demonstration of psychic power, the demonstration of revealing, and the demonstration of instruction. And what is the demonstration of psychic power? It's a mendicant who wields the many kinds of psychic power: multiplying themselves and becoming one again; materializing and dematerializing; going unobstructed through a wall, a rampart, or a mountain as if through space; diving in and out of the earth as if it were water; walking on water as if it were earth; flying cross-legged through the sky like a bird; touching and stroking with the hand the sun and moon, so mighty and powerful; controlling the body as far as the realm of divinity. Someone with faith and confidence sees that mendicant performing those superhuman feats. They tell someone else who lacks faith and confidence: 'Oh lord, how incredible, how amazing! The ascetic has such psychic power and might! I saw him myself, performing all these superhuman feats!' But the one lacking faith and confidence would say to them: 'There's a spell named Gandhārī. Using that a mendicant can perform such superhuman feats.' What do you think, Kevaḍḍha? Wouldn't someone lacking faith speak like that?
Participant A (Kevaḍḍha): They would, sir.

Write Participant B's next reply.
```

#### Assistant Target

```text
Seeing this drawback in psychic power, I'm horrified, repelled, and disgusted by demonstrations of psychic power.
```

### Row 5

- Record ID: `dn23:bilara_dialogue_27:0-0:kassapa-the-prince`
- Source: `Digha Nikaya`
- Source file: `bilara:dn23`
- Source lines: `['dn23:11.16', 'dn23:11.27']`
- Assistant target: `Participant B (Kassapa the Prince)`

#### Prompt

```text
Conversation so far:
Participant B (Kassapa the Prince): How, exactly, chieftain?
Participant A (Pāyāsi): Well, I have friends and colleagues, relatives and kin who refrain from killing living creatures and so on. Some time later they become sick, suffering, gravely ill. When I know that they will not recover from their illness, I go to them and say, 'Sirs, there are some ascetics and brahmins who have this doctrine and view:
Participant B (Kassapa the Prince): Well then, chieftain, I'll ask you about this in return, and you can answer as you like. A hundred human years are equivalent to one day and night for the gods of the thirty-three. Thirty such days make a month, and twelve months make a year. The gods of the thirty-three have a lifespan of a thousand such years. Now, as to your friends who are reborn in the company of the gods of the thirty-three after doing good things. If they think, 'First I'll amuse myself for two or three days, supplied and provided with the five kinds of heavenly sensual stimulation. Then I'll go back to Pāyāsi and tell him that there is an afterlife.' Would they come back to tell you that there is an afterlife?
Participant A (Pāyāsi): No, worthy Kassapa. For I would be long dead by then. But worthy Kassapa, who has told you that the gods of the thirty-three exist, or that they have such a long lifespan? I don't believe you.

Write Participant B's next reply.
```

#### Assistant Target

```text
Chieftain, suppose there was a person blind from birth. They couldn't see sights that are dark or bright, or blue, yellow, red, or magenta. They couldn't see even and uneven ground, or the stars, or the moon and sun. They'd say, 'There's no such thing as dark and bright sights, and no-one who sees them. There's no such thing as blue, yellow, red, magenta, even and uneven ground, stars, moon and sun, and no-one who sees these things. I don't know it or see it, therefore it doesn't exist.' Would they be speaking rightly?
```

### Row 6

- Record ID: `sn2-23:bilara_dialogue_2:0-0:ser`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn2.23`
- Source lines: `['sn2.23:5.1', 'sn2.23:5.2']`
- Assistant target: `Participant B (Serī)`

#### Prompt

```text
Conversation so far:
Participant B (Serī): Both gods and humans enjoy their food. So what's the name of the spirit who doesn't like food?
Participant A (The Buddha): Those who give with faith and a clear and confident heart, partake of food in this world and the next. So you should dispel stinginess, overcoming that stain, and give a gift. The good deeds of sentient beings support them in the next world.

Write Participant B's next reply.
```

#### Assistant Target

```text
It's incredible, sir, it's amazing, how well said this was by the Buddha.
```

### Row 7

- Record ID: `sn3-12:bilara_dialogue_12:0-0:the-buddha`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn3.12`
- Source lines: `['sn3.12:11.1', 'sn3.12:11.4']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant B (The Buddha): I feel inspired to speak, Blessed One! I feel inspired to speak, Holy One!
Participant A (Pasenadi): Then speak as you feel inspired,

Write Participant B's next reply.
```

#### Assistant Target

```text
Like a fragrant pink lotus that blooms at daybreak, its fragrance unfadedsee Aṅgīrasa shine, bright as the sun in the sky!
```

### Row 8

- Record ID: `sn4-19:bilara_dialogue_2:0-0:m-ra-the-wicked`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn4.19`
- Source lines: `['sn4.19:2.7', 'sn4.19:2.14']`
- Assistant target: `Participant B (Māra the Wicked)`

#### Prompt

```text
Conversation so far:
Participant B (Māra the Wicked): So, ascetic, did you happen to see any oxen?
Participant A (The Buddha): But what have you to do with oxen, Wicked One?

Write Participant B's next reply.
```

#### Assistant Target

```text
Mine alone, ascetic, is the eye, mine are sights, mine is the field of eye contact consciousness. Where can you escape me, ascetic? Mine alone is the ear... nose... tongue... body... mind, mine are ideas, mine is the field of mind contact consciousness. Where can you escape me, ascetic?
```

### Row 9

- Record ID: `dn6:bilara_dialogue_17:0-0:the-buddha`
- Source: `Digha Nikaya`
- Source file: `bilara:dn6`
- Source lines: `['dn6:13.1', 'dn6:13.1']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant B (The Buddha): What is the cause, sir, what is the reason why Sunakkhatta cannot hear them, even though they really do exist?
Participant A (Oṭṭhaddha the Licchavi): Mahāli, take a mendicant who has developed immersion to the eastern quarter in one aspect: so as to see heavenly sights but not to hear heavenly sounds. When they have developed immersion for that purpose, they see heavenly sights but don't hear heavenly sounds. Why is that? Because that is how it is for a mendicant who develops immersion in that way. Furthermore, take a mendicant who has developed immersion to the southern quarter in one aspect... western quarter... northern quarter... above, below, across... That is how it is for a mendicant who develops immersion in that way. Take a mendicant who has developed immersion to the eastern quarter in one aspect: so as to hear heavenly sounds but not to see heavenly sights. When they have developed immersion for that purpose, they hear heavenly sounds but don't see heavenly sights. Why is that? Because that is how it is for a mendicant who develops immersion in that way. Furthermore, take a mendicant who has developed immersion to the southern quarter in one aspect... western quarter... northern quarter... above, below, across... That is how it is for a mendicant who develops immersion in that way. Take a mendicant who has developed immersion to the eastern quarter in both aspects: so as to hear heavenly sounds and see heavenly sights. When they have developed immersion for that purpose, they see heavenly sights and hear heavenly sounds. Why is that? Because that is how it is for a mendicant who develops immersion in that way. Furthermore, take a mendicant who has developed immersion to the southern quarter in both aspects... western quarter... northern quarter... above, below, across... That is how it is for a mendicant who develops immersion in that way. This is the cause, Mahāli, this is the reason why Sunakkhatta cannot hear heavenly sounds that are pleasant, sensual, and arousing, even though they really do exist.
Participant B (The Buddha): Surely the mendicants must lead the spiritual life under the Buddha for the sake of realizing such a development of immersion?
Participant A (Oṭṭhaddha the Licchavi): No, Mahāli, the mendicants don't lead the spiritual life under me for the sake of realizing such a development of immersion. There are other things that are finer, for the sake of which the mendicants lead the spiritual life under me.

Write Participant B's next reply.
```

#### Assistant Target

```text
But sir, what are those finer things?
```

### Row 10

- Record ID: `sn1-34:bilara_dialogue_1:0-0:the-buddha`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn1.34`
- Source lines: `['sn1.34:3.1', 'sn1.34:3.3']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant A (a deity): Among mankind there are no sensual pleasures that are permanent. Here there are sensuous things, bound to which, drunk on which, there's no coming back. That person doesn't return from Death's dominion.

Write Participant B's next reply.
```

#### Assistant Target

```text
Gloom is born of desire; suffering is born of desire; when desire is removed, gloom is removed; when gloom is removed, suffering is removed.
```
