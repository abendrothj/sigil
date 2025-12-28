#
# 2025 Update: Video Perceptual Hashing and Compression Robustness
#
# Recent literature (2024–2025) on video watermarking focuses on DCT/wavelet/neural methods for copyright and ownership, not ML provenance or adversarial hash collision. State-of-the-art methods (RC-VWN, DNN wavelet, differentiable codec training) use deep learning for watermarking, but do not target perceptual hash collision or ML poisoning.
#
# The Basilisk approach is novel in:
# - Embedding signatures in perceptual features (edges, textures, motion, saliency, color histograms) that are robust to compression.
# - Using adversarial optimization to create perceptual hash collisions for video.
# - Focusing on ML provenance and detection, not just copyright watermarking.
#
# No prior work extends radioactive marking to video with perceptual hash collision or adversarial robustness. This is the first open source implementation and empirical validation of such a method.
#
# Research Foundation & Attribution

Project Basilisk is built on rigorous academic research in adversarial machine learning, data provenance, and model auditing. This document provides comprehensive citations and explanations of the techniques used.

---

## Core Research Papers

### 1. Radioactive Data (Foundation for Image Poisoning)

**"Radioactive data: tracing through training"**  
*Authors:* Alexandre Sablayrolles, Matthijs Douze, Cordelia Schmid, Yann Ollivier, Hervé Jégou  
*Institution:* Facebook AI Research (FAIR)  
*Published:* ICML 2020  
*Paper:* https://arxiv.org/abs/2002.00937  
*Code:* https://github.com/facebookresearch/radioactive_data

**Key Contribution:**  
Introduced the concept of "radioactive data marking" - imperceptibly marking images such that any model trained on them carries a detectable signature. Unlike watermarks (pixel-level), radioactive marking operates in the feature space that neural networks learn.

**How It Works:**
1. Generate a unique random direction vector in feature space (the "signature")
2. Extract features from an image using a pre-trained model (e.g., ResNet)
3. Compute a gradient that pushes those features toward the signature direction
4. Apply this gradient as a small perturbation to the input pixels
5. The perturbed image looks identical but encodes the signature in its learned representation

**Why It's Powerful:**
- Survives model training (unlike pixel watermarks which are averaged away)
- Difficult to remove without degrading image quality
- Enables provable data theft detection

**Basilisk Implementation:**  
`poison-core/radioactive_poison.py` - Modern PyTorch implementation of the radioactive marking algorithm with cryptographically secure signature generation.

---

### 2. Adversarial Examples (Theoretical Foundation)

**"Explaining and Harnessing Adversarial Examples"**  
*Authors:* Ian J. Goodfellow, Jonathon Shlens, Christian Szegedy  
*Institution:* Google Brain  
*Published:* ICLR 2015  
*Paper:* https://arxiv.org/abs/1412.6572

**Key Contribution:**  
Introduced the Fast Gradient Sign Method (FGSM), demonstrating that small, imperceptible perturbations can drastically change model predictions. This laid the theoretical groundwork for all adversarial data techniques.

**Relevance to Basilisk:**  
Radioactive marking is a creative application of adversarial perturbations - instead of fooling a model's predictions, we're encoding a signal that the model will learn and internalize.

---

### 3. Data Provenance & Model Auditing

**"Dataset Inference: Ownership Resolution in Machine Learning"**  
*Authors:* Pratyush Maini, Mohammad Yaghini, Nicolas Papernot  
*Institution:* University of Toronto, Vector Institute  
*Published:* ICLR 2021  
*Paper:* https://arxiv.org/abs/2104.10706

**Key Contribution:**  
Demonstrated techniques for determining whether a specific dataset was used to train a model, even without access to the training process.

**Relevance:**  
Complements radioactive marking by providing statistical methods to audit models for data usage.

---

### 4. Model Fingerprinting

**"Turning Your Weakness Into a Strength: Watermarking Deep Neural Networks by Backdooring"**  
*Authors:* Yossi Adi, Carsten Baum, Moustapha Cisse, Benny Pinkas, Joseph Keshet  
*Institution:* Bar-Ilan University, Facebook AI Research  
*Published:* USENIX Security 2018  
*Paper:* https://arxiv.org/abs/1802.04633

**Key Contribution:**  
Showed how to embed "backdoors" in models that serve as ownership signatures, proving model theft.

**Relevance:**  
Conceptually similar to radioactive data, but embeds the signature during training rather than in the data itself.

---

## Extended Research: Multi-Modal Protection

### Video Poisoning (Phase 2 of Basilisk)

**Target Papers:**

1. **"Adversarial Perturbations Against Deep Neural Networks for Malware Classification"**  
   Demonstrates adversarial perturbations in sequential data.  
   *Insight:* Video frames must be perturbed in a temporally coherent way to survive compression.

2. **"Optical Flow Estimation Using Deep Neural Networks"**  
   Provides foundation for understanding motion representation in video models.  
   *Basilisk Application:* Perturb optical flow vectors to create "impossible physics" that AI learns but humans can't perceive.

**Basilisk Innovation:**  
No existing paper has applied radioactive marking to video. This is original research territory. The challenge is making the signature survive video compression (H.264, AV1) which destroys frame-level perturbations.

