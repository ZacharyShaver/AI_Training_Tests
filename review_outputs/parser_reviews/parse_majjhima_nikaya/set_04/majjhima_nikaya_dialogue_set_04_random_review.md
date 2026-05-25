# `parse_majjhima_nikaya.py` Set 04 Random Review

Sampled rows: `10`
Source dataset: `review_outputs/parser_reviews/parse_majjhima_nikaya/set_04/majjhima_nikaya_dialogue_set_04.jsonl`

## Review Policy Summary

- Approve: `7`
- Approve with warning: `3`
- Reject: `0`

## Review Example 1: Majjhima Nikaya

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

## Review Example 2: Majjhima Nikaya

- Record ID: `mn75-html:majjhima_nikaya_next_reply_75_10:205-215:m-ga-iya`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN75.html:205-215`
- Target: `Participant B (Māgaṇḍiya)`
- Target words: `31`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant A (The Buddha): What a bad thing to see that we see, Master Bhāradvāja!-that we see the bed of Master Gotama, that destroyer of growth!
Participant A (Bhāradvāja): Be careful of your words, Māgaṇḍiya! Be careful of your words! Many wise noble warrior, wise brahmans, wise householders, & wise contemplatives have full confidence in that Master Gotama and have been disciplined by him in the noble method, the Dhamma that is skillful.
Participant A (The Buddha): Master Bhāradvāja, even if we saw Master Gotama face to face, we would say to him face to face: 'Gotama the contemplative is a destroyer of growth.' Why is that? Because it has come down in our scripture.
Participant A (Bhāradvāja): If it wouldn't be burdensome to you, Master Māgaṇḍiya, I will report this to Master Gotama.
Participant A (The Buddha): Go ahead, Master Bhāradvāja. You may tell him what was said.
Participant A (The Buddha): Bhāradvāja, did you have a conversation with Māgaṇḍiya the wanderer about this very same spread of grass?
Participant A (Bhāradvāja): We wanted to report this very thing to Master Gotama, but Master Gotama, without having been told at all, has told us!
Participant A (The Buddha): Māgaṇḍiya, the eye that finds pleasure in forms, that delights in forms, that rejoices in forms: That has been tamed, guarded, protected, & restrained by the Tathāgata, and he tea...
```

### Assistant Target

```text
It was precisely in reference to that, Master Gotama, that I said, 'Gotama the contemplative is a destroyer of growth.' Why is that? Because it has come down in our scripture.
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 3: Majjhima Nikaya

- Record ID: `mn38-html:majjhima_nikaya_next_reply_38_18:371-389:s-ti`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN38.html:371-389`
- Target: `Participant B (Sāti)`
- Target words: `20`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant A (The Buddha): Worthless man, you will be recognized for your own evil viewpoint. I will cross-question the monks on this matter.
Participant A (The Buddha): Monks, do you too understand the Dhamma as taught by me in the same way that the monk Sāti, the Fisherman's Son, does when, through his own poor grasp (of the Dhamma), he not only slanders us but also digs himself up (by the root) and produces much demerit for himself?
Participant B (Sāti): No, lord, for in many ways the Blessed One has said of dependently co-arisen consciousness, 'Apart from a requisite condition, there is no coming-into-play of consciousness.'
Participant A (The Buddha): Monks, do you see, 'This has come to be'?
Participant B (Sāti): Monks, do you see, 'It comes into play from that nutriment'?
Participant A (The Buddha): Monks, do you see, 'From the cessation of that nutriment, what has come to be is subject to cessation'?
Participant B (Sāti): From the doubt-'Has this come to be?'-does uncertainty arise?
Participant A (The Buddha): From the doubt-'Does it come into play from that nutriment?'-does uncertainty arise?

Write Participant B's next reply.
```

### Assistant Target

```text
From the doubt-'From the cessation of that nutriment, is what has come to be subject to cessation?'-does uncertainty arise?
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 4: Majjhima Nikaya

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

## Review Example 5: Majjhima Nikaya

- Record ID: `mn82-html:majjhima_nikaya_next_reply_82_43:308-317:master-ra-hap-la`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN82.html:308-317`
- Target: `Participant B (Master Raṭṭhapāla)`
- Target words: `40`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (Master Raṭṭhapāla): And what do you think, great king? Are you even now as strong in arm & strong in thigh, as fit, & as seasoned in warfare?
Participant A (The Buddha): Not at all, Master Raṭṭhapāla. I'm now aged, old, elderly, advanced in years, having come to the last stage of life, 80 years old. Sometimes, thinking, 'I will place my foot here,' I place it somewhere else.
Participant B (Master Raṭṭhapāla): It was in reference to this, great king, that the Blessed One who knows & sees, worthy & rightly self-awakened, said: 'The world is swept away. It does not endure.' Having known & seen & heard this, I went forth from the home life into homelessness.
Participant A (The Buddha): Now, in this royal court there are elephant troops & cavalry & chariot troops & infantry that will serve to defend us from dangers. And yet you say, 'The world is without shelter, without protector.' How is the meaning of this statement to be understood?
Participant B (Master Raṭṭhapāla): What do you think, great king? Do you have any recurring illness?
Participant A (The Buddha): Yes, Master Raṭṭhapāla, I have a recurring wind-illness. Sometimes my friends & advisors, relatives & blood-kinsmen, stand around me saying, 'This time King Koravya will die. This time King Koravya will die.'
Participant B (Master Raṭṭhapāla): And what do you think, great king? Can you...
```

### Assistant Target

