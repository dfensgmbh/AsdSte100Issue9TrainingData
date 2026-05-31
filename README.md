[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![CI](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/actions/workflows/ci.yml?query=branch%3Amain)
[![CodeQL](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/actions/workflows/codeql.yml?query=branch%3Amain)

# AsdSte100Issue9TrainingData

Training datasets for ASD-STE100 Issue 9.

**WIP** no training data yet available!!

This training dataset let you fine-tune an LLM to better understand, what the words in the "ASD-STE100 Issue 9" standard mean.

## Datasets

Each dataset corresponds to a sub-command of the `create` CLI and a
GitHub issue that tracks its design and progress. The default output
file for every command is a JSON Lines file named
`taskNN.jsonl` in the current working directory; pass `--output` and
`--file` to override.

| Command | Task | Default output | Status |
| --- | --- | --- | --- |
| `ambiguity` | Task 1: Ambiguity ([#1](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/1)) | `task01.jsonl` | Stub |
| `lexicon` | Task 2: Explicit Lexicon Lookup (Word + POS Level) ([#2](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/2)) | `task02.jsonl` | Stub |
| `pos` | Task 3: POS Identification in Context ([#3](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/3)) | `task03.jsonl` | Stub |
| `rewrite` | Task 4: Sentence Rewriting for Compliance ([#4](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/4)) | `task04.jsonl` | Stub |
| `compliance` | Task 5: Compliance Verification of Correct Usage ([#5](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/5)) | `task05.jsonl` | Stub |
| `choice` | Task 6: Word Choice Between Approved Synonyms ([#6](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/6)) | `task06.jsonl` | Stub |
| `restriction` | Task 7: Restriction Reason Explanation ([#7](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/7)) | `task07.jsonl` | Stub |
| `paragraph` | Task 8: Full Paragraph Compliance Audit ([#8](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/8)) | `task08.jsonl` | Stub |
| `grammar` | Task 9: Internal Grammar Engine (POS Identification) ([#9](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/9)) | `task09.jsonl` | Stub |
| `verb` | Task 10: Approved Verb Lookup by Definition ([#10](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/10)) | `task10.jsonl` | Stub |
| `category` | Task 11: Category-Based Word Restrictions ([#11](https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/11)) | `task11.jsonl` | Stub |
| `query` | Interactive ASD-STE100 query against a chat model | `response-<timestamp>.json` | **WIP** |

### Progress

At this time only the `query` command is implemented. It tokenises and
lemmatises an input string with spaCy, then runs a Pydantic AI agent
against a configured chat model. The agent has access to the
`get_word_status` and `get_word_alternative` tools, which look words
up in the ASD-STE100 vocabulary, and is required to return a JSON
response listing every word together with a short summary and its
ASD-STE100 status.

