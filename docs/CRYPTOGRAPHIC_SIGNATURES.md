# Sigil Cryptographic Signatures

## Overview

Sigil cryptographic signatures create a **chain of custody** for video content without relying on blockchain. This system proves ownership of perceptual hashes through Ed25519 digital signatures and Web2 timestamp oracles.

## The Problem This Solves

### Without Signatures
- **Claim**: "I created this video"
- **Counter**: "You just generated that hash yesterday to match our dataset"
- **Result**: No mathematical defense

### With Signatures
- **Claim**: "I possessed this hash on January 1st, 2025"
- **Proof**: Ed25519 signature + Twitter timestamp
- **Result**: Burden of proof shifts from you to the defendant

---

## Architecture: The Three-Part Defense

```
┌─────────────────────────────────────────────────────────────┐
│                  SIGIL DEFENSE SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. PERCEPTUAL HASH (Public Truth)                          │
│     ├─ Fixed Seed 42 = Anyone can replicate                 │
│     ├─ 256-bit fingerprint of visual content                │
│     └─ Survives compression, transcoding                    │
│                                                              │
│  2. CRYPTOGRAPHIC SIGNATURE (Private Ownership)             │
│     ├─ Ed25519 digital signature                            │
│     ├─ Proves possession of private key                     │
│     └─ Mathematically binds hash to identity                │
│                                                              │
│  3. WEB2 ANCHORING (Timestamp Oracle)                       │
│     ├─ Post signature to Twitter/GitHub                     │
│     ├─ Platform timestamps prove "when"                     │
│     └─ Courts recognize these timestamps                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Generate Identity (One-Time Setup)

```bash
# Identity is auto-generated on first --sign, but you can do it explicitly
python -m cli.identity generate
```

**Output:**
```
🔐 Generating new Ed25519 identity...

✅ Identity Created Successfully

🔐 Key ID: SHA256:Abc123XyZ...
📁 Private key: /Users/you/.sigil/identity.pem
📄 Public key:  /Users/you/.sigil/identity.pub

⚠️  Security Notice:
   Your private key is stored unencrypted at ~/.sigil/identity.pem
   This is intentional (like SSH keys) for ease of use.
```

### 2. Sign a Video Hash

```bash
# Extract hash and create signature in one step
python -m cli.extract my_video.mp4 --sign --verbose
```

**Output:**
```
Loading video: my_video.mp4
Processing 60 frames...
Loaded 60 frames
Extracting perceptual features...
Computing 256-bit perceptual hash...

✅ Hash saved to: my_video_hash.txt

📊 Hash Statistics:
   Length: 256 bits
   Bits set: 128 / 256
   Format: binary

🔐 Creating cryptographic signature...
[Sigil] ✓ Identity created: SHA256:Abc123...
✅ Signature saved to: my_video.mp4.signature.json
   Key ID: SHA256:Abc123...
   Algorithm: Ed25519

💡 Next steps:
   1. Verify signature: python -m cli.verify my_video.mp4.signature.json
   2. Post to Twitter/GitHub for timestamp proof
   3. Anchor: python -m cli.anchor my_video.mp4.signature.json --twitter <url>
```

### 3. Verify Signature

```bash
python -m cli.verify my_video.mp4.signature.json
```

**Output:**
```
✅ SIGNATURE VALID

📄 File: my_video.mp4.signature.json
🔐 Key ID: SHA256:Abc123...
🔑 Algorithm: Ed25519
📊 Hash: a3f2b1c4d5e6...
📅 Signed At: 2025-12-29T12:00:00Z
```

### 4. Anchor to Twitter (Timestamp Proof)

```bash
# First, post your signature to Twitter:
# Tweet: "Claiming ownership of video hash a3f2...
#         Signature: <paste from signature.json>
#         Public key: SHA256:Abc123..."

# Then anchor the tweet URL
python -m cli.anchor my_video.mp4.signature.json \
  --twitter https://twitter.com/yourname/status/123456
```

**Output:**
```
🔗 Anchoring signature to Twitter...
   Signature: my_video.mp4.signature.json
   Tweet: https://twitter.com/yourname/status/123456

✅ Signature anchored successfully
   Total anchors: 1
```

---

## How It Works

### Signature Format

**File: `my_video.mp4.signature.json`**

```json
{
  "claim": {
    "hash_hex": "a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
    "metadata": {
      "video_filename": "my_video.mp4",
      "frames_analyzed": 60
    },
    "timestamp": "2025-12-29T12:00:00Z"
  },
  "proof": {
    "signature": "base64_encoded_ed25519_signature...",
    "public_key": "base64_encoded_public_key...",
    "key_id": "SHA256:Abc123XyZ...",
    "algorithm": "Ed25519",
    "signed_at": "2025-12-29T12:00:00Z"
  },
  "anchors": [
    {
      "type": "twitter",
      "url": "https://twitter.com/user/status/123456",
      "anchored_at": "2025-12-29T12:05:00Z"
    },
    {
      "type": "github",
      "url": "https://gist.github.com/user/abc123",
      "anchored_at": "2025-12-29T12:10:00Z"
    }
  ],
  "version": "1.0"
}
```

### Cryptographic Properties

1. **Ed25519 Signatures**
   - 32-byte keys (256 bits)
   - 10x faster than RSA
   - Used by Signal, SSH, age encryption
   - Deterministic (no RNG needed)

2. **Canonical JSON Signing**
   - Sorted keys, no whitespace
   - Prevents signature malleability
   - Verifiable by anyone with public key

3. **Key Fingerprinting**
   - SHA256 hash of public key
   - Format: `SHA256:base64(sha256(pubkey))`
   - Human-readable identification

---

## Complete Workflow: From Creation to Court

### Phase 1: Creation (Day 1)

```bash
# Create your video content
# Extract hash and sign it
python -m cli.extract my_documentary.mp4 --sign --verbose

