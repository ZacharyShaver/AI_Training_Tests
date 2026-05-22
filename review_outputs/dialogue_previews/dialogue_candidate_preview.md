# Dialogue Extraction Preview

This is a small review sample. Explicit examples are close to training
records. Speech-cue candidates still need parser review before they are
trusted as training examples.

## Body Line Ranges

- `the_key-to-theosophy.txt`: `104-3061`
- `The Corpus Hermeticum.txt`: `70-2446`
- `Milinda Panha.txt`: `927-8158`
- `Platform Sutra .txt`: `532-2838`
- `Asclepius.txt`: `1230-3285`

## Example 1: The Key to Theosophy

- Kind: `explicit_next_reply`
- Lines: `the_key-to-theosophy.txt:104-107`
- Target: `Participant B (Theosophist)`
- Target words: `68`

### User Prompt

```text
Conversation so far:
Participant A (Enquirer): Theosophy and its doctrines are often referred to as a new-fangled religion. Is it a religion?
Participant B (Theosophist): It is not. Theosophy is Divine Knowledge or Science.
Participant A (Enquirer): What is the real meaning of the term?

Write Participant B's next reply.
```

### Assistant Target

```text
"Divine Wisdom," (Theosophia) or Wisdom of the gods, as (theogonia), genealogy of the gods. The word theos means a god in Greek, one of the divine beings, certainly not "God" in the sense attached in our day to the term. Therefore, it is not "Wisdom of God," as translated by some, but Divine Wisdom such as that possessed by the gods. The term is many thousand years old.
```

## Example 2: The Key to Theosophy

- Kind: `explicit_next_reply`
- Lines: `the_key-to-theosophy.txt:960-966`
- Target: `Participant B (Theosophist)`
- Target words: `196`

### User Prompt

```text
Conversation so far:
Participant A (Enquirer): Is that on account of the great distance?
Participant B (Theosophist): Not at all, for we see with our naked eye planets and even stars at immeasurably greater distances; but it is owing to those six globes being outside our physical means of perception, or plane of being. It is not only that their material density, weight, or fabric are entirely different from those of our earth and the other known planets; but they are (to us) on an entirely different layer of space, so to speak; a layer not to be perceived or felt by our physical senses. And when I say "layer," please do not allow your fancy to suggest to you layers like strata or beds laid one over the other, for this would only lead to another absurd misconception. What I mean by "layer" is that plane of infinite space which by its nature cannot fall under our ordinary waking percept...
```

### Assistant Target

```text
None; except, perhaps, that which for Science would be rather a handy peg on which to hang a counter-argument. We have a different set of senses in dream- life, have we not? We feel, talk, hear, see, taste and function in general on a different plane; the change of state of our consciousness being evidenced by the fact that a series of acts and events embracing years, as we think, pass ideally through our mind in one instant. Well, that extreme rapidity of our mental operations in dreams, and the perfect naturalness, for the time being, of all the other functions, show us that we are on quite another plane. Our philosophy teaches us that, as there are seven fundamental forces in nature, and seven planes of being, so there are seven states of consciousness in which man can live, think, remember and have his being. To enumerate these here is impossible, and for this one has to turn to t...
```

## Example 3: The Key to Theosophy

- Kind: `explicit_next_reply`
- Lines: `the_key-to-theosophy.txt:1953-1956`
- Target: `Participant B (Theosophist)`
- Target words: `193`

### User Prompt

```text
Conversation so far:
Participant A (Enquirer): And what is it that regulates the duration, or special qualities of these incarnations?
Participant B (Theosophist): Karma, the universal law of retributive justice.
Participant A (Enquirer): Is it an intelligent law?

Write Participant B's next reply.
```

### Assistant Target

```text
For the Materialist, who calls the law of periodicity which regulates the marshalling of the several bodies, and all the other laws in nature, blind forces and mechanical laws, no doubt Karma would be a law of chance and no more. For us, no adjective or qualification could describe that which is impersonal and no entity, but a universal operative law. If you question me about the causative intelligence in it, I must answer you I do not know. But if you ask me to define its effects and tell you what these are in our belief, I may say that the experience of thousands of ages has shown us that they are absolute and unerring equity, wisdom, and intelligence. For Karma in its effects is an unfailing redresser of human injustice, and of all the failures of nature; a stern adjuster of wrongs; a retributive law which rewards and punishes with equal impartiality. It is, in the strictest sense,...
```