```text
It was in reference to this, great king, that the Blessed One who knows & sees, worthy & rightly self-awakened, said: 'The world is without shelter, without protector.' Having known & seen & heard this, I went forth from the home life into homelessness.
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 6: Majjhima Nikaya

- Record ID: `mn123-html:majjhima_nikaya_next_reply_123_9:206-226:the-buddha`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN123.html:206-226`
- Target: `Participant B (The Buddha)`
- Target words: `82`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant B (The Buddha): That being the case, Ānanda, elaborate to a greater extent on the Tathāgata's amazing & astounding qualities.
Participant A (Ven. Ānanda): So other beings have been reborn here, too!
Participant B (The Buddha): May no human or non-human beings or anyone at all harm the bodhisatta or his mother.
Participant A (Ven. Ānanda): This is a beryl gem, beautiful, radiant, eight-faceted, well-cut & polished, and through it is strung a blue, yellow, red, white, or beige thread.
Participant B (The Buddha): Be gratified, O queen. A son of great influence has been born to you.
Participant A (Ven. Ānanda): I am the foremost of the world. I am chief of the world. I am the best of the world.
Participant B (The Buddha): In the Blessed One's presence, lord, I have heard this, in the Blessed One's presence I have learned this: 'When the bodhisatta left his mother's womb, a great, measureless radiance surpassing the effulgence of the devas appeared in the cosmos with its devas, Māras, & Brahmās, with its people with their contemplatives & brahmans, their royalty & commonfolk. Even in the inter-cosmic void of the unrestrained darkness, pitch-black darkness, where even the light of the sun & moon-so mighty, so powerful-doesn't reach, even there the great, measureless radiance surpassing the effulgence of the devas appeared. And the beings reborn the...
```

### Assistant Target

```text
The fact, lord, that feelings are known to the Blessed One when they arise, known when they remain, known when they go to their end; perceptions are known to the Blessed One when they arise, known when they remain, known when they go to their end; thoughts are known to the Blessed One when they arise, known when they remain, known when they go to their end: I hold this, too, lord, to be an amazing & astounding quality of the Blessed One.
```

### Review Notes

- Summary: `clean structural pass`

## Review Example 7: Majjhima Nikaya

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

## Review Example 8: Majjhima Nikaya

- Record ID: `mn70-html:majjhima_nikaya_next_reply_70_2:207-209:the-buddha`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN70.html:207-209`
- Target: `Participant B (The Buddha)`
- Target words: `45`
- Reviewer status: `Approve with warning`

### User Prompt

```text
Conversation so far:
Participant B (The Buddha): Come, monk. In my name, call the monks led by Assaji & Punabbasu, saying, 'The Teacher calls you, friends.'
Participant B (The Buddha): The Teacher calls you, friends.

Write Participant B's next reply.
```

### Assistant Target

```text
Is it true, monks, that a large number of monks went to you… and you said, '…Why should we, abandoning what is immediately visible, chase after something subject to time? We will eat in the evening, in the morning, & in the wrong-time during the day.'
```

### Review Notes

- Summary: `minimal context`
- Warnings:
  - minimal context

## Review Example 9: Majjhima Nikaya

- Record ID: `mn38-html:majjhima_nikaya_next_reply_38_41:447-502:the-buddha`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN38.html:447-502`
- Target: `Participant B (The Buddha)`
- Target words: `23`
- Reviewer status: `Approve with warning`

### User Prompt

```text
Conversation so far:
Participant B (The Buddha): Lord, from ignorance as a requisite condition come fabrications. That's how it is for us here: From ignorance as a requisite condition come fabrications.
Participant A (Sāti): 'From the cessation of birth comes the cessation of aging-&-death': Thus was it said. Now, monks, is it the case that from the cessation of birth comes the cessation of aging-&-death, or not, or how is it here?
Participant B (The Buddha): Lord, from the cessation of birth comes the cessation of aging-&-death. That's how it is for us here: From the cessation of birth comes the cessation of aging-&-death.
Participant A (Sāti): 'From the cessation of ignorance comes the cessation of fabrications': Thus was it said. Now, monks, is it the case that from cessation of ignorance comes the cessation of fabrications, or not, or how is it here?
Participant B (The Buddha): Lord, from the cessation of ignorance comes the cessation of fabrications. That's how it is for us here: From the cessation of ignorance comes the cessation of fabrications.
Participant A (Sāti): Now, monks, knowing thus and seeing thus, would you run after the past, thinking, 'Were we in the past? Were we not in the past? What were we in the past? How were we in the past? Having been what, what were we in the past'?
Participant B (The Buddha): Knowing thus and seeing thus, would you run after the...
```

### Assistant Target

```text
Knowing thus and seeing thus, would you say, 'The Teacher is our respected mentor. We speak thus out of respect for the Teacher'?
```

### Review Notes

- Summary: `slight local scene looseness`
- Warnings:
  - slight local scene looseness

## Review Example 10: Majjhima Nikaya

- Record ID: `mn31-html:majjhima_nikaya_next_reply_31_2:206-209:anuruddha`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN31.html:206-209`
- Target: `Participant B (Anuruddha)`
- Target words: `20`
- Reviewer status: `Approve with warning`

### User Prompt

```text
Conversation so far:
Participant B (Anuruddha): Friend park warden, don't stand in the way of the Blessed One. It's our Teacher, the Blessed One, who has arrived!
Participant A (The Buddha): Is it tolerable for you, Anuruddhas? Are you getting by? Are you weary from going for alms?

Write Participant B's next reply.
```

### Assistant Target

```text
It's tolerable, O Blessed One. We're getting by, O Blessed One. And we're not weary, lord, from going for alms.
```

### Review Notes

- Summary: `minimal context`
- Warnings:
  - minimal context