# Output: my_documentary.mp4.signature.json
```

### Phase 2: Public Timestamp (Within 24 hours)

```bash
# Post to Twitter
# "I created this documentary. Proof of ownership:
#  Hash: a3f2b1c4d5e6f7a8...
#  Signature: [paste from .signature.json]
#  Key: SHA256:Abc123..."

# Anchor the tweet
python -m cli.anchor my_documentary.mp4.signature.json \
  --twitter https://twitter.com/you/status/123
```

### Phase 3: Distribution (Ongoing)

```bash
# Upload to YouTube, Vimeo, etc.
# Anyone can verify your claim later
```

### Phase 4: Legal Defense (If needed)

**Scenario:** OpenAI used your video without permission.

**Your Evidence:**
1. `my_documentary.mp4.signature.json` (signed Jan 1, 2025)
2. Twitter post from Jan 1, 2025 (timestamp proof)
3. Perceptual hash matches video in OpenAI's dataset

**Legal Argument:**
- Signature proves you possessed the hash on Jan 1
- Perceptual hash proves visual similarity
- Twitter timestamp proves public claim on specific date
- **Burden of proof shifts:** OpenAI must prove they DIDN'T use your video

---

## Identity Management

### Show Current Identity

```bash
python -m cli.identity show
```

### Generate New Identity

```bash
python -m cli.identity generate

# Warning: This invalidates all previous signatures!
```

### Export Public Key

```bash
# For sharing with others to verify your signatures
python -m cli.identity export --output my_public_key.pem
```

### Import Existing Key

```bash
# Use a key from another machine
python -m cli.identity import /path/to/identity.pem
```

---

## API Usage

### Sign a Hash via API

```bash
curl -X POST http://localhost:5000/api/extract \
  -F "video=@my_video.mp4" \
  -F "sign=true" \
  -F "max_frames=60"
```

**Response:**
```json
{
  "success": true,
  "hash": "01010101...",
  "hash_hex": "a3f2b1c4...",
  "hash_id": 123,
  "signature": {
    "claim": { "hash_hex": "...", ... },
    "proof": { "signature": "...", ... },
    "anchors": [],
    "version": "1.0"
  }
}
```

### Verify Signature via API

```bash
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d @my_video.mp4.signature.json
```

**Response:**
```json
{
  "success": true,
  "valid": true,
  "key_id": "SHA256:Abc123...",
  "hash_hex": "a3f2b1c4...",
  "signed_at": "2025-12-29T12:00:00Z",
  "algorithm": "Ed25519"
}
```

---

## Security & Threat Model

### What This Protects Against

✅ **Post-hoc hash fabrication**
- Attacker: "You just made up that hash"
- Defense: Timestamped signature proves prior possession

✅ **Identity impersonation**
- Attacker: "Someone else signed this"
- Defense: Only holder of private key could create signature

✅ **Timestamp manipulation**
- Attacker: "You backdated this claim"
- Defense: Web2 anchors (Twitter/GitHub) are tamper-proof via platform APIs

### What This Does NOT Protect Against

❌ **Private key compromise**
- If your `~/.sigil/identity.pem` is stolen, attacker can sign as you
- Mitigation: Generate new identity, re-sign all content
- Note: Like SSH keys, this is an acceptable risk for this use case

❌ **Hash collisions**
- Attacker creates different video with same perceptual hash
- Mitigation: 256-bit space makes this computationally infeasible
- Note: Would require breaking the hash function itself

❌ **Legal jurisdiction issues**
- Signature proves ownership, but laws vary by country
- Mitigation: Consult local IP attorney for enforcement strategy

### Why Unencrypted Keys?

**Decision:** Store keys unencrypted (like SSH keys)

**Rationale:**
1. **UX Friction:** Password prompts kill viral adoption
2. **Threat Model:** Not protecting nuclear codes; protecting video ownership claims
3. **Recovery:** If compromised, generate new identity and re-sign
4. **Precedent:** SSH, git commit signing work the same way

---

## Why Web2 Anchors (Not Blockchain)?

### Twitter/GitHub > Blockchain for Legal Cases

| Criterion | Web2 (Twitter/GitHub) | Blockchain (Ethereum/Arweave) |
|-----------|----------------------|------------------------------|
| **Court Recognition** | ✅ High (mainstream platforms) | ❌ Low (niche tech) |
| **Timestamp Reliability** | ✅ Strong (Twitter API, GitHub commits) | ⚠️ Moderate (block times vary) |
| **Longevity** | ✅ 15+ year track record | ❌ Uncertain (many chains fail) |
| **Cost** | ✅ Free | ❌ Gas fees ($1-50 per tx) |
| **Simplicity** | ✅ URL-based proof | ❌ Wallet, private keys, block explorers |
| **Adoption** | ✅ Judges understand Twitter | ❌ Expert witness needed |

### The "Oracle Problem"

Signatures prove **WHO**, not **WHEN**.

**Solution:** Rely on trusted timestamp oracles:
- **Twitter**: Public tweets with API-verifiable timestamps
- **GitHub**: Commit/issue timestamps in git history

These platforms have legal precedent. Blockchain does not (yet).

**Optional:** Archive.org can provide additional backup, but is not required for legal proof.

---

## Advanced Usage

### Batch Signing

```bash
# Sign multiple videos
for video in *.mp4; do
  python -m cli.extract "$video" --sign
