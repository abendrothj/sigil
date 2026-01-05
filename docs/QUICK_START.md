# Sigil Quick Start Guide

## What is Sigil?

Sigil is a **perceptual video hash tracking system with cryptographic signatures** that creates a complete "chain of custody" for your video content.

### The Three-Part Defense System

```
1. PERCEPTUAL HASH (Public Truth)
   └─ Anyone can replicate (fixed seed 42)
   └─ Survives compression, transcoding
   └─ 256-bit fingerprint of visual content

2. CRYPTOGRAPHIC SIGNATURE (Private Ownership)
   └─ Ed25519 digital signature
   └─ Proves you possessed the hash at signing time
   └─ Mathematically binds hash to your identity

3. WEB2 ANCHORING (Timestamp Oracle)
   └─ Post to Twitter/GitHub
   └─ Archive with Internet Archive
   └─ Courts recognize these timestamps
```

---

## Installation

```bash
# Clone repository
git clone https://github.com/yourname/sigil.git
cd sigil

# Install dependencies
pip3 install -r requirements.txt

# Verify installation
python -m cli.identity show
```

---

## Usage Examples

### Example 1: Basic Hash Extraction (No Signature)

```bash
# Extract perceptual hash from video
python -m cli.extract my_video.mp4 --verbose

# Output: 256-bit hash saved to my_video_hash.txt
```

**Use case:** Quick forensic tracking, no legal proof needed

### Example 1a: Private Verifiability (Optional)
```bash
# Extract hash with a secret seed (only you or anyone with the password can verify)
python -m cli.extract my_video.mp4 --seed "my-secret-password"
```

---

### Example 2: Sign a Video for Legal Protection

```bash
# Extract hash AND create cryptographic signature
python -m cli.extract my_documentary.mp4 --sign --verbose
```

**Output:**
```
Loading video: my_documentary.mp4
Processing 60 frames...
Computing 256-bit perceptual hash...

✅ Hash saved to: my_documentary_hash.txt

🔐 Creating cryptographic signature...
[Sigil] Generating new Ed25519 identity...
[Sigil] ✓ Identity created: SHA256:Abc123XyZ...

✅ Signature saved to: my_documentary.mp4.signature.json
   Key ID: SHA256:Abc123XyZ...
   Algorithm: Ed25519

💡 Next steps:
   1. Verify signature: python -m cli.verify my_documentary.mp4.signature.json
   2. Post to Twitter/GitHub for timestamp proof
   3. Archive with: python -m cli.anchor my_documentary.mp4.signature.json --twitter <url>
```

**Files created:**
- `my_documentary_hash.txt` - The perceptual hash
- `my_documentary.mp4.signature.json` - The cryptographic signature
- `~/.sigil/identity.pem` - Your private signing key (auto-generated)

**Use case:** Content creators protecting original work before distribution

---

### Example 3: Verify a Signature

```bash
# Anyone can verify your signature
python -m cli.verify my_documentary.mp4.signature.json
```

**Output:**
```
✅ SIGNATURE VALID

📄 File: my_documentary.mp4.signature.json
🔐 Key ID: SHA256:Abc123XyZ...
🔑 Algorithm: Ed25519
📊 Hash: a3f2b1c4d5e6f7a8...
📅 Signed At: 2025-12-29T12:00:00Z
```

**Use case:** Third-party verification of ownership claims

---

### Example 4: Create Timestamp Proof (The "Kill Shot")

**Step 1: Create signature**
```bash
python -m cli.extract my_documentary.mp4 --sign
```

**Step 2: Post to Twitter**

Tweet this:
```
🎬 Claiming ownership of "My Documentary 2025"

📊 Hash: a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6...
🔐 Key ID: SHA256:Abc123XyZ...

Verifiable via Sigil
#ContentOwnership #DMCA
```

**Step 3: Anchor the tweet**
```bash
python -m cli.anchor my_documentary.mp4.signature.json \
  --twitter https://twitter.com/yourname/status/123456
```

**Output:**
```
🔗 Anchoring signature to Twitter...
   Signature: my_documentary.mp4.signature.json
   Tweet: https://twitter.com/yourname/status/123456

✅ Signature anchored successfully
   Total anchors: 1
```

