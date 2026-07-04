# Model Routing Guide

Date supplied: `2026-07-04`.

Purpose:
- Keep model cost under control while using strong models for security, money, tenancy, GDPR, child safety, production operations, and phase reviews.

This is a routing guide, not a replacement for step protocols, tests, regression gates, review, and green commits.

## Codex CLI Ladder

| Tier | Model | Effort | Use |
| --- | --- | --- | --- |
| Cheap | `gpt-5.4-mini` | low/medium | Small tests, docs, simple UI, mechanical refactors, snapshots, fixtures |
| Default | `gpt-5.4` | medium | Most implementation steps |
| Hard | `gpt-5.4` | high | Security boundaries, WebSockets, migrations, orchestration, complex debugging |
| Rare escalation | `gpt-5.5` | high/xhigh | Phase review, ledger/VAT correctness, RLS design review, privacy/safety review, stubborn bugs |

Do not use `gpt-5.5 high/xhigh` as the normal Codex CLI worker.

## Claude Code CLI Ladder

| Tier | Model | Effort | Use |
| --- | --- | --- | --- |
| Cheap | `claude-haiku-4-5` | low/medium | Small tests, docs, simple UI polish, trivial fixes |
| Default | `claude-sonnet-5` | medium | Most implementation steps |
| Hard | `claude-sonnet-5` | high | Security, concurrency, migrations, complex feature implementation |
| Rare escalation | `claude-opus-4.8` or `claude-fable-5` | high/xhigh | Phase review, architecture review, ledger/RLS/GDPR, deep debugging |

Do not use `claude-fable-5` as the normal Claude Code worker.

## Simple Rules

- Start most implementation sessions on `gpt-5.4 medium` or `claude-sonnet-5 medium`.
- Use mini/Haiku only for local, bounded, easy-to-verify tasks.
- Use high effort for RLS, tenancy, auth, sessions, ledger, VAT, payments, refunds, outbound PII, migrations, production scripts, and tutor moderation/safety.
- Use top models mostly as reviewers, not writers.
- Never let cheap models make final decisions on security, money, GDPR/privacy, child safety, production operations, or legal/accounting interpretation.
- Legal/accounting interpretation needs human professionals; models can prepare questions and summaries only.

## Phase-Sensitive Guidance

Use stronger review for:
- RLS and cross-tenant harness.
- Provider proxy and outbound PII gate.
- Tutor runtime safety/moderation.
- Commerce ledger, VAT, refunds, reconciliation, and paid flows.
- Production bring-up, backups, rollback, and phase-exit reviews.
- Real robot lab / hardware safety / WebRTC / booking / refunds.

## Cost Control

- Default to `gpt-5.4` / `claude-sonnet-5`, not flagship models.
- Keep top-model sessions short and scoped.
- Do not ask top models to run long exploratory coding sessions.
- Do not use high/xhigh effort for docs, formatting, snapshots, or mechanical tasks.
- Use mini/Haiku for repetitive work only when the test suite can catch mistakes.
- Run top-model reviews before merging high-risk code.

## Sources To Recheck

Model availability and pricing change. Re-check before long implementation phases:
- OpenAI API model docs.
- OpenAI Codex model/pricing docs.
- Anthropic Claude model overview.
- Claude Code settings/effort docs.
