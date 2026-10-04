#!/bin/bash
# Install git pre-commit hook for this repository
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK="$SCRIPT_DIR/.git/hooks/pre-commit"

cat > "$HOOK" << 'EOF'
#!/bin/bash
# Pre-commit hook: update checksum for modified files
set -e

# Update Version/Checksum lines and md5.json (incremental, only modified files)
python3 update_md5.py

exit 0
EOF

chmod +x "$HOOK"
echo "✓ Pre-commit hook installed: $HOOK"