**What this proves in court:**
1. You possessed the hash on the date you signed it (Ed25519 signature)
2. The signature was publicly posted on a specific date (Twitter timestamp)
3. The timestamp is verifiable via Twitter's API

**Use case:** Maximum legal protection before uploading to YouTube, etc.

---

### Example 5: Compare Two Videos

```bash
# Check if two videos are perceptually similar
python -m cli.compare original.mp4 reupload.mp4 --verbose
```

**Output:**
```
Comparing videos...

✅ MATCH FOUND
   Hamming distance: 12 bits
   Similarity: 95.3%
   Threshold: 30 bits

The videos are perceptually similar despite:
- Different encoding (H.264 vs VP9)
- Different resolution (1080p vs 720p)
- Different compression (CRF 18 vs CRF 28)
```

**Use case:** Detecting re-uploads, copyright infringement

---

## Real-World Workflow: From Creation to Legal Action

### Day 1: Create and Sign

```bash
# Film your documentary
# Extract hash and sign immediately
python -m cli.extract my_documentary.mp4 --sign

# Post signature to Twitter within 24 hours
# Anchor the tweet
python -m cli.anchor my_documentary.mp4.signature.json \
  --twitter https://twitter.com/you/status/123
```

### Day 30: Upload to YouTube

```bash
# Upload to YouTube
# YouTube transcodes: 1080p → 720p, CRF 28
# Perceptual hash still matches (12-bit drift, well within threshold)
```

### Day 180: Discovery

```bash
# You discover OpenAI trained on your video
# Download sample from their dataset
python -m cli.compare my_documentary.mp4 openai_sample.mp4

# Output: 14-bit Hamming distance → MATCH
```

### Day 365: Legal Action

**Your evidence package:**
1. `my_documentary.mp4.signature.json` (signed Jan 1, 2025)
2. Twitter post from Jan 1, 2025 (timestamp proof)
3. Hash comparison showing 14-bit match

**Legal argument:**
- Signature proves you owned the hash on Jan 1, 2025
- Perceptual hash proves visual similarity
- Twitter timestamp proves public claim on specific date
- **Burden of proof shifts:** OpenAI must prove they DIDN'T use your video

---

## Command Reference

### Hash Extraction

```bash
# Basic
python -m cli.extract video.mp4

# With signature
python -m cli.extract video.mp4 --sign

# Custom output
python -m cli.extract video.mp4 --output hash.txt --format hex

# More frames for accuracy (default: 60)
python -m cli.extract video.mp4 --frames 120
```

### Signature Verification

```bash
# Verify signature
python -m cli.verify signature.json

# JSON output
python -m cli.verify signature.json --json
```

### Identity Management

```bash
# Show current identity
python -m cli.identity show

# Generate new identity
python -m cli.identity generate

# Export public key
python -m cli.identity export --output pubkey.pem

# Import existing key
python -m cli.identity import /path/to/key.pem
```

### Anchoring

```bash
# Anchor to Twitter
python -m cli.anchor signature.json --twitter <tweet_url>

# Anchor to GitHub
python -m cli.anchor signature.json --github <gist_url>

# List anchors
python -m cli.anchor signature.json --list
```

### Comparison

```bash
# Compare two videos
python -m cli.compare video1.mp4 video2.mp4

# Compare hash files
python -m cli.compare hash1.txt hash2.txt --hash-input

# Compare against specific hash
python -m cli.compare video.mp4 --target <hash_string>

# Custom threshold (default: 30 bits)
python -m cli.compare video1.mp4 video2.mp4 --threshold 20
```

---

## API Usage

### Start API Server

```bash
python -m api.server
```

Server runs on `http://localhost:5000`

### Extract Hash with Signature

```bash
curl -X POST http://localhost:5000/api/extract \
  -F "video=@my_video.mp4" \
  -F "sign=true" \
  -F "max_frames=60"
```

### Verify Signature

```bash
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d @signature.json
```

### Get Server Identity

```bash
curl http://localhost:5000/api/identity
```

---

## FAQ

### Q: Is this like blockchain/NFTs?

