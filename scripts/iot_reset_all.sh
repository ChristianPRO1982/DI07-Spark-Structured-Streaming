#!/usr/bin/env bash
# Reset all generated data for the DI07 project and restore gitkeep files.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${PROJECT_ROOT}/data"

TARGETS=(
  "${DATA_DIR}/landing"
  "${DATA_DIR}/checkpoints"
  "${DATA_DIR}/delta/bronze/sensor_data"
  "${DATA_DIR}/delta/bronze/delta_smoke_test"
  "${DATA_DIR}/delta/silver"
  "${DATA_DIR}/delta/gold"
)

echo "Stopping containers (safer reset)..."
docker compose down >/dev/null 2>&1 || true

echo "Taking ownership of data directory..."
sudo chown -R "${USER}:${USER}" "${DATA_DIR}" || true
sudo chmod -R u+rwX "${DATA_DIR}" || true

echo "Deleting generated data..."
for path in "${TARGETS[@]}"; do
  if [[ -e "${path}" ]]; then
    sudo rm -rf "${path}"
    echo "Deleted: ${path}"
  fi
done

echo "Recreating base directory structure..."
mkdir -p \
  "${DATA_DIR}/landing" \
  "${DATA_DIR}/checkpoints" \
  "${DATA_DIR}/delta/bronze" \
  "${DATA_DIR}/delta/silver" \
  "${DATA_DIR}/delta/gold"

echo "Restoring .gitkeep files..."
touch \
  "${DATA_DIR}/landing/.gitkeep" \
  "${DATA_DIR}/checkpoints/.gitkeep" \
  "${DATA_DIR}/delta/bronze/.gitkeep" \
  "${DATA_DIR}/delta/silver/.gitkeep" \
  "${DATA_DIR}/delta/gold/.gitkeep"

echo "Reset completed successfully."
