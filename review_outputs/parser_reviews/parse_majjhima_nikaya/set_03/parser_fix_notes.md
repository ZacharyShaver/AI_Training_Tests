# `parse_majjhima_nikaya.py` Set 03 Parser Fix Notes

- Rewrote Majjhima row assembly around broader local exchange windows instead of the earlier ultra-tight continuity gate that collapsed output to one row.
- Limited speaker inference to narration around reporting verbs, stripped embedded quote content from speaker search, and restored pure-quote alternation from local speaker pairs.
- Hardened speaker validation so generic clause-openers, bare titles, group labels, sentence fragments, and place names cannot enter the speaker channel.
- Rejected malformed target fragments with dangling ellipses or unmatched quotation marks before they reach review.