**A:** No. Sigil uses Web2 platforms (Twitter, GitHub) as timestamp oracles because:
- Courts understand Twitter timestamps
- No gas fees
- No wallet complexity
- Legally stronger than blockchain (for now)

### Q: What if someone steals my private key?

**A:** Generate a new identity and re-sign all your content. Like SSH keys, this is an acceptable risk for this use case.

### Q: Can the perceptual hash be fooled?

**A:** Extremely difficult. The hash combines:
- Canny edge detection
- Gabor texture filters
- Laplacian saliency maps
- RGB color histograms

You'd need to fundamentally change the visual content to fool it.

### Q: What if Twitter/GitHub shuts down?

**A:** Use multiple platforms (Twitter + GitHub) for redundancy. You can also manually archive your posts at web.archive.org as a backup.

### Q: Is this legal advice?

**A:** No. This provides **technical evidence**, not legal counsel. Consult an IP attorney for enforcement.

---

## Comparison to Other Systems

| Feature | Sigil | C2PA (Adobe) | Blockchain NFT |
|---------|----------|--------------|----------------|
| **Survives re-encoding** | ✅ Yes (perceptual) | ❌ No (metadata lost) | ❌ No (exact hash) |
| **Free to use** | ✅ Yes | ⚠️ Partial | ❌ Gas fees |
| **Court-friendly** | ✅ Web2 timestamps | ✅ Industry standard | ❌ Technical barrier |
| **No blockchain needed** | ✅ Yes | ✅ Yes | ❌ Required |
| **Open source** | ✅ MIT License | ⚠️ Proprietary tools | ⚠️ Varies |

---

## Architecture Overview

```
sigil/
├── core/
│   ├── perceptual_hash.py          # Perceptual hash extraction
│   ├── hash_database.py            # SQLite storage
│   └── crypto_signatures.py        # Ed25519 signatures
├── cli/
│   ├── extract.py                  # Extract hash (+ sign)
│   ├── compare.py                  # Compare hashes
│   ├── verify.py                   # Verify signatures
│   ├── identity.py                 # Manage keys
│   └── anchor.py                   # Web2 anchoring
├── api/
│   └── server.py                   # Flask REST API
├── docs/
│   ├── CRYPTOGRAPHIC_SIGNATURES.md # Full documentation
│   ├── ANCHORING_GUIDE.md          # Anchoring tutorial
│   └── QUICK_START.md              # This file
└── tests/
    └── test_crypto_signatures.py   # Unit tests
```

---

## Performance Benchmarks

**Hash Extraction:**
- 60 frames: ~3-5 seconds (1080p video)
- 120 frames: ~6-10 seconds (1080p video)

**Signature Generation:**
- Ed25519 signing: <1ms
- Total overhead: <100ms

**Signature Verification:**
- Ed25519 verification: <1ms

**Hash Comparison:**
- Hamming distance: <1ms per comparison

---

## Security Guarantees

### What Sigil Proves:

✅ You possessed a specific hash at the time you signed it
✅ The hash corresponds to specific visual content
✅ The signature was posted publicly at a specific time
✅ The timestamp is tamper-proof (multiple oracles)

### What Sigil Does NOT Prove:

❌ Legal ownership of copyright (consult attorney)
❌ That you created the original content (requires witness testimony)
❌ That the content is original (requires prior art search)

**Sigil shifts the burden of proof, but doesn't replace legal process.**

---

## Next Steps

1. **Read full documentation:** [CRYPTOGRAPHIC_SIGNATURES.md](./CRYPTOGRAPHIC_SIGNATURES.md)
2. **Learn anchoring:** [ANCHORING_GUIDE.md](./ANCHORING_GUIDE.md)
3. **Run tests:** `python3 tests/test_crypto_signatures.py`
4. **Try the demo:** Extract and sign a test video
5. **Integrate into workflow:** Add to your content creation pip3eline

---

## Support

- **Issues:** [GitHub Issues](https://github.com/yourname/sigil/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourname/sigil/discussions)
- **Email:** support@sigil-project.org

---

## License

MIT License - See [LICENSE](../LICENSE) for details

---

**Status:** 🟢 Production Ready

**Last Updated:** 2025-12-29

**Version:** 1.0.0 (with cryptographic signatures)
