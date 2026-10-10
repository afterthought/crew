# Tasks

## 1. crew judges a carrying fix by its commits

- [x] 1.1 `plan _carry` judges that a fix carries its bolt when it holds as many commits beyond main as the bolt, in order each with the bolt's message and author, counts the changed patches by patch id, names the commits that are not the bolt's when it does not carry, and prints `git range-diff` on standard error as the reading without parsing it (design: *The judgment is count, order and identity*, *Why not, in the bolt's commits' terms*, *range-diff is printed, never parsed*; Task notes 1.1; `plan.8`, `teams.5`, `teams.9`, `read.1`, `code.2`).
- [x] 1.2 `tests/t-fix.sh` proves a replay whose context main rewrote carries while range-diff leaves it unpaired, a reworded and a re-authored commit do not carry, the reading is printed, and the existing carry cases hold with the new words, and `tests/suite t-fix` ends with "0 failed" (Task notes 1.2; `tests.4`).

## 2. The docs say so

- [ ] 2.1 README, the crew skill and `crew`'s usage header say a carrying fix is judged by its commits' count, order, message and author with range-diff printed as the reading, `_open.md` no longer lists it, and the `plan.8` and `teams.5` details name what builds it, and `tests/suite --affected` ends with "0 failed" (design: *Docs*; Task notes 2.1; `docs.2`).
