# Random Sample Review Packet

Source JSONL: `review_outputs/parser_reviews/parse_bilara_pali_dialogue/set_05/bilara_pali_dialogue_set_05.jsonl`
Rows: `10`

## Reviewer Criteria

- Prompt and reply preserve source continuity.
- Speaker labels are coherent and not malformed.
- Assistant target is the next reply only.
- No page headers, footnotes, OCR bleed, or commentary contamination.

## Rows

### Row 1

- Record ID: `sn3-6:bilara_dialogue_2:0-0:king-pasenadi`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn3.6`
- Source lines: `['sn3.6:3.1', 'sn3.6:3.6']`
- Assistant target: `Participant B (King Pasenadi)`

#### Prompt

```text
Conversation so far:
Participant B (King Pasenadi): Just now, sir, as I was in private retreat this thought came to mind: 'Few are the sentient beings in the world who, when they obtain luxury possessions, don't grow indulgent and negligent, giving in to greed for sensual pleasures, and doing the wrong thing by others. There are many more who, when they obtain luxury possessions, do grow indulgent and negligent, giving in to greed for sensual pleasures, and doing the wrong thing by others.'
Participant A (The Buddha): That's so true, great king! That's so true!

Write Participant B's next reply.
```

#### Assistant Target

```text
Full of desire for possessions and pleasures, greedy, infatuated by sensual pleasures; they don't notice that they've gone too far, like deer ensnared in a trap set out. It'll be bitter later on; for the result will be bad for them.
```

### Row 2

- Record ID: `dn2:bilara_dialogue_30:0-0:the-buddha`
- Source: `Digha Nikaya`
- Source file: `bilara:dn2`
- Source lines: `['dn2:100.1', 'dn2:100.3']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant A (King Ajātasattu): Excellent, sir! Excellent! As if he were righting the overturned, or revealing the hidden, or pointing out the path to the lost, or lighting a lamp in the dark so people with clear eyes can see what's there, the Buddha has made the teaching clear in many ways. I go for refuge to the Buddha, to the teaching, and to the mendicant Saṅgha. From this day forth, may the Buddha remember me as a lay follower who has gone for refuge for life. I made a mistake, sir. It was foolish, stupid, and unskillful of me to take the life of my father, a just and principled king, for the sake of authority. Please, sir, accept my mistake for what it is, so I will restrain myself in future.

Write Participant B's next reply.
```

#### Assistant Target

```text
Indeed, great king, you made a mistake. It was foolish, stupid, and unskillful of you to take the life of your father, a just and principled king, for the sake of sovereignty. But since you have recognized your mistake for what it is, and have dealt with it properly, I accept it. For it is growth in the training of the Noble One to recognize a mistake for what it is, deal with it properly, and commit to restraint in the future.
```

### Row 3

- Record ID: `sn7-5:bilara_dialogue_1:0-0:the-buddha`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn7.5`
- Source lines: `['sn7.5:2.1', 'sn7.5:2.6']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant A (the brahmin Bhāradvāja the Harmless): I am Harmless, worthy Gotama, I am Harmless!

Write Participant B's next reply.
```

#### Assistant Target

```text
If you were really like your name, then you'd be Harmless. But a truly harmless person does no harm by way of body, speech, or mind; they don't harm anyone else.
```

### Row 4

- Record ID: `sn8-7:bilara_dialogue_1:0-0:venerable-s-riputta`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn8.7`
- Source lines: `['sn8.7:2.2', 'sn8.7:2.6']`
- Assistant target: `Participant B (Venerable Sāriputta)`

#### Prompt

```text
Conversation so far:
Participant A (The Buddha): Come now, monks, I invite you all: Is there anything I've done by way of body or speech that you would criticize?

Write Participant B's next reply.
```

#### Assistant Target

```text
There is nothing, sir, that you've done by way of body or speech that we would criticize. For the Blessed One gave rise to the unarisen path, gave birth to the unborn path, and explained the unexplained path. He is the knower of the path, the discoverer of the path, the expert on the path. And now the disciples live following the path; they acquire it later. And sir, I invite the Blessed One. Is there anything I've done by way of body or speech that you would criticize?
```

### Row 5

- Record ID: `dn2:bilara_dialogue_26:0-0:king-aj-tasattu`
- Source: `Digha Nikaya`
- Source file: `bilara:dn2`
- Source lines: `['dn2:39.2', 'dn2:39.3']`
- Assistant target: `Participant B (King Ajātasattu)`

#### Prompt

```text
Conversation so far:
Participant B (King Ajātasattu): What do you think, great king? If this is so, is there a fruit of the ascetic life apparent in the present life or not?
Participant A (The Buddha): Clearly, sir, there is.
Participant B (King Ajātasattu): This is the second fruit of the ascetic life that's apparent in this very life, which I point out to you.
Participant A (The Buddha): But sir, can you point out a fruit of the ascetic life that's apparent in this very life which is better and finer than these?

