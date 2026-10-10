# Personal Manuscript Preferences

This optional BrookWW profile preserves the source project's structural,
language, and TeX preferences. Load it only when the user requests the bundled
author style. These are author preferences, not journal requirements. Apply
them within the task defined in [SKILL.md](../SKILL.md). Respect the user's current explicit instructions,
mathematical and factual correctness, authoritative wording, and the
[template](../assets/tex_template.tex). Apply unambiguous preferences directly;
report conflicts or ambiguities that could affect meaning.

## Structure

Organize the paper around its mathematical contribution and the reader's path
to understanding and checking it. Choose the order, grouping, and depth of
background, principal results, related work, and proof ideas to suit the
manuscript. Integrate these topics or use informative subsections as helpful.

Make principal statements self-contained, introducing the setting, terminology,
and notation needed to understand their hypotheses, conclusions, and scope
before the relevant statements. Introduce proof-only notation where used.
Present the supported results without fixing the draft's grouping or order.

Discuss relevant prior work accurately and with enough mathematical detail to
clarify the manuscript's contribution. Verify the claims and sources used, and
choose the scope and depth of the discussion to support the reader's understanding.

After an important result, use a concise Remark when it adds understanding of
the hypotheses, sharpness, scope, consequences, or relationship to known results.
Support substantive claims with an argument or precise citation. A Remark
should add mathematical insight rather than repeat the statement or praise it;
use it where helpful.

Explain the actual obstacles and decisive proof ideas where they best orient
the reader, keeping detailed technical estimates in the body. Balance prose and
formulas to make the reasoning clear and easy to follow. Collect shared
preparation in a separate section when this aids reading; otherwise introduce
it where needed. Provide transitions and a brief organizational roadmap when
they help, with accurate references. Every section should serve a substantive
purpose, without filler added to satisfy a structural pattern.

## Title and abstract

Use a precise, searchable title matching the principal contribution. Write a
concise, self-contained abstract, normally in one paragraph, stating the problem,
supported main result, and essential hypotheses or limitations. Briefly mention
a distinctive method when it helps explain the contribution. Choose wording
and formulas for clarity, without word, sentence, or formula quotas unless the
target journal explicitly requires them. Omit generic openings, routine
literature discussion, and organizational detail; preserve necessary
qualifications and do not pad a shorter abstract.

## Template and notation

Retain the template's class, layout, protected macro meanings, and shared
theorem numbering. Add subject-specific packages and definitions as needed.
Resolve same-name macros with different meanings by renaming the manuscript
macro and updating all its uses, preserving its mathematical meaning.
Do not overwrite it with the template definition.
Use Theorem for principal results, Proposition for substantial supporting
results, and Lemma for proof infrastructure. Optional parenthetical titles
are reserved for main theorems and important propositions, never lemmas,
corollaries, or mere proof steps.

- For one numbered multiline formula, use aligned inside equation; for an
  unnumbered one, aligned inside \[...\]. Use align only for separately numbered
  equations, not with \notag or \nonumber to simulate a single number.
- Write fractions with \frac or the protected \f macro. Do not use \tfrac,
  \dfrac, \genfrac, \nicefrac, primitive \over or \atop, or a literal
  mathematical slash.
- Prefer \quad to \qquad and ordinary to long arrows unless the alternative
  has a clear purpose; prefer \backslash to \setminus.
- Space differential measures as in \mathrm{d} x or an equivalent protected
  macro. Use \subset\subset for compact inclusion and \llcorner for measure
  restriction, not \Subset, \upharpoonright, \restriction, or an evaluation bar.
- Match delimiters to meaning: parentheses for grouping, brackets for outer
  grouping or conventional objects, braces for sets, angle brackets for
  inner products and duality, and single/double vertical bars for absolute
  values/norms. Do not use plain angle signs as brackets or single bars for norms.
- Use \inner, \paren, \abs, \norm or their matched \left...\right forms when
  enlargement is needed. Do not use \big, \Big, \bigg, \Bigg or their variants,
  or redefine \( and \).
- Enumerations use Arabic labels. In theorem-like environments use exactly
  label=$(\theenumi)$; preserve the template's first-level enumerate default.
- Use exactly \bibliographystyle{plain}.

## Language and author information

Express quantifiers and logical relationships precisely. Hyphenate productive
"non-" words in author-controlled prose. Preserve official titles, quotations,
bibliography fields, identifiers, commands, and externally fixed terminology
when applying these preferences.

Express the mathematics directly, without irrelevant editorial workflow language.

Use only supplied or verified author metadata and declarations. Remove empty
optional placeholders and report necessary missing facts in the final response.
When keywords or MSC classifications are needed, select relevant keywords and
verify the classification codes.