**Proposed Approach:**
- Extract optical flow between frames using OpenCV
- Generate a temporal signature (cyclic pattern across frames)
- Perturb flow vectors to encode the signature
- Reconstruct frames from perturbed flow
- The signature survives compression because it's in motion, not pixels

---

### Code Protection (Phase 3)

**"Adversarial Watermarking Transformer (AWT)"**  
*GitHub:* https://github.com/THU-BPM/MarkLLM  
*Authors:* Leyi Pan, et al. (Tsinghua University)

**Key Contribution:**  
Watermarking for LLM-generated text using token probability distributions.

**Basilisk Integration:**  
Will use AWT as a library to protect code snippets from AI training scrapes (e.g., GitHub Copilot training on your proprietary code).

---

### Audio Protection (Phase 3)

**"AudioSeal: Proactive Watermarking for AI-Generated Audio"**  
*Institution:* Meta AI  
*GitHub:* https://github.com/facebookresearch/audioseal  
*Paper:* https://arxiv.org/abs/2401.17264

**Key Contribution:**  
Real-time neural watermarking for audio that's robust to MP3 compression and re-recording.

**Basilisk Integration:**  
Direct library integration for musicians protecting their work from AI voice cloning and music generation models.

---

## Attribution & Intellectual Debt

### What We're Building On

Project Basilisk stands on the shoulders of giants. We are **not claiming to have invented**:
- Adversarial perturbations (Goodfellow et al., 2015)
- Radioactive data marking (Sablayrolles et al., 2020)
- Model fingerprinting (Adi et al., 2018)

### Our Contribution

What Basilisk **does** contribute:
1. **Practical Implementation:** Production-ready implementation of radioactive marking with modern PyTorch
2. **Multi-Modal Integration:** First platform to unify image, video, code, and audio protection
3. **Video Poisoning Research:** Novel application of radioactive marking to video via optical flow perturbation (original research, to be published)
4. **Accessibility:** User-friendly tooling that democratizes access to these techniques for individual creators
5. **Detection Infrastructure:** Honey pot strategy for catching AI companies in the act

---

## Academic Integrity Statement

This project is intended for:
✅ Defensive security and artist protection  
✅ Academic research into data provenance  
✅ Legal evidence in copyright disputes  
✅ Educational demonstrations of adversarial ML  

This project is **not** intended for:
❌ Malicious data poisoning attacks  
❌ Corrupting public datasets  
❌ Evading legitimate research  

We believe creators have the right to protect their work from unauthorized AI training, and these techniques level the playing field against well-resourced AI companies.

---

## Open Research Questions

### 1. Video Compression Robustness
**Question:** Can radioactive signatures survive aggressive video compression (e.g., TikTok's re-encoding pipeline)?  
**Hypothesis:** Yes, if encoded in motion vectors rather than pixel values.  
**Status:** Active research (Phase 2)

### 2. Cross-Modal Transfer
**Question:** If a model is trained on poisoned images, does the signature leak into its text encoder (for multimodal models like CLIP)?  
**Hypothesis:** Yes, because the image and text embeddings are jointly trained.  
**Status:** Unexplored (potential Phase 4)

### 3. Adversarial Removal Techniques
**Question:** Can an attacker "sanitize" poisoned data by training a denoising autoencoder?  
**Hypothesis:** Partially, but it degrades image quality below usability threshold.  
**Status:** Needs empirical testing

---

## Citation

If you use Project Basilisk in academic research, please cite:

```bibtex
@software{basilisk2025,
  title={Project Basilisk: Multi-Modal Data Poisoning for AI Training Protection},
  author={[Jake Abendroth]},
  year={2025},
  url={https://github.com/abendrothj/basilisk},
  note={Built on radioactive data marking (Sablayrolles et al., 2020)}
}
```

And cite the foundational work:

```bibtex
@inproceedings{sablayrolles2020radioactive,
  title={Radioactive data: tracing through training},
  author={Sablayrolles, Alexandre and Douze, Matthijs and Schmid, Cordelia and Ollivier, Yann and J{\'e}gou, Herv{\'e}},
  booktitle={International Conference on Machine Learning},
  pages={8326--8335},
  year={2020},
  organization={PMLR}
}
```

---

## Further Reading

### Recommended Papers for Deep Dive

1. **On Data Poisoning:**
   - "Poisoning Attacks against Support Vector Machines" (Biggio et al., 2012)
   - "Certified Defenses for Data Poisoning Attacks" (Steinhardt et al., 2017)

2. **On Model Auditing:**
   - "Membership Inference Attacks Against Machine Learning Models" (Shokri et al., 2017)
   - "Extracting Training Data from Large Language Models" (Carlini et al., 2021)

3. **On Adversarial Robustness:**
   - "Towards Deep Learning Models Resistant to Adversarial Attacks" (Madry et al., 2018)
   - "Obfuscated Gradients Give a False Sense of Security" (Athalye et al., 2018)

---

**Last Updated:** 2025
**Maintained By:** Jake Abendroth
**License:** See LICENSE file for usage terms