Write Participant B's next reply.
```

#### Assistant Target

```text
I can, great king. Well then, listen and apply your mind well, I will speak.
```

### Row 6

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

### Row 7

- Record ID: `dn21:bilara_dialogue_59:0-0:sakka`
- Source: `Digha Nikaya`
- Source file: `bilara:dn21`
- Source lines: `['dn21:2.10.10', 'dn21:2.10.10']`
- Assistant target: `Participant B (Sakka)`

#### Prompt

```text
Conversation so far:
Participant B (Sakka): Dear Pañcasikha, you were very helpful to me, since you first charmed the Buddha, after which I went to see him. I shall appoint you to your father's position-you shall be king of the centaurs. And I give you Bhaddā Suriyavaccasā, for she loves you very much.
Participant A (The Buddha): Homage to him, the blessed one, the perfected one, the fully awakened Buddha! Homage to him, the blessed one, the perfected one, the fully awakened Buddha! Homage to him, the blessed one, the perfected one, the fully awakened Buddha!

Write Participant B's next reply.
```

#### Assistant Target

```text
Everything that is liable to arise is liable to cease.
```

### Row 8

- Record ID: `dn5:bilara_dialogue_23:0-0:the-buddha`
- Source: `Digha Nikaya`
- Source file: `bilara:dn5`
- Source lines: `['dn5:22.1', 'dn5:22.1']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant A (a brahmin): How can you not applaud the ascetic Gotama's fine words?
Participant B (The Buddha): It's not that I don't applaud what he said. If anyone didn't applaud such fine words, their head would explode! But, gentlemen, it occurs to me that the ascetic Gotama does not say: 'So I have heard' or 'It ought to be like this.' Rather, he just says: 'So it was then, this is how it was then.' It occurs to me that the ascetic Gotama at that time must have been King Mahāvijita, the owner of the sacrifice, or else the brahmin high priest who facilitated the sacrifice for him. Does the worthy Gotama recall having performed such a sacrifice, or having facilitated it, and then, when his body broke up, after death, being reborn in a good place, a heavenly realm?
Participant A (a brahmin): I do recall that, brahmin. For I myself was the brahmin high priest at that time who facilitated the sacrifice.

Write Participant B's next reply.
```

#### Assistant Target

```text
But Mister Gotama, apart from that sacrifice accomplished with three modes and sixteen accessories, is there any other sacrifice that has fewer obligations and undertakings, yet is more fruitful and beneficial?
```

### Row 9

- Record ID: `dn11:bilara_dialogue_2:0-0:keva-ha`
- Source: `Digha Nikaya`
- Source file: `bilara:dn11`
- Source lines: `['dn11:2.2', 'dn11:2.6']`
- Assistant target: `Participant B (Kevaḍḍha)`

#### Prompt

```text
Conversation so far:
Participant B (Kevaḍḍha): Sir, this Nāḷandā is successful and prosperous, populous, full of people. Please direct a mendicant to perform a superhuman demonstration of psychic power. Then Nāḷandā will become even more devoted to the Buddha!
Participant A (The Buddha): Kevaḍḍha, I do not teach Dhamma to the mendicants like this: 'Come now, mendicants, perform a superhuman demonstration of psychic power for the white-clothed laypeople.'

Write Participant B's next reply.
```

#### Assistant Target

```text
Sir, I am not teaching you the Dhamma, but nonetheless I say: 'Sir, this Nāḷandā is successful and prosperous, populous, full of people. Please direct a mendicant to perform a superhuman demonstration of psychic power. Then Nāḷandā will become even more devoted to the Buddha!'
```

### Row 10

- Record ID: `dn25:bilara_dialogue_19:0-0:a-wanderer`
- Source: `Digha Nikaya`
- Source file: `bilara:dn25`
- Source lines: `['dn25:18.16', 'dn25:18.16']`
- Assistant target: `Participant B (a wanderer)`

#### Prompt

```text
Conversation so far:
Participant B (a wanderer): Clearly, sir, it is purified. It has reached the peak and the pith.
Participant A (The Buddha): No, Nigrodha, at this point the fervent mortification in disgust of sin has not yet reached the peak and the pith. Rather, it has only reached the bark.
Participant B (a wanderer): But at what point, sir, does the fervent mortification in disgust of sin reach the peak and the pith? Please help me reach the peak and the pith!
Participant A (The Buddha): Nigrodha, take a mortifier who is restrained in the fourfold constraint. They give up these five hindrances, corruptions of the heart that weaken wisdom. Then they meditate spreading a heart full of love... compassion... rejoicing... equanimity. They recollect many kinds of past lives, that is, one, two, three, four, five, ten, twenty, thirty, forty, fifty, a hundred, a thousand, a hundred thousand rebirths; many eons of the world contracting, many eons of the world expanding, many eons of the world contracting and expanding. They remember: 'There, I was named this, my clan was that, I looked like this, and that was my food. This was how I felt pleasure and pain, and that was how my life ended. When I passed away from that place I was reborn somewhere else. There, too, I was named this, my clan was that, I looked like this, and that was my food. This was how I felt pleasure and pain, and that was how my life ended. When I passed away from that place I was reborn here.' And so they recollect their many kinds of past lives, with features and details. What do you think, Nigrodha? If this is so, is the fervent mortification in disgust of sin purified or not?

Write Participant B's next reply.
```

#### Assistant Target

```text
Clearly, sir, it is purified. It has reached the peak and the pith.
```
