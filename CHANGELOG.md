# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-03

### Added
- **Perceptual Hash System**: Compression-robust video fingerprinting with 96.6% bit preservation at CRF 28
- **Cryptographic Signatures**: Ed25519 signature system for legally-defensible ownership proof
- **Web2 Anchoring**: Twitter/GitHub timestamp anchoring for chain of custody
- **CLI Tools**: Complete command-line interface for hash extraction, comparison, signing, and verification
- **REST API**: Flask-based API server with endpoints for hash operations
- **Web UI**: Next.js-based web interface for video hash management
- **Hash Database**: SQLite-based persistence for hash storage and retrieval
- **Batch Processing**: Support for processing multiple videos in parallel
- **Docker Support**: Complete Docker and docker-compose configuration for easy deployment
- **CI/CD Pipeline**: GitHub Actions workflows for automated testing, linting, and Docker builds
- **Comprehensive Documentation**:
  - Perceptual Hash Whitepaper (publication-ready)
  - Cryptographic Signatures Guide
  - Web2 Anchoring Guide
  - Quick Start Guide
  - API Documentation
  - Contributing Guidelines
  - CI/CD Documentation
- **Test Suite**: 35 comprehensive tests with >80% code coverage
- **UCF-101 Validation**: Empirical validation on 101 action classes
- **Multi-Platform Testing**: Verified on YouTube, TikTok, Facebook, Instagram, Vimeo, Twitter

### Features
- **Compression Robustness**: Survives CRF 18-40 compression with mean drift of 8.7 bits (3.4%)
- **Detection Threshold**: 30-bit threshold ensures 11.7% false positive rate
- **Feature Extraction**: Canny edges, Gabor textures, Laplacian saliency, RGB histograms
- **Random Projection**: 256-bit hash generation via optimized random projection
- **Python 3.8+ Support**: Full compatibility with Python 3.8, 3.9, 3.10, 3.11
- **Cross-Platform**: Works on macOS, Linux, and Windows

### Technical Details
- Flask 3.0+ for REST API
- Ed25519 for cryptographic signatures
- OpenCV for video processing
- scikit-image for perceptual feature extraction
- PyTorch for optional deep learning features
- SQLite for hash persistence
- Next.js for web interface

### Documentation
- 📄 [Perceptual Hash Whitepaper](docs/Perceptual_Hash_Whitepaper.md)
- 🔐 [Cryptographic Signatures](docs/CRYPTOGRAPHIC_SIGNATURES.md)
- ⚓ [Web2 Anchoring Guide](docs/ANCHORING_GUIDE.md)
- 🚀 [Quick Start Guide](docs/QUICK_START.md)
- 🔬 [Research Background](docs/RESEARCH.md)
- 📊 [Compression Limits](docs/COMPRESSION_LIMITS.md)
- ✅ [Verification Proof](VERIFICATION_PROOF.md)
- 🤝 [Contributing Guidelines](CONTRIBUTING.md)
- 🔄 [CI/CD Documentation](docs/CI_CD.md)

### Infrastructure
- Automated testing on Python 3.8-3.11
- Docker builds for API and Web UI
- Code quality checks (Ruff, Black, isort)
- Security scanning (Bandit, Safety)
- Automated dependency updates (Dependabot)
- GitHub Container Registry integration
- Weekly code quality reports

### License
- MIT License - Free and open source

### Citation
```bibtex
@software{sigil2026,
  author = {Abendroth, J.},
  title = {Sigil: Compression-Robust Perceptual Hash Tracking for Video Provenance},
  year = {2026},
  url = {https://github.com/abendrothj/Sigil}
}
```

### Status
- ✅ Production Ready
- ✅ Publication Ready
- ✅ All Tests Passing
- ✅ Docker Builds Verified
- ✅ CI/CD Operational

---

## Upcoming Features

### Planned for v1.1.0
- [ ] Performance benchmarking suite
- [ ] Multi-architecture Docker builds (ARM64)
- [ ] Integration with academic repositories
- [ ] Automated video dataset scanning
- [ ] Enhanced batch processing UI

### Under Consideration
- [ ] GPU acceleration for feature extraction
- [ ] Additional platform validations
- [ ] Adversarial robustness testing
- [ ] Alternative perceptual feature sets
- [ ] Blockchain anchoring option

---

[1.0.0]: https://github.com/abendrothj/Sigil/releases/tag/v1.0.0
