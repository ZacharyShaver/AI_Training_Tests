# `parse_majjhima_nikaya.py` Set 05 Random Review

Sampled rows: `10`
Source dataset: `review_outputs/parser_reviews/parse_majjhima_nikaya/set_05/majjhima_nikaya_dialogue_set_05.jsonl`

## Review Policy Summary

- Approve: `9`
- Approve with warning: `1`
- Reject: `0`

## Review Example 1: Majjhima Nikaya

- Record ID: `mn87-html:majjhima_nikaya_next_reply_87_18:231-240:princess-vajir`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN87.html:231-240`
- Target: `Participant B (Princess Vajirī)`
- Target words: `41`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (Princess Vajirī): Now what do you think, great king? Is the noble Queen Vāsabhā dear to you?.… Is [your son] General Viḍūḍabha dear to you?.… Am I dear to you?
Participant A (Queen Vāsabhā): Yes, Mallikā, you are dear to me.
Participant B (Princess Vajirī): And what do you think? Would sorrow, lamentation, pain, distress, & despair arise in you from any change & aberration in me?
Participant A (Queen Vāsabhā): Mallikā, any change & aberration in you would mean an aberration of my very life. How could sorrow, lamentation, pain, distress, & despair not arise in me?
Participant B (Princess Vajirī): Now what do you think, great king? Are [your subjects] the Kāsis & Kosalans dear to you?
Participant A (Queen Vāsabhā): Yes, Mallikā, the Kāsis & Kosalans are dear to me. It's through the might of the Kāsis & Kosalans that we use Kāsi sandalwood and wear garlands, scents, & ointments.
Participant B (Princess Vajirī): And what do you think? Would sorrow, lamentation, pain, distress, & despair arise in you from any change & aberration in the Kāsis & Kosalans?
Participant A (Queen Vāsabhā): Mallikā, any change & aberration in the Kāsis & Kosalans would mean an aberration of my very life. How could sorrow, lamentation, pain, distress, & despair not arise in me?

Write Participant B's next reply.
```

### Assistant Target

```text
Great king, it was in connection with this that the Blessed One-the One who knows, the One who sees, worthy & rightly self-awakened-said, 'Sorrow, lamentation, pain, distress, & despair are born from one who is dear, come springing from one who is dear.'
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 2: Majjhima Nikaya

- Record ID: `mn21-html:majjhima_nikaya_next_reply_21_2:203-205:the-buddha`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN21.html:203-205`
- Target: `Participant B (The Buddha)`
- Target words: `87`
- Reviewer status: `Approve with warning`

### User Prompt

```text
Conversation so far:
Participant B (The Buddha): Come, monk. In my name, call Moliya Phagguna, saying, 'The Teacher calls you, friend Moliya Phagguna.'
Participant A (Moliya Phagguna): The Teacher calls you, friend Moliya Phagguna.

Write Participant B's next reply.
```

### Assistant Target

```text
Is it true, Phagguna that you are spending too much time entangled with the nuns? That this is how much you are spending time entangled with the nuns: If any monk speaks in dispraise of the nuns in your presence, you are angered, displeased, and make an issue of it? And if any monk speaks in dispraise of you in the presence of the nuns, they are angered, displeased, and make an issue of it? Is that how much you are spending time entangled with the nuns?
```

### Review Notes

- Summary: `minimal context`
- Warnings:
  - minimal context

## Review Example 3: Majjhima Nikaya

- Record ID: `mn75-html:majjhima_nikaya_next_reply_75_28:236-258:m-ga-iya`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN75.html:236-258`
- Target: `Participant B (Māgaṇḍiya)`
- Target words: `55`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (Māgaṇḍiya): No, Master Gotama. Why is that? Because when there is disease, there is a use for medicine. But when there is no disease, there is no use for medicine.
Participant A (The Buddha): Māgaṇḍiya, suppose that there was a leper covered with sores & infections, chewed up by worms, picking the scabs off the openings of his wounds with his nails, cauterizing his body over a pit of glowing embers. His friends, companions, & relatives would take him to a doctor. The doctor would concoct medicine for him, and thanks to the medicine he would be cured of his leprosy: well & happy, free, master of himself, going wherever he liked. Then suppose two strong men, having seized hold of him by both arms, were to drag him to a pit of glowing embers. What do you think? Wouldn't he twist his body this way & that?
Participant B (Māgaṇḍiya): Yes, Master Gotama. Why is that? Because the fire is painful to the touch, very hot & scorching.
Participant A (The Buddha): But what do you think, Māgaṇḍiya? Is the fire painful to the touch, very hot & scorching, only now, or was it also that way before?
Participant B (Māgaṇḍiya): Both now & before is it painful to the touch, very hot & scorching, Master Gotama. It's just that when the man was a leper covered with sores & infections, chewed up by worms, picking the scabs off the openings of his wounds with his nai...
```

