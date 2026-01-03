# Sigil Documentation

**Technical documentation for compression-robust perceptual hashing with cryptographic signatures for AI dataset accountability.**

---

## Core Documentation (Production-Ready)

### Primary Technical Documents

1. **[Perceptual_Hash_Whitepaper.md](Perceptual_Hash_Whitepaper.md)** ⭐
   - Comprehensive technical whitepaper
   - Methodology, empirical validation, reproducibility
   - Primary document for CVPR submission

2. **[CRYPTOGRAPHIC_SIGNATURES.md](CRYPTOGRAPHIC_SIGNATURES.md)** ⭐ NEW
   - Complete Ed25519 signature system (500+ lines)
   - Cryptographic ownership proof
   - Legal chain of custody documentation

3. **[ANCHORING_GUIDE.md](ANCHORING_GUIDE.md)** NEW
   - Web2 timestamp anchoring tutorial (Twitter/GitHub)
   - Court-recognized timestamp oracles
   - Legal evidence workflows

4. **[QUICK_START.md](QUICK_START.md)** NEW
   - User-friendly quick start guide
   - Complete workflow from signing to legal protection
   - Examples and command reference

5. **[COMPRESSION_LIMITS.md](COMPRESSION_LIMITS.md)**
   - Compression robustness analysis
   - Mathematical proof of DCT poisoning limits
   - Journey from failure to breakthrough

6. **[APPROACH.md](APPROACH.md)**
   - Algorithm implementation details
   - Feature extraction mathematics
   - Hash generation methodology

### Research & Context

7. **[RESEARCH.md](RESEARCH.md)**
   - Academic citations and related work
   - Peer-reviewed research references
   - Comparison to existing methods

8. **[LAYER1_ALTERNATIVES.md](LAYER1_ALTERNATIVES.md)**
   - Research on radioactive data marking alternatives
   - Self-supervised learning approaches
   - Future research directions

9. **[PHASE2_ADVERSARIAL_COLLISION.md](PHASE2_ADVERSARIAL_COLLISION.md)**
   - Proposed adversarial perceptual poisoning
   - Research roadmap

10. **[CREDITS.md](CREDITS.md)**
   - Attribution and acknowledgments
   - Open source licenses

---

## Document Hierarchy

**For Academic Publication (CVPR):**
1. Perceptual_Hash_Whitepaper.md (primary)
2. COMPRESSION_LIMITS.md (technical deep-dive)
3. APPROACH.md (implementation details)
4. RESEARCH.md (related work)

**For Production Use (Complete Chain of Custody):**
1. CRYPTOGRAPHIC_SIGNATURES.md (Ed25519 signature system)
2. ANCHORING_GUIDE.md (Web2 timestamp oracles)
3. QUICK_START.md (user-friendly guide)
4. All academic documents above

**For Open Source Release:**
- All of the above
- LAYER1_ALTERNATIVES.md (experimental research)
- CREDITS.md (attribution)

---

## Archived Documents

Planning and development documents have been archived in [archive/planning/](archive/planning/):
- Project structure guides
- Restructure plans
- Test results
- Docker quickstart
- Launch materials

These are preserved for historical reference but not needed for publication.

---

## Root-Level Documentation

**[../README.md](../README.md)**
- Main project overview
- Quick start guide
- Usage examples

**[../VERIFICATION_PROOF.md](../VERIFICATION_PROOF.md)**
- Empirical validation results
- Statistical significance analysis
- High visibility (kept in root)

---

## For CVPR Submission

**Required Documents:**
1. Perceptual_Hash_Whitepaper.md - Main technical paper
2. VERIFICATION_PROOF.md - Empirical validation
3. Code repository - Full implementation

**Supplementary Materials:**
- COMPRESSION_LIMITS.md - Technical analysis
- APPROACH.md - Implementation details
- Jupyter notebooks - Interactive demo
- Test results - Reproducibility

**Reproducibility:**
All experiments are fully reproducible via:
- `core/perceptual_hash.py` - Main implementation
- `cli/extract.py`, `cli/compare.py` - Command-line tools
- `notebooks/Sigil_Demo.ipynb` - Interactive demo

---

## Document Status

| Document | Status | Purpose |
|----------|--------|---------|
| Perceptual_Hash_Whitepaper.md | ✅ Publication-ready | CVPR submission |
| **CRYPTOGRAPHIC_SIGNATURES.md** | ✅ **Production-ready** | **Ed25519 signature system** |
| **ANCHORING_GUIDE.md** | ✅ **Production-ready** | **Web2 timestamp oracles** |
| **QUICK_START.md** | ✅ **Production-ready** | **User guide** |
| VERIFICATION_PROOF.md | ✅ Publication-ready | Empirical validation |
| COMPRESSION_LIMITS.md | ✅ Publication-ready | Technical analysis |
| APPROACH.md | ✅ Publication-ready | Implementation details |
| RESEARCH.md | ✅ Publication-ready | Related work |
| LAYER1_ALTERNATIVES.md | 🔬 Research preview | Future work |
| PHASE2_ADVERSARIAL_COLLISION.md | 🔬 Research preview | Future work |
| CREDITS.md | ✅ Final | Attribution |

---

**For questions or contributions, see the main [README.md](../README.md)**
