[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

# AsdSte100Issue9TrainingData

Training datasets for ASD-STE100 Issue 9.

This training dataset let you fine-tune an LLM to better understand, what the words in the "ASD-STE100 Issue 9" standard mean.

## Datasets

Each dataset corresponds to a sub-command of the `create` CLI and a
GitHub issue that tracks its design and progress. The default output
file for every command is a JSON Lines file named
`taskNN.jsonl` in the current working directory; pass `--output` and
`--file` to override.

| Command | Task | Default output | GitHub issue | Status |
| --- | --- | --- | --- | --- |
| `ambiguity` | Task 1: Ambiguity | `task01.jsonl` | [#1](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/1) | Stub |
| `lexicon` | Task 2: Explicit Lexicon Lookup (Word + POS Level) | `task02.jsonl` | [#2](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/2) | Stub |
| `pos` | Task 3: POS Identification in Context | `task03.jsonl` | [#3](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/3) | Stub |
| `rewrite` | Task 4: Sentence Rewriting for Compliance | `task04.jsonl` | [#4](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/4) | Stub |
| `compliance` | Task 5: Compliance Verification of Correct Usage | `task05.jsonl` | [#5](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/5) | Stub |
| `choice` | Task 6: Word Choice Between Approved Synonyms | `task06.jsonl` | [#6](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/6) | Stub |
| `restriction` | Task 7: Restriction Reason Explanation | `task07.jsonl` | [#7](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/7) | Stub |
| `paragraph` | Task 8: Full Paragraph Compliance Audit | `task08.jsonl` | [#8](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/8) | Stub |
| `grammar` | Task 9: Internal Grammar Engine (POS Identification) | `task09.jsonl` | [#9](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/9) | Stub |
| `verb` | Task 10: Approved Verb Lookup by Definition | `task10.jsonl` | [#10](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/10) | Stub |
| `category` | Task 11: Category-Based Word Restrictions | `task11.jsonl` | [#11](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/11) | Stub |
| `query` | Interactive ASD-STE100 query against a chat model (`response-<timestamp>.json`) | — | — | **Working** (only command currently implemented) |

### Progress

At this time only the `query` command is implemented. It tokenises and
lemmatises an input string with spaCy, then runs a Pydantic AI agent
against a configured chat model. The agent has access to the
`get_word_status` and `get_word_alternative` tools, which look words
up in the ASD-STE100 vocabulary, and is required to return a JSON
response listing every word together with a short summary and its
ASD-STE100 status.

The other 11 commands (`ambiguity` through `category`) are registered
placeholders. They validate their arguments, log their inputs, and
exit without producing data. Each command tracks its own GitHub issue
(see the table) where the dataset design is being worked out.
