#!/usr/bin/env bash
set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: ./commit.sh \"commit message\"" >&2
  exit 1
fi

VERSION=$(tr -d '[:space:]' < VERSION.md)
TAG="v${VERSION}"

git add -A
git commit -m "$1"

if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Tag $TAG already exists, skipping tag creation."
else
  git tag -a "$TAG" -m "Release $TAG"
  echo "Created tag $TAG"
fi
