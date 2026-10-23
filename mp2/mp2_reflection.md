# MP2 Reflection

## What worked

`python mp2_rag.py validate` matched the expected source for all five
questions: 2/2 predefined and 3/3 learner questions. The easy Blue Carbuncle
question also matched both expected facts (2/2), and the Speckled Band
question matched 5/6.

## What didn't work

Some answers cited the correct story but missed expected details. The assistant
question matched only 1/5 facts; the Engineer's Thumb and Scandal in Bohemia
questions each matched 2/3. So perfect source matching did not guarantee that
the answer included every requested detail.

## What I'd change

I would inspect the three partial fact matches, especially the assistant
question's 1/5, and try a reranking strategy: retrieve a broader set of
candidate chunks, then rerank them by relevance to the question before building
the answer context. I would also adjust the prompt to address each part of the
question. Then I would rerun the same five questions and compare fact coverage,
source matches, and latency to check whether the changes improve results without
losing the 5/5 source matches.

## One surprise

All five questions retrieved and cited the expected story, including the
harder multi-detail questions, but their fact coverage varied from 1/5 to 5/6.
The run took about 2.5–3.8 seconds per question. This made the difference
between finding the right source and answering every part of a question
particularly clear.
