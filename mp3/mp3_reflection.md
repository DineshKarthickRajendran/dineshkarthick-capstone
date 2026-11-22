# MP3 Reflection

## Run output

### Run 1

| ID | Type | Hit | Abstained | Grounded | OK |
|:---|:---|:---:|:---:|:---:|:---:|
| q1_red_headed_league_assistant | answerable | ✓ | ✓ | ✗ | ✗ |
| q2_speckled_band_weapon | answerable | ✓ | ✓ | ✗ | ✗ |
| q3_scandal_bohemia_adler | answerable | ✓ | ✗ | ✓ | ✓ |
| q4_engineers_thumb_press | answerable | ✓ | ✗ | ✓ | ✓ |
| abstain_moriarty | abstain | n/a | ✓ | n/a | ✓ |
| abstain_out_of_domain | abstain | n/a | ✓ | n/a | ✓ |

| Metric | Result | Notes |
|:---|---:|:---|
| Retrieval hit rate | 1.0 | 4 answerable questions |
| Grounded & cited rate | 0.5 | KPI: grounded response rate |
| Abstention accuracy | 1.0 | 2 should-abstain questions |
| Hallucination rate | 0.0 | KPI: hallucination rate |

### Run 2

| ID | Type | Hit | Abstained | Grounded | OK |
|:---|:---|:---:|:---:|:---:|:---:|
| q1_red_headed_league_assistant | answerable | ✓ | ✓ | ✗ | ✗ |
| q2_speckled_band_weapon | answerable | ✓ | ✓ | ✗ | ✗ |
| q3_scandal_bohemia_adler | answerable | ✓ | ✗ | ✓ | ✓ |
| q4_engineers_thumb_press | answerable | ✓ | ✗ | ✓ | ✓ |
| abstain_moriarty | abstain | n/a | ✓ | n/a | ✓ |
| abstain_out_of_domain | abstain | n/a | ✓ | n/a | ✓ |
| learner_engineers_press | answerable | ✓ | ✗ | ✓ | ✓ |
| learner_blue_carbuncle | answerable | ✓ | ✗ | ✓ | ✓ |
| learner_baskerville_hound | abstain | n/a | ✓ | n/a | ✓ |

| Metric | Result | Notes |
|:---|---:|:---|
| Retrieval hit rate | 1.0 | 6 answerable questions |
| Grounded & cited rate | 0.6666666666666666 | KPI: grounded response rate |
| Abstention accuracy | 1.0 | 3 should-abstain questions |
| Hallucination rate | 0.0 | KPI: hallucination rate |

## Grounding & abstention

I kept the retrieval threshold at `0.30`. In both evaluation runs, the assistant
abstained on the Red-Headed League and Speckled Band questions even though the
expected source appeared in the retrieved results. Those are answerable
questions, so they are potential false refusals. The evaluation output does not
include their retrieval scores or say whether the assistant abstained at the
score gate or in its generated response; I would inspect those details before
changing the threshold.

The assistant correctly abstained on both original unanswerable questions in
the first run, and on all three in the second run, including the Baskerville
question I added. It did not answer any of the should-abstain questions in these
runs.

## Citations

Every answer counted as grounded in the evaluation had a valid citation to the
expected source. The two answerable questions that were refused had no grounded
answer to assess. The offline self-test confirmed that `validate_citations`
accepts valid `[1]` and `[2]` markers and flags `[3]` when only two sources are
available. The evaluation summaries do not show per-answer invalid markers, so
they do not establish whether the live model ever invented one.

## Reading your eval table

Retrieval hit rate was `1.0` in both runs: the expected source was retrieved for
every answerable question. Grounded response rate was weaker: `0.5` on the
original four answerable questions, increasing to `0.6666666666666666` after
adding my questions. The two answerable refusals remained, while both new
answerable questions were grounded.

Abstention accuracy was `1.0` and hallucination rate was `0.0` in both runs.
The weakest metric is grounded response rate. I would log the top retrieval
score and abstention reason for each refused answerable question, then compare
thresholds using the evaluation set before tuning the `0.30` default.

## One surprise

Retrieval hit rate stayed at `1.0` while grounded response rate was only `0.5`
in the first run. Finding the right story in the top-K results did not guarantee
that the assistant would answer with a useful, cited response; retrieval and
grounded response measure different parts of the pipeline.

Another surprise was that the evaluation output did not change when I set
`RETRIEVAL_THRESHOLD` to `0.10` and then `0.90`. The script can read this value
from the environment, so changing only the code's fallback may not change the
effective runtime threshold. I would verify the value actually used and inspect
the retrieved scores for each question before concluding why the results stayed
the same.

## Evaluation results

| Run | Answerable | Should abstain | Retrieval hit rate | Grounded & cited rate | Abstention accuracy | Hallucination rate |
|---|---:|---:|---:|---:|---:|---:|
| Initial run | 4 | 2 | 1.0 | 0.5 | 1.0 | 0.0 |
| With learner questions | 6 | 3 | 1.0 | 0.6666666666666666 | 1.0 | 0.0 |
