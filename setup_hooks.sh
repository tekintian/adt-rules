#!/bin/bash
# Install git pre-commit hook for this repository
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK="$SCRIPT_DIR/.git/hooks/pre-commit"

cat > "$HOOK" << 'EOF'
#!/bin/bash
# Pre-commit hook: update checksum + sign own-source rules
set -e

# 1. Update Version/Checksum lines and md5.json (incremental, only modified files)
python3 update_md5.py

# 2. Sign own-source rules (adt-*.txt) with RSA-SHA256
python3 sign_rules.py

exit 0
EOF

chmod +x "$HOOK"
echo "✓ Pre-commit hook installed: $HOOK"
