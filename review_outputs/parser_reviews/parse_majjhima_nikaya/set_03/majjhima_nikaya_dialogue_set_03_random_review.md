# `parse_majjhima_nikaya.py` Set 03 Random Review

Sampled rows: `10`
Source dataset: `review_outputs/parser_reviews/parse_majjhima_nikaya/set_03/majjhima_nikaya_dialogue_set_03.jsonl`

## Review Policy Summary

- Approve: `8`
- Approve with warning: `2`
- Reject: `0`

## Review Example 1: Majjhima Nikaya

- Record ID: `mn56-html:majjhima_nikaya_next_reply_56_40:261-292:up-li`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN56.html:261-292`
- Target: `Participant B (Upāli)`
- Target words: `36`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant A (The Buddha): What do you think, householder? There might be the case where a Nigaṇṭha is restrained with the fourfold restraint: constrained by all constraints, yoked to all constraints, cleansed by all constraints, attained to all constraints. As he walks back & forth, he brings many small beings to destruction. What (kammic) result would the Nigaṇṭha Nāṭaputta describe for him?
Participant B (Upāli): What is unintended, lord, the Nigaṇṭha Nāṭaputta does not describe as greatly blameworthy.
Participant A (Nigaṇṭha Nāṭaputta): But if he intends it?
Participant B (Upāli): Greatly blameworthy, lord.
Participant B (Upāli): Now, lord, I must go. Many are my duties, many my responsibilities.
Participant A (The Buddha): Then do, householder, what you consider it is now time to do.
Participant B (Upāli): From this day forth, my good gatekeeper, I close the door to male & female Nigaṇṭhas and leave the door unclosed to the Blessed One's monks, nuns, male lay followers, & female lay followers. In case any Nigaṇṭha comes, you are to tell him, 'Stay there, venerable sir. Don't come in. From this day forward, Upāli the householder has entered into discipleship under Gotama the contemplative. The door is closed to male & female Nigaṇṭhas, but not closed to the Blessed One's monks, nuns, male lay followers, & female lay followers. If you have need of al...
```

### Assistant Target

```text
It's impossible, Tapassin, it could not happen, that Upāli the householder would enter into discipleship under Gotama the contemplative. But there is the possibility that Gotama the contemplative would enter into discipleship under Upāli the householder.
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 2: Majjhima Nikaya

- Record ID: `mn93-html:majjhima_nikaya_next_reply_93_33:230-239:assal-yana`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN93.html:230-239`
- Target: `Participant B (Assalāyana)`
- Target words: `52`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant A (The Buddha): No, Master Gotama. The fire made by those born from a noble warrior clan, a brahman clan, or a royal clan… would have flame, color, & radiance, able to do whatever a fire might be needed to do. And the fire made by those born from an outcast clan, a trapper clan, a wicker workers' clan, a cartwrights' clan, or a scavengers' clan… would have flame, color, & radiance, able to do whatever a fire might be needed to do. For all fire has flame, color, & radiance, and is able to do whatever a fire might be needed to do.
Participant B (Assalāyana): So what strength is there, Assalāyana, what assurance, when the brahmans say, 'Brahmans are the superior caste… Only brahmans are pure, not non-brahmans. Only brahmans are the sons & offspring of Brahmā: born of his mouth, born of Brahmā, created by Brahmā, heirs of Brahmā'?
Participant A (The Buddha): Even though Master Gotama says that, still the brahmans think, 'Brahmans are the superior caste… Only brahmans are pure, not non-brahmans. Only brahmans are the sons & offspring of Brahmā: born of his mouth, born of Brahmā, created by Brahmā, heirs of Brahmā.'
Participant B (Assalāyana): What do you think, Assalāyana? There is the case where a noble warrior youth might cohabit with a brahman maiden, and from their cohabitation a son would be born. Would the son born from the noble warrior you...
```

### Assistant Target

```text
What do you think, Assalāyana? There is the case where there might be two brahman-student brothers, born of the same mother: one learned & initiated, the other not learned & uninitiated. Which of the two would the brahmans serve first at a funeral feast, a milk-rice offering, a sacrifice, or a feast for guests?
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 3: Majjhima Nikaya

