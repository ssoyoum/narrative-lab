# Generation evaluation v1

The 36 fixed cases in `cases.jsonl` cover 3 themes × 3 locations × 2 protagonists × 2 endings. Atmosphere rotates across the cases. Case IDs and inputs stay fixed when comparing revisions or providers. This is a deliberately small diagnostic set, not a representative sample of all possible narratives.

## Run

```bash
python scripts/evaluate_generation.py
# Optional, paid/provider-dependent run with OPENAI_API_KEY configured:
python scripts/evaluate_generation.py --mode configured --output evaluation/results-configured
```

The default baseline mode forces the deterministic draft even on machines with an API key. Each run writes `run.json` (revision, dataset source and structural counts), `outputs.jsonl` (full generation and evidence), and `review.csv` (blank human scores). Keep result directories outside commits unless a reviewed comparison is intentionally published. Do not compare fallback-corpus results with the 246-story SQLite corpus as if they came from the same data.

## Review protocol

Review the generated text **and** its prompt, blueprint, and cited source beats in `outputs.jsonl`. Score each dimension 0, 1, or 2:

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Constraint adherence | Key selected conditions missing or contradicted | Some conditions reflected | Theme, mood, setting, protagonist and ending substantively reflected |
| Source consistency | Claimed source is contradicted or unattributed events dominate | Some source events recognizable, attribution/role unclear | Bound source events traceably used in their intended roles |
| Character consistency | Identity or motivations conflict | Mostly stable, with unexplained changes | Identity, goal and choices remain coherent |
| Place consistency | Setting conflicts with chosen place | Place named but weakly maintained | Place materially shapes events and remains coherent |
| Plot coherence | Beats lack causality or resolution | Partial causal chain | Stakes, choice and consequence follow clearly |

Use `reviewer` and `notes` for attribution and concrete evidence. A second reviewer should score independently before reconciling disagreements. Report per-dimension distributions and disagreements, not just an aggregate score. An empty review sheet does **not** mean the narratives passed.

The script's structural checks test beat presence, source IDs and literal text presence. Literal presence is only a diagnostic and does not establish character, place or literary quality. For configured LLM mode, record the provider/model and compare the actual `generation_provider` and `generation_status` per row: a fallback output must not be counted as an LLM success.

The [first baseline diagnostic](baseline-2026-09-20.md) found missing source beat bindings in 8 of 36 cases. This remains an open quality issue for retrieval and binding, not a score for the final stories.
