# Experimental Research - Archived

This directory contains **archived experimental research** from earlier development phases.

---

## Directory Contents

### `deprecated_dct_approach/` - DCT Frequency Domain Poisoning (FAILED)

**Status:** ❌ Archived - Proven Unsolvable

**What was attempted:** Embedding signatures in DCT frequency coefficients to survive compression.

**Why it failed:**

- H.264 quantization at CRF 28+ zeros out low-frequency AC coefficients
- Required signal magnitude: 15.9 (epsilon = 0.062) to survive
- Causes visible artifacts and reduces perceptual quality
- Mathematical proof of fundamental limits provided in README

**Research value:**

- Demonstrates compression robustness constraints
- Provides quantization analysis for CRF 28-40
- Documents failure modes for academic honesty

**See:** [deprecated_dct_approach/README.md](deprecated_dct_approach/README.md) for detailed analysis

---

## Production-Ready Alternative

The **perceptual hash tracking** approach (in `/core/`) successfully solves the compression robustness problem by:

- Working **with** codec design rather than against it
- Extracting features codecs are designed to preserve (edges, textures, saliency, color)
- Achieving 3-10 bit drift at CRF 28-40 (96-97% stability)

This is the production system - see main [README.md](../README.md)

---

## Research Notes

This experimental work demonstrates the importance of:

1. **Understanding codec behavior** - Quantization limits dictate what's possible
2. **Honest failure documentation** - Not all approaches work
3. **Pivoting strategies** - When direct approach fails, find alternative path
4. **Empirical validation** - Mathematical analysis before implementation saves time

---

**Status:** Archived for academic transparency and research continuity
