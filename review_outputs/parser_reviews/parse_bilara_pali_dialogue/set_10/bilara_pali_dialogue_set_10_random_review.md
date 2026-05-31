# Random Sample Review Packet

Source JSONL: `review_outputs/parser_reviews/parse_bilara_pali_dialogue/set_10/bilara_pali_dialogue_set_10.jsonl`
Rows: `10`

## Reviewer Criteria

- Prompt and reply preserve source continuity.
- Speaker labels are coherent and not malformed.
- Assistant target is the next reply only.
- No page headers, footnotes, OCR bleed, or commentary contamination.

## Rows

### Row 1

- Record ID: `dn2:bilara_dialogue_32:0-0:the-buddha`
- Source: `Digha Nikaya`
- Source file: `bilara:dn2`
- Source lines: `['dn2:101.3', 'dn2:101.3']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant A (King Ajātasattu): Excellent, sir! Excellent! As if he were righting the overturned, or revealing the hidden, or pointing out the path to the lost, or lighting a lamp in the dark so people with clear eyes can see what's there, the Buddha has made the teaching clear in many ways. I go for refuge to the Buddha, to the teaching, and to the mendicant Saṅgha. From this day forth, may the Buddha remember me as a lay follower who has gone for refuge for life. I made a mistake, sir. It was foolish, stupid, and unskillful of me to take the life of my father, a just and principled king, for the sake of authority. Please, sir, accept my mistake for what it is, so I will restrain myself in future.
Participant B (The Buddha): Indeed, great king, you made a mistake. It was foolish, stupid, and unskillful of you to take the life of your father, a just and principled king, for the sake of sovereignty. But since you have recognized your mistake for what it is, and have dealt with it properly, I accept it. For it is growth in the training of the Noble One to recognize a mistake for what it is, deal with it properly, and commit to restraint in the future.
Participant A (King Ajātasattu): Well, now, sir, I must go. I have many duties, and much to do.

Write Participant B's next reply.
```

#### Assistant Target

```text
Please, great king, go at your convenience.
```

### Row 2

- Record ID: `sn7-21:bilara_dialogue_3:0-0:the-buddha`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn7.21`
- Source lines: `['sn7.21:2.6', 'sn7.21:2.6']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant A (the brahmin Saṅgārava): Sir, there is a brahmin named Saṅgārava staying in Sāvatthī. He practices purification by water, believing in purification by water. He lives devoted to ritual bathing at daybreak and dusk. Please visit him at his home out of sympathy.
Participant B (The Buddha): Is it really true, brahmin, that you practice purification by water, believing in purification by water; that you live committed to the practice of immersing yourself in water at daybreak and dusk?
Participant A (the brahmin Saṅgārava): Yes, worthy Gotama.

Write Participant B's next reply.
```

#### Assistant Target

```text
But brahmin, for what reason do you practice purification by water?
```

### Row 3

- Record ID: `sn4-7:bilara_dialogue_1:0-0:the-buddha`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn4.7`
- Source lines: `['sn4.7:3.1', 'sn4.7:3.4']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant A (Māra the Wicked): What, you're asleep? Really, you're asleep? You sleep like a loser-what's up with that? You sleep, thinking that the hut is empty. You sleep when the sun has come up-what's up with that?

Write Participant B's next reply.
```

#### Assistant Target

```text
For them there is no cravingthe weaver, the clinger-to track them anywhere. With the ending of all attachments the awakened Buddha sleeps. What's that got to do with you, Māra?
```

### Row 4

- Record ID: `dn4:bilara_dialogue_30:0-0:so-ada-a`
- Source: `Digha Nikaya`
- Source file: `bilara:dn4`
- Source lines: `['dn4:24.2', 'dn4:24.6']`
- Assistant target: `Participant B (Soṇadaṇḍa)`

#### Prompt

