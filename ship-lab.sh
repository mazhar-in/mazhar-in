#!/usr/bin/env bash
# ==============================================================================
# ship-lab.sh — One-Command Shipper for mazhar.in/labs
# Usage: ./ship-lab.sh "projectile-motion: add velocity vector telemetry"
# ==============================================================================

set -e

MSG="${1:-update labs}"

echo "⚡ Step 1: Running Labs Auto-Discovery & SEO Indexer..."
if command -v python3 &>/dev/null; then
    python3 scripts/update_labs.py
else
    python scripts/update_labs.py
fi

echo "📦 Step 2: Staging repository changes..."
git add .

echo "📝 Step 3: Committing: ship lab: $MSG..."
git commit -m "ship lab: $MSG"

echo "🚀 Step 4: Pushing to origin..."
git push origin main

echo "✅ Lab successfully shipped to production!"
