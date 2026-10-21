# Context hygiene

Every phase's output is persisted to `docs/specs/`, `docs/specs/STATUS.md` and the knowledge graph before its gate closes - nothing load-bearing lives only in this session's conversation. Start steps 1-3 already re-read everything needed from disk, so starting a *new* orchestrator session instead of continuing this one is always safe, not just tolerated:

- **Between features, always.** This session's transcript from feature A isn't useful context for feature B - carrying it forward spends context on the previous feature's delegation noise instead of the next feature's actual files. Recommend a fresh session at the start of the next `/plan-grill`/`/orchestrate`.
- **Mid-feature, if this session has been through many TDD-loop iterations or several long phases.** The signal: re-deriving state from `docs/specs/<feature>/STATUS.md` that a fresh read would give for free, meaning the accumulated transcript isn't adding value anymore.

Suggest this to the user rather than forcing it - they may want this session's own recall of *why* a decision was made mid-conversation, which a fresh session won't have (though it's in the specs/ADRs if it mattered enough to record).