## Example 4: The Key to Theosophy

- Kind: `explicit_next_reply`
- Lines: `the_key-to-theosophy.txt:2571-2577`
- Target: `Participant B (Theosophist)`
- Target words: `26`

### User Prompt

```text
Conversation so far:
Participant A (Enquirer): I have heard people say that your rules require all members to be vegetarians, celibates, and rigid ascetics; but you have not told me anything of the sort yet. Can you tell me the truth once for all about this?
Participant B (Theosophist): The truth is that our rules require nothing of the kind. The Theosophical Society does not even expect, far less require of any of its members that they should be ascetics in any way, except - if you call that asceticism - that they should try and benefit other people and be unselfish in their own lives.
Participant A (Enquirer): But still many of your members are strict vegetarians, and openly avow their intention of remaining unmarried. This, too, is most often the case with those who take a prominent part in connection with the work of your Society.

Write Participant B's next reply.
```

### Assistant Target

```text
That is only natural, because most of our really earnest workers are members of the Inner Section of the Society, which I told you about before.
```

## Example 5: The Key to Theosophy

- Kind: `explicit_next_reply`
- Lines: `the_key-to-theosophy.txt:3041-3050`
- Target: `Participant B (Theosophist)`
- Target words: `119`

### User Prompt

```text
Conversation so far:
Participant A (Enquirer): But if this danger be averted?
Participant B (Theosophist): Then the Society will live on into and through the twentieth century. It will gradually leaven and permeate the great mass of thinking and intelligent people with its large-minded and noble ideas of Religion, Duty, and Philanthropy. Slowly but surely it will burst asunder the iron fetters of creeds and dogmas, of social and caste prejudices; it will break down racial and national antipathies and barriers, and will open the way to the practical realisation of the Brotherhood of all men. Through its teaching, through the philosophy which it has rendered accessible and intelligible to the modern mind, the West will learn to understand and appreciate the East at its true value. Further, the development of the psychic powers and faculties, the premonitory symptoms of which are already...
```

### Assistant Target

```text
Scarcely. But I must tell you that during the last quarter of every hundred years an attempt is made by those "Masters," of whom I have spoken, to help on the spiritual progress of Humanity in a marked and definite way. Towards the close of each century you will invariably find that an outpouring or upheaval of spirituality - or call it mysticism if you prefer - has taken place. Some one or more persons have appeared in the world as their agents, and a greater or less amount of occult knowledge and teaching has been given out. If you care to do so, you can trace these movements back, century by century, as far as our detailed historical records extend.
```

## Example 6: The Corpus Hermeticum

- Kind: `explicit_next_reply`
- Lines: `The Corpus Hermeticum.txt:487-499`
- Target: `Participant B (Hermes)`
- Target words: `87`

### User Prompt

```text
Conversation so far:
Participant A (Asclepius): They move, Thrice-greatest one.
Participant B (Hermes): And what their motion, my Asclepius?
Participant A (Asclepius): Motion that turns for ever round the same.

Write Participant B's next reply.
```

### Assistant Target

```text
But revolution - motion around same - is fixed by rest. For "round-the-same" doth stop "beyond-same". "Beyond-same" then, being stopped, if it be steadied in "round-same" - the contrary stands firm, being rendered ever stable by its contrariety. 8. Of this I'll give thee here on earth an instance, which the eye can see. Regard the animals down here - a man, for instance, swimming! The water moves, yet the resistance of his hands and feet give him stability, so that he is not borne along with it, nor sunk thereby.
```

## Example 7: The Corpus Hermeticum

- Kind: `explicit_next_reply`
- Lines: `The Corpus Hermeticum.txt:552-562`
- Target: `Participant B (Hermes)`
- Target words: `50`

### User Prompt

