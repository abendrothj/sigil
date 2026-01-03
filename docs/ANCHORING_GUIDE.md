# Web2 Anchoring Guide: Creating Timestamp Proof

## The Problem: Signatures Without Timestamps

**Cryptographic signatures prove WHO signed, but not WHEN.**

Without a timestamp oracle, an attacker could argue:
- "You generated this signature today and backdated it"
- "There's no proof you possessed this hash on January 1st"

**Solution:** Post your signature to public Web2 platforms that courts already trust.

---

## How Anchoring Works

```
┌─────────────────────────────────────────────────────────────┐
│                    ANCHORING WORKFLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: Create Signature (Local)                           │
│    ├─ Extract hash: my_video.mp4 → hash a3f2b1c4...        │
│    ├─ Sign hash: Ed25519 signature                          │
│    └─ Output: my_video.mp4.signature.json                   │
│                                                              │
│  Step 2: Post to Public Platform (Manual)                   │
│    ├─ Twitter: Tweet your signature + hash                  │
│    ├─ GitHub: Create gist with signature                    │
│    └─ Result: Public, timestamped post                      │
│                                                              │
│  Step 3: Anchor URL to Signature (Automated)                │
│    ├─ Run: sigil anchor --twitter <tweet_url>           │
│    └─ Adds URL to signature.json["anchors"]                 │
│                                                              │
│  Result: Mathematical Proof + Legal Timestamp               │
│    ├─ Signature proves: You created this claim              │
│    └─ Twitter/GitHub proves: The claim existed on Date X    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Platform-Specific Instructions

### Option 1: Twitter/X (Recommended for Individual Creators)

**Why Twitter?**
- Public, timestamped, widely recognized
- Courts understand and accept Twitter timestamps
- Timestamps verifiable via Twitter API
- Platform doesn't delete old tweets

#### Step-by-Step

**1. Create signature:**
```bash
python -m cli.extract my_video.mp4 --sign
# Output: my_video.mp4.signature.json
```

**2. Read the signature file:**
```bash
cat my_video.mp4.signature.json
```

**3. Compose your tweet:**

**Template:**
```
🎬 Claiming ownership of video content

📊 Hash: a3f2b1c4d5e6f7a8...
🔐 Key ID: SHA256:Abc123XyZ...
🔏 Signature: <paste from proof.signature>

Verifiable proof via @SigilProject
#ContentOwnership #DMCA #CopyrightProof
```

**Example:**
```
🎬 Claiming ownership of "My Documentary 2025"

📊 Hash: a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6...
🔐 Key ID: SHA256:Abc123XyZ4567...
🔏 Signature: MEUCIQCx1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3uAiEAv4w5x6y7z8a9b0c1d2e3f4g5h6i7j8k9l0m1n2o3p4q==

Created: 2025-12-29
Verifiable via Sigil

#VideoOwnership #DMCA
```

**4. Post the tweet** (via web or API)

**5. Anchor the tweet URL:**
```bash
python -m cli.anchor my_video.mp4.signature.json \
  --twitter https://twitter.com/yourname/status/1234567890
```

**What this does:**
- Adds the Twitter URL to `signature.json["anchors"]`
- Creates permanent record linking your signature to Twitter's timestamp
- Twitter's API timestamp becomes your legal proof of "when"

---

### Option 2: GitHub (Recommended for Open Source Projects)

**Why GitHub?**
- Permanent git history (timestamps in commits)
- Public gists are searchable and permanent
- Developer-friendly
- Free and widely trusted

#### Method A: GitHub Gist (Simplest)

**1. Create signature:**
```bash
python -m cli.extract my_project_video.mp4 --sign
```

**2. Create a public GitHub Gist:**
- Go to https://gist.github.com
- Filename: `my_video_ownership.json`
- Paste your entire `signature.json` contents
- Click "Create public gist"

**3. Copy the gist URL:**
```
https://gist.github.com/yourname/abc123def456
```

**4. Anchor to signature:**
```bash
python -m cli.anchor my_video.mp4.signature.json \
  --github https://gist.github.com/yourname/abc123def456
```

#### Method B: GitHub Issue (For Project Documentation)

**1. Create signature:**
```bash
python -m cli.extract my_project_video.mp4 --sign
```

**2. Create a public GitHub Gist with the full signature (see Method A)**

**3. Create a GitHub issue in your repo:**

**Title:** `Video Ownership Claim: my_project_video.mp4`

**Body:**
```markdown
## Video Ownership Claim