### Assistant Target

```text
It's amazing, Master Gotama. It's astounding, how this, too, is well-stated by Master Gotama: 'Freedom from disease: the foremost good fortune. Unbinding: the foremost ease.' We have also heard this said by earlier wanderers in the lineage of our teachers: 'Freedom from disease: the foremost good fortune. Unbinding: the foremost ease.' This agrees with that.
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 4: Majjhima Nikaya

- Record ID: `mn64-html:majjhima_nikaya_next_reply_64_3:204-207:the-buddha`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN64.html:204-207`
- Target: `Participant B (The Buddha)`
- Target words: `221`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant A (Māluṅkyaputta): Lord, I remember the five lower fetters as taught by the Blessed One.
Participant B (The Buddha): And how, Māluṅkyaputta, do you remember the five lower fetters as taught by me?
Participant A (Māluṅkyaputta): Lord, I remember self-identification view as a lower fetter taught by the Blessed One. I remember uncertainty as a lower fetter taught by the Blessed One. I remember grasping at habits & practices as a lower fetter taught by the Blessed One. I remember sensual desire as a lower fetter taught by the Blessed One. I remember ill will as a lower fetter taught by the Blessed One. That's how I remember the five lower fetters as taught by the Blessed One.

Write Participant B's next reply.
```

### Assistant Target

```text
And to whom, Māluṅkyaputta, do you remember my having taught the five lower fetters in that way? Wouldn't the wanderers of other sects make a rebuttal with the simile of the youngster? For even the thought 'self-identification' doesn't occur to a stupid baby boy lying on its back, so from where would self-identification view arise in it, even though a latent tendency to self-identification view lies latent within it? Even the thought 'dhammas' doesn't occur to a stupid baby boy lying on its back, so from where would uncertainty about dhammas arise in it, even though a latent tendency to uncertainty lies latent within it? Even the thought 'habits' doesn't occur to a stupid baby boy lying on its back, so from where would grasping at habits & practices arise in it, even though a latent tendency to grasping at habits & practices lies latent within it? Even the thought 'sensuality' doesn't occur to a stupid baby boy lying on its back, so from where would sensual desire for sensuality arise in it, even though a latent tendency to sensual passion lies latent within it? Even the thought 'beings' doesn't occur to a stupid baby boy lying on its back, so from where would ill will for beings arise in it, even though a latent tendency to ill will lies latent within it?
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 5: Majjhima Nikaya

- Record ID: `mn75-html:majjhima_nikaya_next_reply_75_31:246-262:the-buddha`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN75.html:246-262`
- Target: `Participant B (The Buddha)`
- Target words: `21`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (The Buddha): Now what do you think, Māgaṇḍiya? Have you ever seen or heard of a king or king's minister-enjoying himself, provided & endowed with the five strings of sensuality, without abandoning sensual craving, without removing sensual fever-who has dwelt or will dwell or is dwelling free from thirst, his mind inwardly at peace?
Participant A (Māgaṇḍiya): No, Master Gotama.
Participant B (The Buddha): Very good, Māgaṇḍiya. Neither have I ever seen or heard of a king or king's minister-enjoying himself, provided & endowed with the five strings of sensuality, without abandoning sensual craving, without removing sensual fever-who has dwelt or will dwell or is dwelling free from thirst, his mind inwardly at peace. But whatever contemplatives or brahmans who have dwelt or will dwell or are dwelling free from thirst, their minds inwardly at peace, all have done so having realized-as it has come to be-the origination, the disappearance, the allure, the drawbacks, & the escape from sensuality, having abandoned sensual craving and removed sensual fever.
Participant A (Māgaṇḍiya): It's amazing, Master Gotama. It's astounding, how this, too, is well-stated by Master Gotama: 'Freedom from disease: the foremost good fortune. Unbinding: the foremost ease.' We have also heard this said by earlier wanderers in the lineage of our teachers: 'Freedom from...
```

### Assistant Target

```text
Of course, he did it not knowing & not seeing, Master Gotama, but out of faith in the man with good eyesight.
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 6: Majjhima Nikaya

- Record ID: `mn38-html:majjhima_nikaya_next_reply_38_24:385-401:s-ti`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN38.html:385-401`
- Target: `Participant B (Sāti)`
- Target words: `23`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (Sāti): From the doubt-'Has this come to be?'-does uncertainty arise?
Participant A (The Buddha): From the doubt-'Does it come into play from that nutriment?'-does uncertainty arise?
Participant B (Sāti): From the doubt-'From the cessation of that nutriment, is what has come to be subject to cessation?'-does uncertainty arise?
Participant A (The Buddha): Monks, for one who sees with right discernment, as it has come to be, that 'This has come to be,' is that uncertainty abandoned?
Participant B (Sāti): For one who sees with right discernment, as it has come to be, that 'It comes into play from that nutriment,' is that uncertainty abandoned?
Participant A (The Buddha): For one who sees with right discernment, as it has come to be, that 'From the cessation of that nutriment, what has come to be is subject to cessation,' is that uncertainty abandoned?
Participant B (Sāti): Monks, are you thus free from uncertainty here that 'This has come to be'?
Participant A (The Buddha): Are you thus free from uncertainty here that 'It comes into play from that nutriment'?