```text
Conversation so far:
Participant A (Asclepius): Thy argument (logos), Thrice-greatest one, is not to be gainsaid; air is a body. Further, it is this body which doth pervade all things, and so, pervading, fill them. What are we, then, to call that space in which the all doth move?
Participant B (Hermes): The bodiless, Asclepius.
Participant A (Asclepius): What, then, is Bodiless?

Write Participant B's next reply.
```

### Assistant Target

```text
'Tis Mind and Reason (logos), whole out of whole, all self-embracing, free from all body, from all error free, unsensible to body and untouchable, self stayed in self, containing all, preserving those that are, whose rays, to use a likeness, are Good, Truth, Light beyond light, the Archetype of soul.
```

## Example 8: The Corpus Hermeticum

- Kind: `explicit_next_reply`
- Lines: `The Corpus Hermeticum.txt:2131-2151`
- Target: `Participant B (Hermes)`
- Target words: `178`

### User Prompt

```text
Conversation so far:
Participant A (Tat): But these are purely energies, O father mine!
Participant B (Hermes): If, then, they're purely energies, my son - by whom, then, are they energized except by God? Or art thou ignorant, that just as Heaven, Earth, Water, Air, are parts of Cosmos, in just the selfsame way God's parts are Life and Immortality, [and] Energy, and Spirit, and Necessity, and Providence, and Nature, Soul, and Mind, and the Duration of all these that is called Good? And there are naught of things that have become, or are becoming, in which God is not.
Participant A (Tat): Is He in Matter, father, then?

Write Participant B's next reply.
```

### Assistant Target

```text
Matter, my son, is separate from God, in order that thou may'st attribute to it the quality of space. But what thing else than mass think'st thou it is, if it's not energized? Whereas if it be energized, by whom is it made so? For energies, we said, are parts of God. By whom are, then, all lives enlivened? By whom are things immortal made immortal? By whom changed things made changeable? And whether thou dost speak of Matter, of Body, or of Essence, know that these too are energies of God; and that materiality is Matter's energy, that corporeality is Bodies' energy, and that essentiality doth constituteth the energy of Essence; and this is God - the All. 23. And in the All is naught that is not God. Wherefore nor size, nor space, nor quality, nor form, nor time, surroundeth God; for He is All, and All surroundeth all, and permeateth all. Unto this Reason (Logos), son, thy adoration an...
```

## Example 9: The Corpus Hermeticum

- Kind: `explicit_next_reply`
- Lines: `The Corpus Hermeticum.txt:2233-2245`
- Target: `Participant B (Hermes)`
- Target words: `77`

### User Prompt

```text
Conversation so far:
Participant A (Tat): What then is true, Thrice-greatest One?
Participant B (Hermes): That which is never troubled, son, which cannot be defined; that which no color hath, nor any figure, which is not turned, which hath no garment, which giveth light; that which is comprehensible unto itself [alone], which doth not suffer change; that which no body can contain.
Participant A (Tat): In very truth I lose my reason, father. Just when I thought to be made wise by thee, I find the senses of this mind of mine blocked up.

Write Participant B's next reply.
```

### Assistant Target

```text
Thus is it, son: That which is upward borne like fire, yet is borne down like earth, that which is moist like water, yet blows like air, how shalt thou this perceive with sense - the that which is not solid nor yet moist, which naught can bind or loose, of which in power and energy alone can man have any notion - and even then it wants a man who can perceive the Way of Birth in God?
```

## Example 10: The Corpus Hermeticum

- Kind: `explicit_next_reply`
- Lines: `The Corpus Hermeticum.txt:2333-2359`
- Target: `Participant B (Hermes)`
- Target words: `97`

### User Prompt

```text
Conversation so far:
Participant A (Tat): Tell me, O father: This Body which is made up of the Powers, is it at any time dissolved?
Participant B (Hermes): Hush, [son]! Speak not of things impossible, else wilt thou sin and thy Mind's eye be quenched. The natural body which our sense perceives is far removed from this essential birth. The first must be dissolved, the last can never be; the first must die, the last death cannot touch. Dost thou not know thou hast been born a God, Son of the One, even as I myself?
Participant A (Tat): I would, O father, hear the Praise-giving with hymn which thou didst say thou heardest then when thou wert at the Eight [the Ogdoad] of Powers

Write Participant B's next reply.
```