- Record ID: `mn123-html:majjhima_nikaya_next_reply_123_4:202-215:ven-nanda`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN123.html:202-215`
- Target: `Participant B (Ven. Ānanda)`
- Target words: `23`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (Ven. Ānanda): Friends, Tathāgatas are both amazing & endowed with amazing qualities, both astounding & endowed with astounding qualities.
Participant A (The Buddha): That being the case, Ānanda, elaborate to a greater extent on the Tathāgata's amazing & astounding qualities.
Participant B (Ven. Ānanda): So other beings have been reborn here, too!
Participant A (The Buddha): May no human or non-human beings or anyone at all harm the bodhisatta or his mother.

Write Participant B's next reply.
```

### Assistant Target

```text
This is a beryl gem, beautiful, radiant, eight-faceted, well-cut & polished, and through it is strung a blue, yellow, red, white, or beige thread.
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 4: Majjhima Nikaya

- Record ID: `mn75-html:majjhima_nikaya_next_reply_75_1:203-204:bh-radv-ja`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN75.html:203-204`
- Target: `Participant B (Bhāradvāja)`
- Target words: `57`
- Reviewer status: `Approve with warning`

### User Prompt

```text
Conversation so far:
Participant A (Māgaṇḍiya): Dear Master Bhāradvāja, whose spread of grass is laid out in the fire hall? One would think it fit to be a contemplative's bed.

Write Participant B's next reply.
```

### Assistant Target

```text
Māgaṇḍiya, there is the Master Gotama, of whom this admirable reputation has spread: 'He is indeed a Blessed One, worthy & rightly self-awakened, consummate in clear-knowing & conduct, well-gone, an expert with regard to the cosmos, unexcelled trainer of people fit to be tamed, teacher of devas & human beings, awakened, blessed.' This is that Master Gotama's bed laid out.
```

### Review Notes

- Summary: `one prior turn of context`
- Warnings:
  - one prior turn of context

## Review Example 5: Majjhima Nikaya

- Record ID: `mn97-html:majjhima_nikaya_next_reply_97_10:203-254:ven-s-riputta`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN97.html:203-254`
- Target: `Participant B (Ven. Sāriputta)`
- Target words: `131`
- Reviewer status: `Approve with warning`

### User Prompt

```text
Conversation so far:
Participant B (Ven. Sāriputta): I trust that the Saṅgha of monks is strong & free from illness?
Participant A (The Buddha): The Saṅgha of monks is also strong & free from illness.
Participant A (The Saṅgha): At the Taṇḍulapāla Gate is a brahman named Dhanañjānin. I trust that he is strong & free from illness?
Participant A (The Buddha): Dhanañjānin the brahman is also strong & free from illness.
Participant A (The Saṅgha): And I trust that Dhanañjānin the brahman is heedful?
Participant A (The Buddha): From where would our Dhanañjānin the brahman get any heedfulness, friend? Relying on the king, he plunders brahmans & householders. Relying on the brahmans & householders, he plunders the king. His wife-a woman of faith, fetched from a family with faith-has died. He has fetched another wife-a woman of no faith-from a family with no faith.
Participant B (Ven. Sāriputta): I trust, Dhanañjānin, that you are heedful?
Participant A (The Buddha): From where would we get any heedfulness, master?-when parents are to be supported, wife & children are to be supported, slaves & workers are to be supported, friend-&-companion duties are to be done for friends & companions, kinsmen-&-relative duties for kinsmen & relatives, guest duties for guests, departed-ancestor duties for departed ancestors, devatā duties for devatās, king duties for the king, and this body also h...
```

### Assistant Target

```text
And what is the path to union with the Brahmās? There is the case where a monk keeps pervading the first direction [the east] with an awareness imbued with good will, likewise the second, likewise the third, likewise the fourth. Thus above, below, & all around, everywhere, in its entirety, he keeps pervading the all-encompassing cosmos with an awareness imbued with good will-abundant, expansive, immeasurable, without hostility, without ill will. He keeps pervading the first direction with an awareness imbued with compassion… empathetic joy… equanimity, likewise the second, likewise the third, likewise the fourth. Thus above, below, & all around, everywhere, in its entirety, he keeps pervading the all-encompassing cosmos with an awareness imbued with equanimity-abundant, expansive, immeasurable, without hostility, without ill will. This, Dhanañjānin, is the path to union with the Brahmās.
```

### Review Notes

- Summary: `slight local scene looseness`
- Warnings:
  - slight local scene looseness

## Review Example 6: Majjhima Nikaya

- Record ID: `mn107-html:majjhima_nikaya_next_reply_107_3:217-220:the-buddha`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN107.html:217-220`
- Target: `Participant B (The Buddha)`
- Target words: `29`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant A (Gaṇaka Moggallāna): When Master Gotama's disciples are thus exhorted & instructed by him, do they all attain unbinding, the absolute conclusion, or do some of them not?
Participant B (The Buddha): Brahman, when my disciples are thus exhorted & instructed by me, some attain unbinding, the absolute conclusion, and some don't.
Participant A (Gaṇaka Moggallāna): What is the reason, what is the cause-when unbinding is there, and the path leading to unbinding is there, and Master Gotama is there as the guide-that when Master Gotama's disciples are thus exhorted & instructed by him, some attain unbinding, the absolute conclusion, and some don't?

