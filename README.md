# Cold-email reply classifier

Sorts replies to cold email into `positive`, `info_request`, `not_interested`, `unsubscribe`,
`out_of_office`, `left_company`, `wrong_person` and `other`, and computes reply rates the honest way:
**contacted leads are the denominator, never replies**. Out-of-office and left-company replies are
split out first, because a departed mailbox auto-replies every time and makes a dead list look alive.

Two classifiers, one eval harness:

```
python -m reply_classifier eval data/holdout2.csv                 # keyword rules, no network
python -m reply_classifier eval data/holdout2.csv --method llm    # needs OPENROUTER_API_KEY
python -m reply_classifier rates replies.csv --contacted 576      # raw vs human reply rate
```

## Results

All sets are synthetic, written by me, 39 replies each (no real replies, no client data).

| Classifier | Dev set | Fresh holdout (`holdout2.csv`) |
|---|---|---|
| Keyword rules | 100% | **41%** |
| LLM (`openai/gpt-4o-mini`, temperature 0) | not run | **97.4%** |

What happened, in order:

1. Wrote the rules against `dev.csv`: 100%. That number is meaningless, because the rules were
   written while looking at those examples.
2. Scored them once on a first holdout (`holdout.csv`): **56%**. Out-of-office recall was 0%.
3. Generalised the rules and re-ran: 100% on that set. Also meaningless now, since I had read the misses.
4. Wrote a fresh set (`holdout2.csv`) and scored it once, with no tuning afterwards: **41%**.
   The rules in this repo are the ones that scored 41%.
5. Ran the LLM on the same fresh set: **97.4%**. Its one miss was "I'll pass this along to my boss and
   see.", which it called `wrong_person`. I labeled it `other`, and the label is arguable.

The takeaway is the gap between steps 1 and 4. Regex rules memorise their examples; they do not
generalise to new phrasing. Use the rules as a free first pass for the unambiguous cases and an LLM
for the rest.

## Caveats

- n=39 per set; one reply is 2.6 points. Treat 97.4% as "good", not "97.4% in production".
- The labels are mine, and several are judgment calls (`other` vs `not_interested`).
- Real replies are messier than these: quoted threads, signatures, other languages, HTML.
- Never commit real replies or client names to `data/`. The LLM call sends reply text to OpenRouter.

## Tests

```
python -m unittest discover -s tests
```

The rules classifier and eval harness use only the standard library.
