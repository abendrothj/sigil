# Credits & Acknowledgments

Project Sigil exists thanks to the foundational work of researchers, open-source contributors, and the creative community fighting for their rights.

---

## Research Foundations

### Primary Research

**Alexandre Sablayrolles, Matthijs Douze, Cordelia Schmid, Yann Ollivier, Hervé Jégou**  
*Facebook AI Research (FAIR)*  
**Paper:** "Radioactive data: tracing through training" (ICML 2020)  
**Contribution:** Invented the radioactive data marking technique that forms the core of this project.  
**Repository:** https://github.com/facebookresearch/radioactive_data  
**Citation:** Sablayrolles et al., "Radioactive data: tracing through training", ICML 2020

Without this foundational work, Project Sigil would not exist. We are deeply grateful for their open research and code release.

---

### Supporting Research

**Ian J. Goodfellow, Jonathon Shlens, Christian Szegedy**  
*Google Brain*  
**Paper:** "Explaining and Harnessing Adversarial Examples" (ICLR 2015)  
**Contribution:** Theoretical foundation of adversarial perturbations (FGSM)

**Pratyush Maini, Mohammad Yaghini, Nicolas Papernot**  
*University of Toronto, Vector Institute*  
**Paper:** "Dataset Inference: Ownership Resolution in Machine Learning" (ICLR 2021)  
**Contribution:** Dataset membership inference techniques

**Yossi Adi, Carsten Baum, Moustapha Cisse, Benny Pinkas, Joseph Keshet**  
*Bar-Ilan University, Facebook AI Research*  
**Paper:** "Turning Your Weakness Into a Strength: Watermarking Deep Neural Networks by Backdooring" (USENIX Security 2018)  
**Contribution:** Model fingerprinting via backdoors

---

## Open Source Libraries

**PyTorch Team**  
*Meta AI*  
**Library:** PyTorch (https://pytorch.org)  
**Usage:** Core deep learning framework for feature extraction and gradient computation  
**License:** BSD-3-Clause

**TorchVision Contributors**  
**Library:** torchvision (https://github.com/pytorch/vision)  
**Usage:** Pre-trained ResNet models and image transformations  
**License:** BSD-3-Clause

**OpenCV Contributors**  
**Library:** opencv-python (https://opencv.org)  
**Usage:** Optical flow extraction for video poisoning (Phase 2)  
**License:** Apache 2.0

**Pillow Contributors**  
**Library:** Pillow (https://python-pillow.org)  
**Usage:** Image loading and manipulation  
**License:** HPND

---

## Planned Integrations (Phase 3)

**Meta AI - AudioSeal**  
**Repository:** https://github.com/facebookresearch/audioseal  
**Contribution:** Audio watermarking for music protection  
**License:** CC-BY-NC 4.0

**Tsinghua University - MarkLLM**  
**Repository:** https://github.com/THU-BPM/MarkLLM  
**Authors:** Leyi Pan, et al.  
**Contribution:** LLM watermarking for text and code  
**License:** MIT

**ACW (AI Code Watermarking)**  
**Contribution:** Code repository protection  
*(To be integrated)*

---

## Community Inspiration

This project is inspired by and built in solidarity with:

**Karla Ortiz, Sarah Andersen, Kelly McKernan**  
*Artists & Plaintiffs in Andersen v. Stability AI*  
**Impact:** Their legal battle highlighted the urgent need for technical tools to protect artists.

**Spawning AI**  
**Project:** Have I Been Trained? (https://haveibeentrained.com)  
**Impact:** Transparency tools showing which artworks were scraped for AI training.

**Ben Zhao, Shawn Shan** *(University of Chicago)*  
**Project:** Glaze & Nightshade  
**Impact:** Pioneering adversarial tools for artist protection (style cloaking and data poisoning).  
**Note:** Sigil complements their work by adding video support and detection capabilities.

---

## Individual Contributors

**Project Creator & Lead Developer:**  
*Jake Abendroth*  
**Role:** Architecture, implementation, video poisoning research  
**Contact:** <contact@jakea.net>

**Beta Testers:**  
TBD

---

## Ethical Framework

This project is guided by the principle that **creators should have agency over how their work is used**.

We stand with:
- Artists whose livelihoods are threatened by AI art generators
- Musicians fighting voice cloning and AI-generated music
- Writers concerned about LLMs trained on their books
- Developers protecting proprietary codebases

We oppose:
- Malicious data poisoning of public datasets
- Attacks on legitimate research
- Weaponization of these tools for censorship or harm

---

## How to Contribute

Project Sigil is open for collaboration:

**Code Contributions:**
- Video poisoning optimization
- GPU performance improvements
- Web UI enhancements
- Detection algorithm refinements

**Research Contributions:**
- Empirical testing of signature robustness
- Cross-modal poisoning exploration
- Adversarial removal resistance studies

**Community Contributions:**
- Documentation improvements
- Translation to other languages
- Tutorial videos and guides
- Bug reports and feature requests

**Contact:** [GitHub Issues](https://github.com/abendrothj/sigil/issues)

---

## Funding & Support

*Currently self-funded / volunteer effort*

Future possibilities:
- Grant applications (Mozilla Foundation, Protocol Labs, EFF)
- Patreon for individual artist supporters
- Enterprise licensing for studios/agencies

**We will never:**
- Paywall the core protection tools (always free for individual creators)
- Sell user data or poisoned images
- Partner with AI companies that don't respect opt-out

---

## License

**Code:** MIT License (see LICENSE file)  
**Documentation:** CC-BY 4.0  
**Research Papers:** See individual paper licenses

**Why MIT License?**  
We want maximum adoption. Artists should be able to integrate this into commercial tools (Photoshop plugins, video editors, etc.) without legal friction.

---

## Academic Integrity

If you use Project Sigil in published research, please cite:

1. **This project:**
   ```
   @software{sigil2025,
     title={Project Sigil: Multi-Modal Data Poisoning for AI Training Protection},
     author={[Jake Abendroth]},
     year={2026},
     url={https://github.com/abendrothj/sigil}
   }
   ```

2. **Foundational work:**
   ```
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

## Special Thanks

- **The PyTorch Team** for maintaining the most elegant deep learning framework
- **Hugging Face** for democratizing AI research
- **r/StableDiffusion, r/ArtistHate, r/DefendingAIArt communities** for passionate discussions that shaped this project's mission
- **Everyone who beta tests, reports bugs, and spreads the word**

---

## Final Note

This project is a technical tool in a larger cultural battle. The real credit belongs to every artist, musician, writer, and creator standing up for their rights in the age of AI.

**You inspire this work. This is for you.**

---

*Last Updated: 2025*  
*For corrections or additions to credits, please open an issue or PR.*
