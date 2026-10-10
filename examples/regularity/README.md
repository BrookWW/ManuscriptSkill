# Synthetic review fixture

This short two-file manuscript is deliberately defective. It is test material,
not a research contribution or a recommended result to cite.

Use `examples/regularity` as the project root and `paper/main.tex` as the entry.
Choose a new output directory outside that root. The input contains a false
continuity-to-Lipschitz claim, a sound affine identity, a nested entry, a local
include, a custom `\f` macro, and a missing font package. It has no bibliography.

The fixture tests whether a review identifies the false claim with an actual
counterexample, preserves sound material and the supplied format, explains any
change to the main conclusion, resolves the compile defect when tools permit,
and saves a complete source handoff without changing the input. A reviewer may
retain the refuted claim pending an author decision, provided the report makes
its status and alternatives explicit. A completed handoff does not make that
claim true.

For planning-only evaluation, request a segmented plan in a separate new
directory; no manuscript edits or review handoff should be produced. To test a
block, start a fresh chat with the saved plan, a specified block, and a new output.

See the [validation record](../../docs/validation.md) for observed results and
limitations.

中文说明：这是故意包含错误的合成测试稿，不是研究成果。项目根目录为
`examples/regularity`，入口为 `paper/main.tex`；输出应另建目录。测试关注反例、
原稿保留、格式保留、依赖修复及完整交接，不衡量研究级数学可靠性。