### Assistant Target

```text
Just as the Shepherd did foretell [I should], my son, [when I came to] the Eight. Well dost thou haste to "strike thy tent", for thou hast been made pure. The Shepherd, Mind of all masterhood, hath not passed on to me more than hath been written down, for full well did he know that I should of myself be able to learn all, and hear what I should wish, and see all things. He left to me the making of fair things; wherefore the Powers within me. e'en as they are in all, break into song.
```

## Example 11: Milinda Panha

- Kind: `speech_cue_candidate`
- Lines: `Milinda Panha.txt:1075-1093`
- Cue: `Nāgasena replied`
- Words: `173`

### Candidate Block

```text
Nāgasena. "The three Vedas," replied Soṇut- tara. "Well then, father, I will learn them," said Nāgasena. A brahmin teacher was employed and young Nāgasena memorized the three Vedas after a single repetition. He then asked his father: "Father, is there anything more to be trained in in this brahmin family?" "Dear Nāgasena, there is nothing more to be trained in; this is the full extent." Then, after seri- ous contemplation, Nāgasena concluded: "Empty indeed are these Vedas, void indeed are these Vedas, pithless, without pith." And he was remorseful and displeased. At this time Venerable Rohaṇa was living in the Vattaniya Hermitage. Knowing with his psychic powers the reasoning in the mind of young Nāgasena, Venerable Rohaṇa vanished from the hermitage and appeared in the Kajangala village. Nāgasena saw him approaching from a distance and was pleased and uplifted. He thought: "Perhaps t...
```

## Example 12: Milinda Panha

- Kind: `speech_cue_candidate`
- Lines: `Milinda Panha.txt:2323-2337`
- Cue: `King Milinda said`
- Words: `128`

### Candidate Block

```text
King Milinda said: "Revered Nāgasena, as to this 'long time' you mentioned, what is this time?" "The past time, sire, the future time and the present time." "But does this time exist, revered sir?" "Some time exists, sire, some does not." "But which exists, revered sir, which does not?" "Those formations, sire, that are past, departed, stopped or changed-that time does not exist. Those mental states that are results and those mental states that are liable to have results and those giving rebirth elsewhere-that time exists.47 For those beings who die and arise elsewhere time exists; for those beings who die and do not arise elsewhere time does not exist; for those beings who have attained final Nibbāna time does not exist." "You are dexterous, revered Nāgasena."
```

## Example 13: Milinda Panha

- Kind: `speech_cue_candidate`
- Lines: `Milinda Panha.txt:2867-2879`
- Cue: `King Milinda said`
- Words: `101`

### Candidate Block

```text
King Milinda said: "Revered Nāgasena, does he who does not obtain Nibbāna know that Nibbāna is happiness." "Yes, sire, he does." "But how, revered Nāgasena, does anyone without obtaining Nibbāna know that Nibbāna is happiness?" "What do you think about this, sire? Would those who have not had their hands and feet cut off know that the cutting off of them is suffering?" "Yes, revered sir, they would know." "How would they know?" "They know, revered sir, from having heard the lamentations of those whose hands and feet have been cut off that the cut- ting off of them is suffering."
```

## Example 14: Milinda Panha

- Kind: `speech_cue_candidate`
- Lines: `Milinda Panha.txt:3339-3354`
- Cue: `King Milinda said`
- Words: `117`

### Candidate Block

```text
King Milinda said: "Revered Nāgasena, how many factors of enlightenment are there?" "There are seven factors of enlightenment, sire."66 "By how many factors of enlightenment does one become enlightened, sir?" "By one factor of enlightenment, sire, the factor of investiga- tion of phenomena." "Then why are seven factors mentioned, revered sir?" "What do you think about this, sire? If a sword has been put into a sheath and not taken in the hand, is it able to cut any- thing you wanted to cut with it?" "No, revered sir." "Even so, sire, without the other six factors of enlightenment one does not become enlightened by the factor of investigation of phenomena." "You are dexterous, revered Nāgasena."
```