```text
Conversation so far:
Participant B (Soṇadaṇḍa): That's all I know about this matter, worthy Gotama. May the worthy Gotama himself please clarify the meaning of this.
Participant A (The Buddha): Well then, brahmin, listen and apply your mind well, I will speak.
Participant B (Soṇadaṇḍa): Yes, worthy sir,
Participant A (The Buddha): It's when a Realized One arises in the world, perfected, a fully awakened Buddha... That's how a mendicant is accomplished in ethics. This, brahmin, is that ethical conduct.... They enter and remain in the first absorption... second absorption... third absorption... fourth absorption... They project and extend the mind toward knowledge and vision... This pertains to their wisdom.... They understand: '... there is nothing further for this place.' This pertains to their wisdom. This, brahmin, is that wisdom.

Write Participant B's next reply.
```

#### Assistant Target

```text
Excellent, worthy Gotama! Excellent! As if he were righting the overturned, or revealing the hidden, or pointing out the path to the lost, or lighting a lamp in the dark so people with clear eyes can see what's there, worthy Gotama has made the Teaching clear in many ways. I go for refuge to the worthy Gotama, to the teaching, and to the mendicant Saṅgha. From this day forth, may the worthy Gotama remember me as a lay follower who has gone for refuge for life. Would you and the mendicant Saṅgha please accept tomorrow's meal from me?
```

### Row 5

- Record ID: `sn8-7:bilara_dialogue_3:0-0:venerable-s-riputta`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn8.7`
- Source lines: `['sn8.7:4.1', 'sn8.7:4.2']`
- Assistant target: `Participant B (Venerable Sāriputta)`

#### Prompt

```text
Conversation so far:
Participant A (The Buddha): Come now, monks, I invite you all: Is there anything I've done by way of body or speech that you would criticize?
Participant B (Venerable Sāriputta): There is nothing, sir, that you've done by way of body or speech that we would criticize. For the Blessed One gave rise to the unarisen path, gave birth to the unborn path, and explained the unexplained path. He is the knower of the path, the discoverer of the path, the expert on the path. And now the disciples live following the path; they acquire it later. And sir, I invite the Blessed One. Is there anything I've done by way of body or speech that you would criticize?
Participant A (The Buddha): There is nothing, Sāriputta, that you've done by way of body or speech that I would criticize. Sāriputta, you are astute. You have great wisdom, widespread wisdom, laughing wisdom, swift wisdom, sharp wisdom, penetrating wisdom. A wheel-turning monarch's oldest son rightly keeps wielding the power set in motion by his father. In the same way, Sāriputta rightly keeps rolling the supreme Wheel of Dhamma that was rolled forth by me.

Write Participant B's next reply.
```

#### Assistant Target

```text
Since it seems I have done nothing worthy of the Blessed One's criticism, is there anything these five hundred monks have done by way of body or speech that you would criticize?
```

### Row 6

- Record ID: `sn2-28:bilara_dialogue_1:0-0:the-buddha`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn2.28`
- Source lines: `['sn2.28:3.1', 'sn2.28:3.4']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant A (Nandivisāla): Four are its wheels, and nine its doors; it's stuffed full, bound with greed, and born from a bog. Great hero, how will I keep going?

Write Participant B's next reply.
```

#### Assistant Target

```text
Having cut the strap and harnesswicked desire and greedand having plucked out craving, root and all: that's how you will keep going.
```

### Row 7

- Record ID: `dn27:bilara_dialogue_4:0-0:the-buddha`
- Source: `Digha Nikaya`
- Source file: `bilara:dn27`
- Source lines: `['dn27:4.1', 'dn27:5.0']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant B (The Buddha): Vāseṭṭha, you are both brahmins by birth and family, and have gone forth from the lay life to homelessness from a brahmin family. I hope you don't have to suffer abuse and insults from the brahmins.
Participant A (Vāseṭṭha): Actually, sir, the brahmins do insult and abuse us with their typical insults to the fullest extent, holding nothing back.
Participant B (The Buddha): But how do the brahmins insult you?
Participant A (Vāseṭṭha): Sir, the brahmins say: 'Only brahmins are the best class; other classes are inferior. Only brahmins are the light class; other classes are dark. Only brahmins are purified, not others. Only brahmins are the Divinity's true-born sons, born from his mouth, born of the Divinity, created by the Divinity, heirs of the Divinity. You've both abandoned the best class to join an inferior class, namely these shavelings, fake ascetics, primitives, black spawn from the feet of our kinsman. This is not right, it's not proper!' That's how the brahmins insult us.

Write Participant B's next reply.
```