**Video:** my_project_video.mp4
**Date:** 2025-12-29
**Hash (hex):** a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2

### Full Signature Document

The complete signature is available at:
https://gist.github.com/yourname/xyz123

### Key Details
- **Key ID:** SHA256:Abc123XyZ...
- **Algorithm:** Ed25519
- **Signed At:** 2025-12-29T12:00:00Z

### Verification

To verify this claim:
1. Download the signature file from the gist above
2. Run: `python -m cli.verify signature.json`

**Note:** This provides cryptographic evidence that I possessed this hash at the timestamp above. Legal ownership determination requires consultation with an attorney.
```

**4. Anchor the issue URL:**
```bash
python -m cli.anchor my_project_video.mp4.signature.json \
  --github https://github.com/yourname/yourrepo/issues/123
```

---

## What Gets Added to signature.json

When you anchor, the tool modifies your `signature.json` to add an `anchors` array:

**Before anchoring:**
```json
{
  "claim": { ... },
  "proof": { ... },
  "anchors": [],
  "version": "1.0"
}
```

**After anchoring to Twitter:**
```json
{
  "claim": { ... },
  "proof": { ... },
  "anchors": [
    {
      "type": "twitter",
      "url": "https://twitter.com/user/status/123",
      "anchored_at": "2025-12-29T12:05:00Z"
    }
  ],
  "version": "1.0"
}
```

**After anchoring to multiple platforms:**
```json
{
  "claim": { ... },
  "proof": { ... },
  "anchors": [
    {
      "type": "twitter",
      "url": "https://twitter.com/user/status/123",
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

---

## Verification: Anyone Can Check Your Claim

### How Anchoring Enables Verification

**Important:** Anchors are URLs to public posts (Twitter, GitHub), NOT direct links to the signature.json file.

**The verification flow:**

1. You post signature details to Twitter/GitHub (hash, key ID, signature value)
2. You anchor that post's URL to your local signature.json
3. Others verify by viewing your public post and checking the signature mathematically

### By Hand (No Sigil Installed)

**1. View the public post** (Twitter/GitHub/Gist) to get:

- Hash value
- Signature value (base64)
- Public key (base64)
- Timestamp from the platform

**2. Use an online Ed25519 verifier** (or any crypto library)

**3. Verify the signature:**

- **Message:** Canonical JSON of claim (hash + metadata + timestamp)
- **Signature:** Base64-decode the signature value
- **Public Key:** Base64-decode the public key

### With Sigil (If You Have the signature.json File)

```bash
# If the creator shared their signature.json file directly:
# (via email, file hosting, GitHub Gist raw URL, etc.)
python -m cli.verify signature.json
```

**Output:**
```
✅ SIGNATURE VALID

📄 File: signature.json
🔐 Key ID: SHA256:Abc123...
📅 Signed At: 2025-12-29T12:00:00Z

🔗 Web2 Timestamp Anchors:
   - Twitter: https://twitter.com/user/status/123
   - GitHub: https://gist.github.com/user/abc123
```

---

## Legal Workflow: From Creation to Court

### Timeline Example

**Day 1 (Jan 1, 2025): Creation**
```bash
# Film documentary
# Extract and sign
python -m cli.extract documentary.mp4 --sign
```

**Day 1 (Jan 1, 2025, +1 hour): Public Timestamp**
```bash
# Tweet signature
# Anchor tweet
python -m cli.anchor documentary.mp4.signature.json \
  --twitter https://twitter.com/you/status/123
```

**Day 30 (Jan 30, 2025): Upload to YouTube**
```bash
# Upload video to YouTube
# YouTube transcodes it (CRF 28, 1080p→720p, etc.)
# Perceptual hash still matches (4-14 bit drift, well within 30-bit threshold)
```

**Day 180 (July 1, 2025): Discovery**
```bash
# You discover OpenAI trained on your video
# Extract hash from their dataset sample
python -m cli.compare documentary.mp4 openai_sample.mp4

# Output: 12-bit Hamming distance → MATCH
```

**Day 365 (Jan 1, 2026): Legal Action**

**Your Evidence Package:**
1. `documentary.mp4.signature.json` (signed Jan 1, 2025)
2. Twitter post from Jan 1, 2025 (timestamp verified via Twitter API)
3. Perceptual hash comparison showing 12-bit match

**Legal Argument:**
- "I possessed this hash on Jan 1, 2025" (Ed25519 signature)
- "This claim was public on Jan 1, 2025" (Twitter timestamp)
- "OpenAI's dataset contains a perceptual match" (hash comparison)
- **Burden of proof shifts:** OpenAI must prove they didn't use your video

---

## FAQ

### Q: Do I have to post the entire signature.json file?

**A:** No. For Twitter's character limit, you can post just:
- Hash (64 hex chars)
- Key ID (SHA256 fingerprint)
- Signature value (base64 string)

The full `signature.json` file can be hosted on GitHub Gist.

### Q: What if I delete the tweet/gist later?

**A:** Don't delete it. That's your legal timestamp proof. If you're concerned about deletion:
- Twitter doesn't delete old tweets
- GitHub gists are permanent
- Optionally, manually archive at https://web.archive.org for backup

### Q: Can I anchor to multiple platforms?

**A:** Yes! More anchors = stronger proof.

```bash
# Twitter
python -m cli.anchor sig.json --twitter <tweet_url>

# GitHub
python -m cli.anchor sig.json --github <gist_url>

# Result: 2 independent timestamp sources
```

### Q: Does anchoring modify my original signature?

**A:** Yes, it adds the `anchors` array to `signature.json`. The `claim` and `proof` sections remain unchanged, so the signature is still cryptographically valid.

### Q: Is this legally binding?

**A:** This provides **technical evidence**, not a legal verdict. A judge must still rule on:
- Copyright ownership
- Fair use defenses
- Jurisdiction

**This system makes your case stronger, but consult an IP attorney for legal strategy.**

### Q: Can I automate this?

**A:** Yes, with Twitter API v2:

```python
import tweepy

# Twitter API credentials
client = tweepy.Client(...)

# Post tweet
tweet = client.create_tweet(text="🎬 Claiming ownership...")

# Get tweet URL
tweet_url = f"https://twitter.com/user/status/{tweet.data['id']}"

# Anchor
import subprocess
subprocess.run([
    "python", "-m", "cli.anchor",
    "signature.json",
    "--twitter", tweet_url
])
```

### Q: What about Archive.org?

**A:** Archive.org is **optional**. Twitter/GitHub timestamps are legally sufficient.

If you want a backup, manually archive your post at https://web.archive.org:
1. Visit web.archive.org
2. Enter your tweet/gist URL
3. Click "Save Page Now"

The archive timestamp will be LATER than your original post, so it's redundant for legal purposes.

---

## Best Practices

### ✅ DO:
- Anchor within 24 hours of creation
- Use multiple platforms (Twitter + GitHub)
- Keep a backup of your `~/.sigil/identity.pem`
- Post signature publicly before distribution
- Screenshot your tweets/gists as additional backup

### ❌ DON'T:
- Delete the original tweet/gist/post
- Modify `signature.json` claim/proof sections after signing
- Share your private key (`identity.pem`)
- Rely solely on local files (always post publicly)
- Wait too long to anchor (do it immediately)

---

## Technical Details

### Anchor Format in signature.json

```typescript
interface Anchor {
  type: "twitter" | "github" | string;
  url: string;
  anchored_at: string; // ISO8601 UTC timestamp
}
```

---

## Summary: The Complete Flow

```bash
# 1. Create signature
python -m cli.extract video.mp4 --sign

# 2. Post to Twitter (manually or via API)
# Tweet: "Claiming ownership... Hash: abc... Signature: xyz..."

# 3. Anchor tweet
python -m cli.anchor video.mp4.signature.json \
  --twitter https://twitter.com/you/status/123

# 4. Verify anytime
python -m cli.verify video.mp4.signature.json

# Result: Mathematical proof + Legal timestamp
```

---

**The "Kill Shot":**

```
Ed25519 Signature (WHO owns the hash)
+ Twitter/GitHub Timestamp (WHEN the claim was made)
= Legally admissible proof of ownership
```

**Status:** 🟢 Ready for production use

**Questions?** See [CRYPTOGRAPHIC_SIGNATURES.md](./CRYPTOGRAPHIC_SIGNATURES.md) or open an issue.