Write Participant B's next reply.
```

### Assistant Target

```text
Very well then, brahman, I will cross-question you on this matter. Answer as you see fit. What do you think? Are you skilled in the road leading to Rājagaha?
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 7: Majjhima Nikaya

- Record ID: `mn87-html:majjhima_nikaya_next_reply_87_5:204-224:the-buddha`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN87.html:204-224`
- Target: `Participant B (The Buddha)`
- Target words: `101`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (The Buddha): Householder, your faculties are not those of one who is steady in his own mind. There is an aberration in your faculties.
Participant A (King Pasenadi Kosala): Mallikā, your contemplative, Gotama, has said this: 'Sorrow, lamentation, pain, distress, & despair are born from one who is dear, come springing from one who is dear.'
Participant B (The Buddha): If that was said by the Blessed One, great king, then that's the way it is.
Participant A (King Pasenadi Kosala): No matter what Gotama the contemplative says, Mallikā endorses it: 'If that was said by the Blessed One, great king, then that's the way it is.' Just as, no matter what his teacher says, a pupil endorses it: 'That's the way it is, teacher. That's the way it is.' In the same way, no matter what Gotama the contemplative says, Mallikā endorses it: 'If that was said by the Blessed One, great king, then that's the way it is.' Go away, Mallikā! Out of my sight!
Participant A (Queen Mallikā): Master Gotama, Queen Mallikā shows reverence with her head to your feet and asks whether you are free from illness & affliction, are carefree, strong, & living in comfort. And she says further: 'Lord, did the Blessed One say that sorrow, lamentation, pain, distress, & despair are born from one who is dear, come springing from one who is dear?'

Write Participant B's next reply.
```

### Assistant Target

```text
Once in this same Sāvatthī there was a wife who went to her relatives' home. Her relatives, having separated her from her husband, wanted to give her to another against her will. So she said to her husband, 'These relatives of mine, having separated us, want to give me to another against my will,' whereupon he cut her in two and slashed himself open, thinking, 'Dead we will be together.' It's through this line of reasoning that it may be understood how sorrow, lamentation, pain, distress, & despair are born from one who is dear, come springing from one who is dear.
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 8: Majjhima Nikaya

- Record ID: `mn38-html:majjhima_nikaya_next_reply_38_44:478-508:s-ti`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN38.html:478-508`
- Target: `Participant B (Sāti)`
- Target words: `23`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (Sāti): 'From the cessation of ignorance comes the cessation of fabrications': Thus was it said. Now, monks, is it the case that from cessation of ignorance comes the cessation of fabrications, or not, or how is it here?
Participant A (The Buddha): Lord, from the cessation of ignorance comes the cessation of fabrications. That's how it is for us here: From the cessation of ignorance comes the cessation of fabrications.
Participant B (Sāti): Now, monks, knowing thus and seeing thus, would you run after the past, thinking, 'Were we in the past? Were we not in the past? What were we in the past? How were we in the past? Having been what, what were we in the past'?
Participant A (The Buddha): Knowing thus and seeing thus, would you run after the future, thinking, 'Shall we be in the future? Shall we not be in the future? What shall we be in the future? How shall we be in the future? Having been what, what shall we be in the future'?
Participant B (Sāti): Knowing thus and seeing thus, would you be inwardly perplexed about the immediate present, thinking, 'Am I? Am I not? What am I? How am I? Where has this being come from? Where is it bound'?
Participant A (The Buddha): Knowing thus and seeing thus, would you say, 'The Teacher is our respected mentor. We speak thus out of respect for the Teacher'?
Participant B (Sāti): Knowing thus and seeing th...
```

### Assistant Target

```text
Knowing thus and seeing thus, would you return to the observances, grand ceremonies, & auspicious rites of common contemplatives & brahmans as having any essence?
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 9: Majjhima Nikaya