#### Assistant Target

```text
Actually, Vāseṭṭha, the brahmins are forgetting their tradition when they say this to you. For brahmin women are seen menstruating, being pregnant, giving birth, and breast-feeding. Yet even though they're born from a brahmin womb they say: 'Only brahmins are the best class; other classes are inferior. Only brahmins are the light class; other classes are dark. Only brahmins are purified, not others. Only brahmins are the Divinity's true-born sons, born from his mouth, born of the Divinity, created by the Divinity, heirs of the Divinity.' They misrepresent the brahmins, speak falsely, and brim with much wickedness.
```

### Row 8

- Record ID: `sn2-26:bilara_dialogue_2:0-0:rohitassa`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn2.26`
- Source lines: `['sn2.26:2.1', 'sn2.26:4.3']`
- Assistant target: `Participant B (Rohitassa)`

#### Prompt

```text
Conversation so far:
Participant B (Rohitassa): Sir, is it possible to know or see or reach the end of the world by traveling to a place where there's no being born, growing old, dying, passing away, or being reborn?
Participant A (The Buddha): Reverend, I say it's not possible to know or see or reach the end of the world by traveling to a place where there's no being born, growing old, dying, passing away, or being reborn.

Write Participant B's next reply.
```

#### Assistant Target

```text
It's incredible, sir, it's amazing, how well said this was by the Buddha. Once upon a time, I was a seer called Rohitassa, son of the benefactors. I was a sky-walker with psychic powers. I was as fast as a light arrow easily shot across the shadow of a palm tree by a well-trained expert archer with a strong bow. My stride was such that it could span from the eastern ocean to the western ocean. This wish came to me: 'I will reach the end of the world by traveling.' Having such speed and stride, I traveled for my whole lifespan of a hundred years-pausing only to eat and drink, go to the toilet, and sleep to dispel weariness-and I passed away along the way, never reaching the end of the world. It's incredible, sir, it's amazing, how well said this was by the Buddha. 'Reverend, I say it's not possible to know or see or reach the end of the world by traveling to a place where there's no being born, growing old, dying, passing away, or being reborn.'
```

### Row 9

- Record ID: `sn1-33:bilara_dialogue_1:0-0:the-buddha`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn1.33`
- Source lines: `['sn1.33:18.1', 'sn1.33:19.4']`
- Assistant target: `Participant B (The Buddha)`

#### Prompt

```text
Conversation so far:
Participant A (a deity): Sir, who has spoken well?

Write Participant B's next reply.
```

#### Assistant Target

```text
You've all spoken well in your own way. However, listen to me also: A gift of faith is praised in many ways, but a passage of teaching is better than giving, for the virtuous, in days old and older still, even attained extinction with wisdom.
```

### Row 10

- Record ID: `sn2-24:bilara_dialogue_4:0-0:gha-k-ra`
- Source: `Samyutta Nikaya Sagathavagga`
- Source file: `bilara:sn2.24`
- Source lines: `['sn2.24:6.1', 'sn2.24:7.4']`
- Assistant target: `Participant B (Ghaṭīkāra)`

#### Prompt

```text
Conversation so far:
Participant B (Ghaṭīkāra): Seven mendicants reborn in Aviha have been freed. With the complete ending of greed and hate, they've crossed over clinging to the world.
Participant A (The Buddha): Who are those who've crossed the bog, Death's dominion so hard to pass? Who, after leaving behind the human body, have risen above celestial yokes?
Participant B (Ghaṭīkāra): Upaka and Palagaṇḍa, and Pukkusāti, these three; Bhaddiya and Bhaddadeva, and Bāhudantī and Piṅgiya. They, after leaving behind the human body, have risen above celestial yokes.
Participant A (The Buddha): You speak well of them, who have let go the snares of Māra. Whose teaching did they understand to cut the bonds of rebirth?

Write Participant B's next reply.
```

#### Assistant Target

```text
None other than the Blessed One! None other than your instruction! It was your teaching that they understood to cut the bonds of rebirth. Where name and form cease with no residue left behind; understanding this teaching, they cut the bonds of rebirth.
```
