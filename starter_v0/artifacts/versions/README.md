# Evaluation artifact provenance

These snapshots make the corrected base evaluation reproducible.

| Version | Source | Change |
|---|---|---|
| v0 | `2c1a5ec` | Original starter prompt and declarations, byte-for-byte from Git. |
| v1 | `a6ec1af` | Historical clarification, confirmation, context, and domain rules; original declarations. |
| v2 | `c767a87` | Historical improved tool descriptions; prompt identical to v1. |
| v3 | Corrected submission | Restore security rules from `b3177f0`, add general routing, latest-intent, enum, and missing-information rules; retain v2 declarations. |

The final v3 snapshot matches `../system_prompt.md` and `../tools.yaml` byte-for-byte. No printer-specific or QA-specific rule is included in the final prompt.

All corrected runs use the same current agent, provider adapter, tool implementations, and fixed datasets from checkout `f070dae`. Thus v0 is the original **artifact baseline on the current runtime**, not a replay of every historical source file. The runner only adds optional pacing and retries (`--case-delay`, `--case-retries`, `--retry-delay`) for provider transport errors; scoring and cases are unchanged. Historical group-run metrics are not reconstructed or relabeled as base evidence.

Run from `starter_v0` (OpenAI credentials must already be configured in the ignored `.env`):

```powershell
foreach ($version in @('v0', 'v1', 'v2', 'v3')) {
    python run_eval.py --provider openai --model gpt-4o --version $version --suite base --eval-cases data/eval_base.json --system-prompt "artifacts/versions/$version/system_prompt.md" --tools "artifacts/versions/$version/tools.yaml" --case-delay 10 --case-retries 3 --retry-delay 20
}
python run_eval.py --provider openai --model gpt-4o --version v3 --suite group --eval-cases data/eval_group.json --case-delay 5 --case-retries 3 --retry-delay 15
python run_eval.py --provider openai --model gpt-4o --version v3 --suite adversarial --eval-cases data/eval_adversarial.json --case-delay 5 --case-retries 3 --retry-delay 15
```

Accept a run only when `provider_error_cases == 0` and `measured_cases == total_cases`. Rerun the full suite if provider errors occur; do not combine partial runs. Routing scores do not establish successful tool execution or end-to-end safety. See the report for tool-result limitations.
