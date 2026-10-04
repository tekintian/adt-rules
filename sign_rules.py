#!/usr/bin/env python3
"""
Sign own-source ABP subscription files with RSA-SHA256.

ABP official checksum algorithm (from combineSubscriptions.py):
  1. splitlines() to read
  2. Pop header [Adblock Plus ...]
  3. seen = {'checksum', 'version'} (pre-seeded, so first Checksum/Version lines are removed)
  4. Remove duplicate metadata (first occurrence kept for others)
  5. MD5(header + \\n + lines.join(\\n))
  6. Base64 encode, strip trailing =

Our extension:
  - Also exclude ! Signature: lines from checksum (decoupled from signature)
  - Signature is computed over content excluding ! Signature: line (includes Checksum)

Flow:
  1. Remove existing ! Signature: line
  2. Compute checksum (ABP algo, excludes Checksum + Signature lines)
  3. Update Checksum line
  4. Compute signed content (excludes Signature line, includes Checksum line)
  5. Sign
  6. Add ! Signature: line
  7. Verify both
"""
import hashlib
import re
import base64
import subprocess
import tempfile
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PRIVATE_KEY = SCRIPT_DIR / 'rsa-private-key.pem'
PUBLIC_KEY = SCRIPT_DIR / 'rsa-public-key.pem'

OWN_SOURCE_FILES = ['adt-base.txt', 'adt-hot.txt', 'adt-dev.txt', 'adt-video.txt', 'adt-web.txt', 'adt-dnr.txt']

def sign_content(content: str, private_key: Path) -> str:
    proc = subprocess.run(
        ['openssl', 'dgst', '-sha256', '-sign', str(private_key), '-binary'],
        input=content.encode('utf-8'),
        capture_output=True,
        check=True,
    )
    return base64.b64encode(proc.stdout).decode('ascii')

def verify_signature(content: str, signature_b64: str, public_key: Path) -> bool:
    sig_bytes = base64.b64decode(signature_b64)
    with tempfile.NamedTemporaryFile(suffix='.sig', delete=False) as sf:
        sf.write(sig_bytes)
        sig_path = sf.name
    proc = subprocess.run(
        ['openssl', 'dgst', '-sha256', '-verify', str(public_key), '-signature', sig_path],
        input=content.encode('utf-8'),
        capture_output=True,
    )
    os.unlink(sig_path)
    return proc.returncode == 0

def compute_checksum_for_lines(lines: list[str]) -> str:
    """ABP official checksum algorithm (from combineSubscriptions.py)."""
    if not lines:
        return ''
    working = list(lines)
    header = working.pop(0)

    seen = {'checksum', 'version'}
    def check_line(line: str) -> bool:
        match = re.search(
            r'^\s*!\s*(Redirect|Homepage|Title|Checksum|Version|Expires|Signature)\s*:',
            line, re.M | re.I,
        )
        if not match:
            return True
        key = match.group(1).lower()
        if key in seen:
            return False
        seen.add(key)
        return key != 'signature'

    filtered = list(filter(check_line, working))
    content = '\n'.join([header] + filtered)
    md5_digest = hashlib.md5(content.encode('utf-8')).digest()
    return base64.b64encode(md5_digest).decode('ascii').rstrip('=')

def compute_signed_content(lines: list[str]) -> str:
    filtered = [l for l in lines if not re.match(r'^!\s*signature\s*:', l, re.I)]
    return '\n'.join(filtered).replace('\r', '')

def find_metadata_insert_idx(lines: list[str]) -> int:
    insert_idx = 1
    for i, l in enumerate(lines):
        if l.startswith('!') and l.strip() != '!':
            insert_idx = i + 1
        elif not l.startswith('!') and l.strip():
            break
    return insert_idx

def process_file(filepath: Path):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()
    lines = raw.splitlines()

    lines = [l for l in lines if not re.match(r'^!\s*signature\s*:', l, re.I)]
    sig_insert_idx = find_metadata_insert_idx(lines)

    new_checksum = compute_checksum_for_lines(lines)

    for i, l in enumerate(lines):
        if re.match(r'^!\s*checksum\s*:', l, re.I):
            lines[i] = f'! Checksum: {new_checksum}'
            break

    signed_content = compute_signed_content(lines)
    signature = sign_content(signed_content, PRIVATE_KEY)
    lines.insert(sig_insert_idx, f'! Signature: {signature}')

    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')

    with open(filepath, 'r', encoding='utf-8') as f:
        raw_v = f.read()
    lines_v = raw_v.splitlines()

    sig_b64 = None
    for l in lines_v:
        m = re.match(r'^!\s*signature\s*:\s*(.+)', l, re.I)
        if m:
            sig_b64 = m.group(1).strip()
            break
    verify_content = compute_signed_content(lines_v)
    sig_valid = verify_signature(verify_content, sig_b64, PUBLIC_KEY) if sig_b64 else False

    final_checksum = compute_checksum_for_lines(lines_v)
    current_checksum = None
    for l in lines_v:
        m = re.match(r'^!\s*checksum\s*:\s*(.+)', l, re.I)
        if m:
            current_checksum = m.group(1).strip()
            break
    cksum_valid = final_checksum == current_checksum

    sig_s = '✓' if sig_valid else '✗'
    ck_s = '✓' if cksum_valid else '✗'
    print(f'  {sig_s} {filepath.name}: signature={sig_valid} checksum={cksum_valid} ({current_checksum})')

def main():
    print('=== Signing own-source subscription files ===')
    modified = []
    for fname in OWN_SOURCE_FILES:
        filepath = SCRIPT_DIR / fname
        if not filepath.exists():
            print(f'  SKIP {fname}: not found')
            continue
        process_file(filepath)
        modified.append(fname)

    if modified:
        try:
            subprocess.run(['git', 'add'] + modified, cwd=str(SCRIPT_DIR), check=True)
            print(f'\n  git add: {", ".join(modified)}')
        except Exception as e:
            print(f'\n  WARNING: git add failed: {e}')

    print('\nDone!')

if __name__ == '__main__':
    main()