Write Participant B's next reply.
```

### Assistant Target

```text
Are you thus free from uncertainty here that 'From the cessation of that nutriment, what has come to be is subject to cessation'?
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 7: Majjhima Nikaya

- Record ID: `mn75-html:majjhima_nikaya_next_reply_75_25:231-246:the-buddha`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN75.html:231-246`
- Target: `Participant B (The Buddha)`
- Target words: `51`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant A (Māgaṇḍiya): No, Master Gotama. Why is that? Because heavenly sensualities are more excellent than human sensualities, and more sublime.
Participant B (The Buddha): Māgaṇḍiya, suppose that there was a leper covered with sores & infections, chewed up by worms, picking the scabs off the openings of his wounds with his nails, cauterizing his body over a pit of glowing embers. His friends, companions, & relatives would take him to a doctor. The doctor would concoct medicine for him, and thanks to the medicine he would be cured of his leprosy: well & happy, free, master of himself, going wherever he liked. He would see another leper covered with sores & infections, chewed up by worms, picking the scabs off the openings of his wounds with his nails, cauterizing his body over a pit of glowing embers. What do you think, Māgaṇḍiya? Would that man envy that leper's pit of glowing embers or his partaking of medicine?
Participant A (Māgaṇḍiya): No, Master Gotama. Why is that? Because when there is disease, there is a use for medicine. But when there is no disease, there is no use for medicine.
Participant B (The Buddha): Māgaṇḍiya, suppose that there was a leper covered with sores & infections, chewed up by worms, picking the scabs off the openings of his wounds with his nails, cauterizing his body over a pit of glowing embers. His friends, companions,...
```

### Assistant Target

```text
Now what do you think, Māgaṇḍiya? Have you ever seen or heard of a king or king's minister-enjoying himself, provided & endowed with the five strings of sensuality, without abandoning sensual craving, without removing sensual fever-who has dwelt or will dwell or is dwelling free from thirst, his mind inwardly at peace?
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 8: Majjhima Nikaya

- Record ID: `mn93-html:majjhima_nikaya_next_reply_93_25:221-229:assal-yana`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN93.html:221-229`
- Target: `Participant B (Assalāyana)`
- Target words: `247`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (Assalāyana): What do you think, Assalāyana? Is it only a brahman who is capable of developing in any direction a heart of good will-free from animosity, free from ill will-and not a noble warrior, not a merchant, not a worker?
Participant A (The Buddha): No, Master Gotama. Even a noble warrior.… Even a brahman.… Even a merchant.… Even a worker.… (Members of) all four castes are capable of developing in any direction a heart of good will-free from animosity, free from ill will.
Participant B (Assalāyana): So what strength is there, Assalāyana, what assurance, when the brahmans say, 'Brahmans are the superior caste… the sons & offspring of Brahmā: born of his mouth, born of Brahmā, created by Brahmā, heirs of Brahmā'?
Participant A (The Buddha): Even though Master Gotama says that, still the brahmans think, 'Brahmans are the superior caste… the sons & offspring of Brahmā: born of his mouth, born of Brahmā, created by Brahmā, heirs of Brahmā.'
Participant B (Assalāyana): What do you think, Assalāyana? Is it only a brahman who is capable of taking a loofah & bath powder, going to a river, and scrubbing off dust & dirt, and not a noble warrior, not a merchant, not a worker?
Participant A (The Buddha): No, Master Gotama. Even a noble warrior.… Even a brahman.… Even a merchant.… Even a worker.… (Members of) all four castes are capable of taking a...
```

### Assistant Target

```text
What do you think, Assalāyana? There is the case where a consecrated noble warrior king might call together 100 men of different births (and say to them), 'Come, masters. Those of you there born from a noble warrior clan, from a brahman clan, or from a royal clan: taking an upper fire-stick of Sal wood, salaḷa wood, sandalwood, or padumaka wood, produce fire & make heat appear. And come, masters. Those of you there born from an outcast clan, a trapper clan, a wicker workers' clan, a cartwrights' clan, or a scavengers' clan: taking an upper fire-stick from a dog's drinking trough, from a pig's trough, from a dustbin, or of castor-oil wood, produce fire & make heat appear.' What do you think, Assalāyana? Would the fire made by those born from a noble warrior clan, a brahman clan, or a royal clan-who had produced fire & made heat appear by taking an upper fire-stick of Sal wood, salaḷa wood, sandalwood, or padumaka wood-be the only one with flame, color, & radiance, able to do whatever a fire might be needed to do? And would the fire made by those born from an outcast clan, a trapper clan, a wicker workers' clan, a cartwrights' clan, or a scavengers' clan-who had produced fire & made heat appear by taking an upper fire-stick from a dog's drinking trough, from a pig's trough, from a dustbin, or of castor-oil wood-be without flame, color, & radiance, unable to do what a fire migh...
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 9: Majjhima Nikaya

