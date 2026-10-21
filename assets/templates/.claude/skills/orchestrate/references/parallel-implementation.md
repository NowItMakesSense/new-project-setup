# Parallel implementation (optional, phase 5 only)

Default is sequential. Only use this when two or more phase-5 tasks are confirmed independent - no shared files, no ordering dependency - and it's worth the added coordination:

1. Confirm independence explicitly with the user if there's any doubt; don't infer it from task titles alone.
2. Delegate each task's `test` -> `implementer` loop with `isolation: "worktree"` on the Agent/Task call instead of relying on "don't touch the same file" as a convention - each task gets its own git worktree/branch, which removes the collision risk structurally rather than hoping the independence check was right.
3. Once a task's tests are green in its worktree, merge its branch back before starting the next phase - this is an outward-facing-enough git operation that it gets the same human confirmation as any other destructive/merge action, same as prime directive 5.
4. If a merge conflict or a late-discovered dependency shows the tasks weren't actually independent, stop that pair and fall back to sequential for the rest - don't force it through.

This never changes the human gates on phases 6-8; it only changes how phase 5 itself is executed.
