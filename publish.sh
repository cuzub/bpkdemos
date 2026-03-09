#!/bin/bash

set -euo pipefail

VERSION_FILE=".image_version"

FRONT_IMAGE="cuzub/bpk-demo-frontend"
BACK_IMAGE="cuzub/bpk-demo-backend"

PLATFORMS="linux/amd64,linux/arm64"
BUILDER_NAME="multiarch-builder"

echo "================================"
echo " BPK Demo multi-arch publish"
echo "================================"

if [ ! -f "$VERSION_FILE" ]; then
  echo "1.0" > "$VERSION_FILE"
fi

CURRENT="$(tr -d '[:space:]' < "$VERSION_FILE")"

if ! echo "$CURRENT" | grep -Eq '^[0-9]+\.[0-9]+$'; then
  echo "Error: $VERSION_FILE must contain a version like 1.0"
  exit 1
fi

MAJOR="${CURRENT%%.*}"
MINOR="${CURRENT##*.}"
NEW_MINOR=$((MINOR + 1))
VERSION="${MAJOR}.${NEW_MINOR}"

echo "Current version : $CURRENT"
echo "New version     : $VERSION"

echo
echo "=== Buildx setup ==="
if ! docker buildx inspect "$BUILDER_NAME" >/dev/null 2>&1; then
  docker buildx create --name "$BUILDER_NAME" --use
else
  docker buildx use "$BUILDER_NAME"
fi

docker buildx inspect --bootstrap >/dev/null

echo
echo "=== Build and push frontend ==="
docker buildx build \
  --platform "$PLATFORMS" \
  -t "$FRONT_IMAGE:$VERSION" \
  -t "$FRONT_IMAGE:latest" \
  --push \
  ./frontend

echo
echo "=== Build and push backend ==="
docker buildx build \
  --platform "$PLATFORMS" \
  -t "$BACK_IMAGE:$VERSION" \
  -t "$BACK_IMAGE:latest" \
  --push \
  ./backend

echo "$VERSION" > "$VERSION_FILE"

echo
echo "================================"
echo "Published:"
echo "  $FRONT_IMAGE:$VERSION"
echo "  $FRONT_IMAGE:latest"
echo "  $BACK_IMAGE:$VERSION"
echo "  $BACK_IMAGE:latest"
echo "================================"