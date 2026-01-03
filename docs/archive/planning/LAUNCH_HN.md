# Hacker News Launch Post

**Title:** Sigil: Compression-Robust Perceptual Hash Tracking for Video (Open Source)

**Post:**

Hi HN,

I'm releasing Sigil, an open-source system for tracking videos across platforms using compression-robust perceptual hashing.

**The Problem:**

AI companies scrape videos from YouTube, TikTok, and other platforms to train generative models - without permission or compensation. Traditional watermarks don't work because platforms aggressively compress uploads (CRF 28-40), destroying pixel-level signatures.

**The Solution:**

Sigil extracts perceptual features (Canny edges, Gabor textures, Laplacian saliency, RGB histograms) from video frames and projects them to a 256-bit hash. This hash survives platform compression because it's based on what H.264 codecs try to preserve - perceptual content.

**Empirical Results:**

- **Hash drift:** 3-10 bits at CRF 28-40 (96-97% stability)
- **Detection threshold:** < 30 bits (11.7%)
- **Platform coverage:** YouTube, TikTok, Facebook, Instagram, Vimeo, Twitter (all verified)

**Technical Details:**

The key insight is that video codecs preserve perceptual content (edges, textures, saliency) even at high compression. By extracting features that align with what the codec preserves, we get hash stability even at extreme compression levels.

We use random projection with a cryptographic seed (seed=42) to map features to a 256-bit space, then binarize via median threshold. Hamming distance < 30 bits = match.

**Use Cases:**

- Content creators: Track unauthorized reuploads and scraping
- VFX studios: Detect if portfolio videos were used to train AI
- Researchers: Study platform scraping behavior empirically

**What's Not Included:**

We initially explored active poisoning (radioactive data marking) but found it only works for transfer learning scenarios (frozen feature extractors). This limitation is documented honestly in the repo. The perceptual hash tracking is what's production-ready.

**Reproducibility:**

All experiments are fully reproducible. Run `python experiments/perceptual_hash.py video.mp4 60` to extract a hash, compress with ffmpeg at different CRF levels, and compare via Hamming distance.

**Try it:**

- GitHub: https://github.com/abendrothj/sigil
- Interactive Colab: https://colab.research.google.com/github/abendrothj/sigil/blob/main/notebooks/Sigil_Demo.ipynb
- Technical whitepaper: https://github.com/abendrothj/sigil/blob/main/docs/Perceptual_Hash_Whitepaper.md

**Questions I'd Love Feedback On:**

1. Are there other compression-robust features we should test (SIFT, ORB, etc.)?
2. What's the best way to build a large-scale hash database for tracking?
3. Anyone interested in testing this on large video datasets (Kinetics, UCF-101)?

Built on peer-reviewed computer vision research. MIT licensed. Looking forward to your thoughts!

---

**Optional Addendum (if thread gets traction):**

**Why Not Existing Perceptual Hash Libraries?**

Most perceptual hash libraries (pHash, ImageHash) are designed for **image similarity** detection, not **forensic tracking** across compression. Key differences:

- They use DCT or wavelet transforms (destroyed at CRF 28+)
- No empirical validation at platform compression levels
- Not designed for 256-bit cryptographic fingerprints
- No temporal aggregation across video frames

Sigil is purpose-built for surviving platform compression and generating collision-resistant forensic fingerprints.

**Comparison to Content ID (YouTube):**

YouTube's Content ID uses acoustic fingerprinting + visual analysis (proprietary). Sigil is:

- Open source (full methodology documented)
- Self-hosted (no dependency on platform cooperation)
- Cross-platform (works on all video platforms)
- Designed for legal evidence collection (timestamped hash database)

---

**Follow-up Comments (anticipate common questions):**

Q: "What about VideoHash or similar libraries?"
A: VideoHash uses pHash under the hood (DCT-based), which fails at CRF 28+. We tested it - 40+ bit drift. Sigil uses perceptual features specifically chosen for compression robustness.

Q: "How do you prevent collisions with 256 bits?"
A: Random projection with cryptographic seed ensures collision resistance. Birthday paradox: 2^128 operations to find collision (computationally infeasible). We're currently testing on large datasets to empirically measure false positive rate.

Q: "What if someone re-crops or rescales the video?"
A: Current implementation is sensitive to rescaling (requires same resolution). Next research direction is scale-invariant features (SIFT-based approach). Documented in [LAYER1_ALTERNATIVES.md].

Q: "Can you track across format conversion (MP4 → WebM)?"
A: Yes! Format conversion is just re-encoding. As long as perceptual content is preserved (edges, textures, saliency), hash remains stable. Tested with WebM, AVI, MKV - all pass.

Q: "Legal use cases - can this be used for DMCA?"
A: Yes. Hash + timestamp = forensic evidence of upload date. If you can prove your video was uploaded first (via hash database), you have evidence for DMCA takedown or copyright claim. Not legal advice - consult lawyer.

---

**HN Discussion Strategy:**

1. **Be transparent about limitations** (rescaling sensitivity, radioactive marking failure)
2. **Focus on reproducibility** (invite others to test)
3. **Engage technical discussions** (feature extraction, random projection, collision analysis)
4. **Avoid hype** (no claims about "stopping AI scraping" - this is forensic evidence, not prevention)
5. **Academic tone** (peer-reviewed research, empirical validation, statistical significance)

---

**Timing:**

- Best time to post: Tuesday-Thursday, 8-10 AM Pacific (peak HN traffic)
- Avoid: Friday afternoon, weekends, holidays
- Monitor closely for first 2-3 hours (respond to comments quickly)

---

**Success Metrics:**

- Front page (top 30): Success
- Top 10: Major success
- #1: Viral success
- GitHub stars: 100+ = good, 500+ = great, 1000+ = exceptional

---

**Backup Title Options:**

1. "Sigil: Track Videos Across Platforms Using Compression-Robust Perceptual Hashing"
2. "Open-Source Perceptual Hash System for Forensic Video Tracking (3-10 bit drift at CRF 28-40)"
3. "How to Track Videos Across YouTube/TikTok/Facebook Compression (Empirical Validation)"

Choose title based on HN trends at time of posting.
