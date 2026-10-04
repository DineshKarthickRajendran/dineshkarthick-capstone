# Prompt Pairwise 001: Results Overview

## At a glance

The run evaluated 20 golden questions. The IDEAL answer won most comparisons; APP won four, and two comparisons were order-dependent ties.

| Outcome | Questions | Share |
|---|---:|---:|
| IDEAL wins | 14 | 70% |
| APP wins | 4 | 20% |
| Order-dependent ties | 2 | 10% |
| **Total** | **20** | **100%** |

```text
IDEAL  14/20  ##############  70%
APP     4/20  ####            20%
Ties    2/20  ##              10%
```

Among the 18 comparisons with a consistent winner, IDEAL won 14 (about 78%) and APP won 4 (about 22%).

## Question breakdown

- **APP wins:** g004, g006, g007, g009
- **IDEAL wins:** g001, g002, g003, g008, g010, g012, g013, g014, g015, g016, g017, g018, g019, g020
- **Order-dependent ties:** g005, g011

## Interpretation and scope

In this run, the golden IDEAL answers were favored substantially more often than the APP answers. The two ties indicate cases where the pairwise judge did not select the same winner in both answer orders.

The available results report aggregate APP-versus-IDEAL outcomes. Although the report lists prompt v1 and prompt v2 as inputs, it does not provide separate results for each prompt or a direct v1-versus-v2 comparison. These results therefore do not show which prompt performed better.

Source: [pairwise-001-results.md](../data/pairwise-001-results.md)