- Record ID: `mn75-html:majjhima_nikaya_next_reply_75_32:247-278:m-ga-iya`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN75.html:247-278`
- Target: `Participant B (Māgaṇḍiya)`
- Target words: `63`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (Māgaṇḍiya): No, Master Gotama.
Participant A (The Buddha): Very good, Māgaṇḍiya. Neither have I ever seen or heard of a king or king's minister-enjoying himself, provided & endowed with the five strings of sensuality, without abandoning sensual craving, without removing sensual fever-who has dwelt or will dwell or is dwelling free from thirst, his mind inwardly at peace. But whatever contemplatives or brahmans who have dwelt or will dwell or are dwelling free from thirst, their minds inwardly at peace, all have done so having realized-as it has come to be-the origination, the disappearance, the allure, the drawbacks, & the escape from sensuality, having abandoned sensual craving and removed sensual fever.
Participant B (Māgaṇḍiya): It's amazing, Master Gotama. It's astounding, how this, too, is well-stated by Master Gotama: 'Freedom from disease: the foremost good fortune. Unbinding: the foremost ease.' We have also heard this said by earlier wanderers in the lineage of our teachers: 'Freedom from disease: the foremost good fortune. Unbinding: the foremost ease.' This agrees with that.
Participant A (The Buddha): But as for what you have heard said by earlier wanderers in the lineage of your teachers, Māgaṇḍiya-'Freedom from disease: the foremost good fortune. Unbinding: the foremost ease'-which freedom from disease is that, which unbindin...
```

### Assistant Target

```text
This body, Māgaṇḍiya, is a disease, a cancer, an arrow, painful, an affliction. And yet you say, with reference to this body which is a disease, a cancer, an arrow, painful, an affliction: 'This is that freedom from disease, Master Gotama. This is that unbinding,' for you don't have the noble vision with which you would know freedom from disease and see unbinding.
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 10: Majjhima Nikaya

- Record ID: `mn22-html:majjhima_nikaya_next_reply_22_9:308-344:the-buddha`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN22.html:308-344`
- Target: `Participant B (The Buddha)`
- Target words: `129`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (The Buddha): Worthless man, you will be recognized for your own evil viewpoint. I will cross-examine the monks on this matter.
Participant B (The Buddha): Monks, do you, too, understand the Dhamma as taught by me in the same way that the monk Ariṭṭha Formerly-of-the-Vulture-Killers does when, through his own wrong grasp, he both slanders us as well as injuring himself and accumulating much demerit for himself?
Participant B (The Buddha): Suppose a man were traveling along a path. He would see a great expanse of water, with the near shore dubious & risky, the further shore secure & free from risk, but with neither a ferryboat nor a bridge going from this shore to the other. The thought would occur to him, 'Here is this great expanse of water, with the near shore dubious & risky, the further shore secure & free from risk, but with neither a ferryboat nor a bridge going from this shore to the other. What if I were to gather grass, twigs, branches, & leaves and, having bound them together to make a raft, were to cross over to safety on the other shore in dependence on the raft, making an effort with my hands & feet?' Then the man, having gathered grass, twigs, branches, & leaves, having bound them together to make a raft, would cross over to safety on the other shore in dependence on the raft, making an effort with his hands & feet. Having cro...
```

### Assistant Target

```text
There is the case where someone has this view: 'This cosmos is the self. After death this I will be constant, permanent, eternal, not subject to change. I will stay just like that for an eternity.' He hears a Tathāgata or a Tathāgata's disciple teaching the Dhamma for the elimination of all view-positions, determinations, biases, inclinations, & obsessions; for the pacification of all fabrications; for the relinquishing of all acquisitions; the ending of craving; dispassion; cessation; unbinding. The thought occurs to him, 'So it might be that I will be annihilated! So it might be that I will perish! So it might be that I will not exist!' He grieves & is tormented, weeps, beats his breast, & grows delirious. It's thus that there is agitation over what is internally not present.
```

### Review Notes

- Summary: `clean structural pass`
