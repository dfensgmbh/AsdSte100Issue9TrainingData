#!/usr/bin/env bash
#
# Run the same checks as .github/workflows/ci.yml, locally.
#
# Mirrors the GitHub Actions CI pipeline so that "passes locally" also
# means "will pass in CI". Each step is announced, and the script aborts
# on the first failure unless --continue is given.
#
# Usage:
#   scripts/ci-local.sh                    # run everything, stop on first failure
#   scripts/ci-local.sh --skip pylint,mypy # skip selected steps
#   scripts/ci-local.sh --continue         # run all steps regardless
#
set -u

SKIP=""
CONTINUE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip)      SKIP="$2"; shift 2 ;;
        --skip=*)    SKIP="${1#*=}"; shift ;;
        --continue)  CONTINUE=1; shift ;;
        -h|--help)
            sed -n '2,17p' "$0"; exit 0 ;;
        *)
            echo "Unknown argument: $1" >&2; exit 2 ;;
    esac
done

FAILURES=()

step_skipped() {
    local name="$1"
    IFS=',' read -ra arr <<< "$SKIP"
    for s in "${arr[@]}"; do
        [[ "$s" == "$name" ]] && return 0
    done
    return 1
}

run_step() {
    local name="$1"; shift
    if step_skipped "$name"; then
        printf '\n=== [SKIP] %s ===\n' "$name"
        return 0
    fi
    printf '\n=== [RUN ] %s ===\n' "$name"
    local start end rc
    start=$(date +%s)
    if "$@"; then rc=0; else rc=$?; fi
    end=$(date +%s)
    local elapsed=$(( end - start ))
    if [[ $rc -eq 0 ]]; then
        printf '=== [PASS] %s (%ss) ===\n' "$name" "$elapsed"
    else
        printf '=== [FAIL] %s (%ss): exit %d ===\n' "$name" "$elapsed" "$rc"
        FAILURES+=("$name")
        [[ $CONTINUE -eq 0 ]] && exit 1
    fi
}

step_sync()      { uv sync --extra dev --extra test; }
step_pylint()    { uv run pylint $(git ls-files '*.py'); }
step_flake8()    { uv run flake8 src tests; }
step_black()     { uv run black --check .; }
step_mypy()      { uv run mypy src tests; }
step_bandit()    { uv run bandit -r src -ll; }
step_pip_audit() {
    local req
    req=$(mktemp --suffix=.txt)
    trap 'rm -f "$req"' RETURN
    uv export --no-emit-project --no-hashes \
        --format requirements-txt \
        --output-file "$req"
    # Strip the en-core-web-sm GitHub-hosted wheel (same as CI).
    sed -i '/^en-core-web-sm /,/^[^[:space:]#]/{/^en-core-web-sm /d; /^[[:space:]#]/d}' "$req"
    uv run pip-audit --strict --requirement "$req"
}
step_tests()     {
    uv run coverage run -m unittest discover -v -s tests -t . -p 'test_*.py' \
        && uv run coverage report -m
}
step_build()     { uv build; }

echo "Repository: $(pwd)"
echo "uv:         $(uv --version)"

run_step sync      step_sync
run_step pylint    step_pylint
run_step flake8    step_flake8
run_step black     step_black
run_step mypy      step_mypy
run_step bandit    step_bandit
run_step pip-audit step_pip_audit
run_step tests     step_tests
run_step build     step_build

echo
if [[ ${#FAILURES[@]} -eq 0 ]]; then
    echo '*** All checks passed ***'
    exit 0
else
    echo "*** ${#FAILURES[@]} check(s) failed: ${FAILURES[*]} ***"
    exit 1
fi