- Record ID: `mn86-html:majjhima_nikaya_next_reply_86_3:262-265:has-king-seniya-bimbis-ra`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN86.html:262-265`
- Target: `Participant B (Has King Seniya Bimbisāra)`
- Target words: `52`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant A (The Buddha): What is it, great king? Has King Seniya Bimbisāra of Magadha provoked you, or have the Licchavis of Vesālī or some other hostile king?
Participant B (Has King Seniya Bimbisāra): No, lord. King Seniya Bimbisāra of Magadha hasn't provoked me, nor have the Licchavis of Vesālī, nor has some other hostile king. There is a bandit in my realm, lord, named Aṅgulimāla: brutal, bloody-handed, devoted to killing & slaying, showing no mercy to living beings. He has turned villages into non-villages, towns into non-towns, settled countryside into unsettled countryside. Having repeatedly killed human beings, he wears a garland made of fingers. I am going to stamp him out.
Participant A (King Seniya Bimbisāra): Great king, suppose you were to see Aṅgulimāla with his hair & beard shaved off, wearing the ochre robe, having gone forth from the home life into homelessness, refraining from killing living beings, refraining from taking what is not given, refraining from telling lies, living the holy life on one meal a day, virtuous & of fine character: what would you do to him?

Write Participant B's next reply.
```

### Assistant Target

```text
We would bow down to him, lord, or rise up to greet him, or offer him a seat, or offer him robes, almsfood, lodgings, or medicinal requisites for curing illness; or we would arrange a lawful guard, protection, & defense. But how could there be such virtue & restraint in an unvirtuous, evil character?
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 10: Majjhima Nikaya

- Record ID: `mn90-html:majjhima_nikaya_next_reply_90_19:280-310:king-pasenadi-kosala`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN90.html:280-310`
- Target: `Participant B (King Pasenadi Kosala)`
- Target words: `21`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (King Pasenadi Kosala): I'm not asking about the present life, lord. I'm asking about the future life. Is there any distinction or difference among these four castes?
Participant A (General Viḍūḍabha): Lord, can the afflicted devas oust or expel the unafflicted devas from that place?
Participant A (Ven. Ānanda): In that case, general, I will ask you a counter question. Answer as you see fit. Through the extent of land conquered by King Pasenadi Kosala-where he exercises sovereign & independent kingship-is he able to oust or expel a contemplative or brahman from that place, regardless of whether that person has merit or not, or follows the holy life or not?
Participant A (General Viḍūḍabha): Sir, through the extent of land conquered by King Pasenadi Kosala-where he exercises sovereign & independent kingship-he is able to oust or expel a contemplative or brahman from that place, regardless of whether that person has merit or not, or follows the holy life or not.
Participant A (Ven. Ānanda): And what do you think, general? Through the extent of land not conquered by King Pasenadi Kosala-where he does not exercise sovereign & independent kingship-is he able to oust or expel a contemplative or brahman from that place, regardless of whether that person has merit or not, or follows the holy life or not?
Participant A (General Viḍūḍabha): Sir, thro...
```

### Assistant Target

```text
And what do you think, general? Could King Pasenadi Kosala oust or expel the Devas of the Thirty-three from that place?
```

### Review Notes

- Summary: `clean structural pass`