done
```

### Custom Key Location

```bash
# Use a different key for this project
python -m cli.extract video.mp4 --sign \
  --key-path /path/to/project_identity.pem
```

### Programmatic Signing (Python)

```python
from core.crypto_signatures import SignatureManager
from core.perceptual_hash import (
    load_video_frames,
    extract_perceptual_features,
    compute_perceptual_hash
)

# Extract hash
frames = load_video_frames("video.mp4", max_frames=60)
features = extract_perceptual_features(frames)
hash_bits = compute_perceptual_hash(features)
hash_hex = hex(int(''.join(map(str, hash_bits)), 2))[2:].zfill(64)

# Sign it
sig_manager = SignatureManager()
sig_file = sig_manager.create_signature_file(
    hash_hex=hash_hex,
    output_path="video.mp4.signature.json",
    video_filename="video.mp4"
)

print(f"Signed! Key ID: {sig_manager.identity.key_id}")
```

---

## Troubleshooting

### "No identity found"

```bash
# Generate identity first
python -m cli.identity generate
```

### "Signature verification failed"

- Check that signature file hasn't been modified
- Ensure you're using the correct public key
- Verify JSON format is valid

### "Permission denied: ~/.sigil/identity.pem"

```bash
# Fix permissions
chmod 600 ~/.sigil/identity.pem
```

---

## Legal Disclaimer

**This system provides technical evidence of hash ownership, not legal ownership of content.**

- Consult an IP attorney for enforcement strategy
- Signature proves possession of hash at a timestamp
- Courts must still rule on copyright/ownership
- Laws vary by jurisdiction

**Use this as evidence, not as a substitute for legal counsel.**

---

## Technical Specifications

### Signature Algorithm
- **Type:** Ed25519 (EdDSA)
- **Curve:** Curve25519
- **Key Size:** 256 bits (32 bytes)
- **Signature Size:** 512 bits (64 bytes)
- **Security Level:** 128-bit (equivalent to AES-128)

### Hash Function
- **Signature:** Ed25519 (built-in)
- **Key Fingerprint:** SHA-256
- **Perceptual Hash:** 256-bit custom (Canny + Gabor + Laplacian + RGB histograms)

### File Formats
- **Private Key:** PEM (PKCS#8, unencrypted)
- **Public Key:** PEM (SubjectPublicKeyInfo)
- **Signature:** JSON (base64-encoded binary)

### Dependencies
- `cryptography>=41.0.0` (Python library)
- Ed25519 implementation from `cryptography.hazmat.primitives.asymmetric.ed25519`

---

## Comparison to Other Systems

### vs. PGP/GPG
- **Sigil:** Video-specific, Ed25519, simple UX
- **PGP:** General-purpose, RSA, complex UX
- **Sigil wins on:** Simplicity, speed, modern crypto

### vs. Blockchain NFTs
- **Sigil:** Free, Web2 timestamps, court-friendly
- **NFT:** Expensive, blockchain timestamps, technical barrier
- **Sigil wins on:** Cost, legal recognition, UX

### vs. C2PA (Adobe Content Authenticity)
- **Sigil:** Perceptual hash (survives re-encoding)
- **C2PA:** Embedded metadata (lost on re-encoding)
- **Sigil wins on:** Robustness against compression

---

## Future Enhancements

- [ ] Hardware security module (HSM) integration for enterprise
- [ ] Multi-signature support (M-of-N threshold signatures)
- [ ] Automatic GitHub Actions integration for CI/CD
- [ ] Browser extension for one-click verification
- [ ] Mobile app for on-the-go signing

---

## References

- [Ed25519 Specification](https://ed25519.cr.yp.to/)
- [RFC 8032: Edwards-Curve Digital Signature Algorithm](https://datatracker.ietf.org/doc/html/rfc8032)
- [Twitter API Timestamp Verification](https://developer.twitter.com/en/docs)
- [GitHub API](https://docs.github.com/en/rest)

---

**Status:** 🟢 **Production Ready**

**License:** MIT

**Author:** Sigil Project

**Contact:** See [GitHub Issues](https://github.com/yourname/sigil/issues)
