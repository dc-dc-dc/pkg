#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

WORK_DIR=$(mktemp -d)
trap "rm -rf $WORK_DIR" EXIT

echo "==> Installing pkg from source for $REPO_ROOT"
uv tool install --force "$REPO_ROOT"

echo "==> Creating test project"
cd "$WORK_DIR"
pkg init testproject --tool bun --no-git

PROJECT_DIR="$WORK_DIR/testproject"
cd "$PROJECT_DIR"

echo "==> Adding minimal test"
mkdir -p tests
cat > tests/main.test.ts << 'PYEOF'
import { test, expect, describe } from "bun:test";

describe("main operations", () => {
  test("testing console", () => {
  });
});

PYEOF

echo "==> Installing project dependencies"
pkg install

echo "==> Running build"
pkg build

echo ""
echo "Integration test passed!"
