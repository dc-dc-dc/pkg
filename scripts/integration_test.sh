#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

WORK_DIR=$(mktemp -d)
trap "rm -rf $WORK_DIR" EXIT

echo "==> Installing pkg from source for $REPO_ROOT"
uv tool install --force "$REPO_ROOT"

echo "==> Creating test project"
PROJECT_DIR="$WORK_DIR/testproject"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

pkg init testproject --tool uv --no-git

echo "==> Adding minimal test"
mkdir -p tests
printf 'def test_smoke():\n    assert True\n' > tests/test_smoke.py

echo "==> Installing project dependencies"
pkg install

echo "==> Running build"
pkg build

echo ""
echo "Integration test passed!"