## Example 15: Milinda Panha

- Kind: `speech_cue_candidate`
- Lines: `Milinda Panha.txt:6487-6500`
- Cue: `King Milinda said`
- Words: `141`

### Candidate Block

```text
King Milinda said: "Revered Nāgasena, you keep on talking about Nibbāna, but is it possible by simile or argument or cause or method to point out the shape or configuration or age or size of this Nibbāna?" "Without a counterpart, sire, is Nibbāna, and it is not possi- ble by simile or argument or cause or method to point out the shape or configuration or age or size of Nibbāna." "But, revered Nāgasena, I do not agree to this not laying down by simile or argument or cause or method the shape or configuration or age or size of Nibbāna, which is a thing that exists. Convince me by a reason." "Let it be, sire, I will convince you of this by a reason. Is there, sire, what is called the great ocean?" "Yes, revered sir, there is this great ocean."
```

## Example 16: Platform Sutra

- Kind: `speech_cue_candidate`
- Lines: `Platform Sutra .txt:568-569`
- Cue: `The patriarch asked`
- Words: `109`

### Candidate Block

```text
The patriarch asked me, 'Where are you from, and what is it you seek?' I replied, 'Your disciple is a commoner from Xinzhou in Lingnan, and I have come this far to pay reverence to you. I wish only to achieve buddhahood and do not seek anything else.' The patriarch said, 'If you're from Lingnan, then you must be a hunter.40 How could you ever achieve buddhahood?' I said, 'Although people may be from north or south, there is fundamentally no north and south in the buddha-nature. Although this hunter's body is dif- ferent from Your Reverence's, how can there be any difference in the buddha- natures [within]?'
```

## Example 17: Platform Sutra

- Kind: `speech_cue_candidate`
- Lines: `Platform Sutra .txt:1532-1534`
- Cue: `The master said`
- Words: `185`

### Candidate Block

```text
The master said, "I do not understand words, but try reciting the sutra for me once and I will explain it for you." Fada then recited the sutra aloud. When he came to the "Chapter on Parables" the master said, "Stop. The central doctrine of this sutra is funda- mentally the causes and conditions and the appearance [of the buddhas] in the world. There can be no parables that surpass this. "What are the causes and conditions? The sutra says, 'The buddhas and World-honored Ones only appear in the world through the causes and con- ditions of the one great affair.' The one great affair is the perceptual under- standing of the buddhas. The people of this world are delusively attached to characteristics externally and delusively attached to emptiness internally. If one is able to transcend characteristics within characteristics and to tran- scend emptiness within emptiness, this is to be und...
```

## Example 18: Platform Sutra

- Kind: `speech_cue_candidate`
- Lines: `Platform Sutra .txt:1893-1894`
- Cue: `A monk asked`
- Words: `31`

### Candidate Block

```text
A monk asked the master, "What type of person attains the doctrine of Huang- mei?" The master said, "Someone who understands the Buddha-Dharma." The monk said, "Has Your Reverence attained it?"
```

## Example 19: Platform Sutra

- Kind: `speech_cue_candidate`
- Lines: `Platform Sutra .txt:2087-2088`
- Cue: `The master said`
- Words: `70`

### Candidate Block

```text
The master said, "Formerly I heard the nun Wujin Zang read through the Nirvana Sutra once, and I explained it for her without so much as a sin- gle character or single doctrine being different from the text of the sutra. And I ultimately have no separate teaching for you." [Xingchang] said, "This student's understanding129 is shallow, and I ask Your Reverence to reveal [the teaching] for me in detail."
```

## Example 20: Platform Sutra

- Kind: `speech_cue_candidate`
- Lines: `Platform Sutra .txt:2830-2830`
- Cue: `The questioner said`
- Words: `34`

### Candidate Block

```text
The questioner acknowledged this, bowed again, and said in gratitude, "I have been feebleminded [in asking this]. Please include [this exchange] at the end of the sutra in order to inform those to come."
```
