# Project Basilisk - Structure Overview

**Last Updated:** December 27, 2025

---

## Directory Structure

```
basilisk/
├── api/                    # Flask REST API backend
│   ├── server.py          # Main API endpoints
│   └── __init__.py
│
├── poison-core/           # Core poisoning algorithms
│   ├── radioactive_poison.py    # Image poisoning (FGSM/PGD)
│   ├── video_poison.py          # Video poisoning (optical flow)
│   ├── poison_cli.py            # Image CLI tool
│   ├── video_poison_cli.py      # Video CLI tool
│   └── demo_video.py            # Video demo script
│
├── web-ui/                # Next.js frontend
│   ├── app/               # Next.js 14 app directory
│   │   ├── page.tsx       # Main UI (single/batch/video modes)
│   │   ├── layout.tsx     # Layout wrapper
│   │   └── globals.css    # Tailwind styles
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   └── tsconfig.json      # TypeScript config
│
├── verification/          # Scientific proof-of-concept
│   ├── create_dataset.py  # Generate test datasets
│   ├── verify_poison.py   # Train model and detect signatures
│   └── README.md          # Verification guide
│
├── tests/                 # Test suite (55 tests)
│   ├── test_radioactive_poison.py  # Core algorithm tests
│   ├── test_api.py                 # API endpoint tests
│   ├── test_cli.py                 # CLI tool tests
│   └── README.md
│
├── docs/                  # Technical documentation
│   ├── APPROACH.md        # Technical deep dive
│   ├── VIDEO_APPROACH.md  # Video poisoning methodology
│   ├── RESEARCH.md        # Academic citations
│   └── CREDITS.md         # Attribution
│
├── research/              # Research papers (PDF)
│
├── .gitignore             # Git exclusions
├── .dockerignore          # Docker exclusions
├── Dockerfile.api         # API container
├── Dockerfile.web         # Web container
├── docker-compose.yml     # Docker orchestration
├── pytest.ini             # Pytest configuration
│
├── run_api.sh             # Start Flask API
├── run_web.sh             # Start Next.js UI
├── run_tests.sh           # Run test suite
└── setup.sh               # Initial setup script
```

---

## Root-Level Documentation

### User Guides
- **README.md** - Quick start, installation, usage
- **DOCKER_QUICKSTART.md** - Docker deployment guide
- **LAUNCH_CHECKLIST.md** - Pre-launch tasks

### Technical Documentation
- **PROJECT_SUMMARY.md** - Comprehensive project overview
- **VERIFICATION_PROOF.md** - Scientific proof (correlation 0.26, p < 0.0000001)
- **TESTING_SUMMARY.md** - Test results and coverage
- **VIDEO_SUMMARY.md** - Video poisoning implementation

### Project Structure
- **PROJECT_STRUCTURE.md** - This file

---

## Generated Artifacts (Not Committed)

These are created during testing/usage but excluded from git:

```
verification_data/         # Generated verification datasets
├── clean/                 # Clean test images
├── poisoned/              # Poisoned test images
└── signature.json         # Test signature

test_batch_output/         # Batch processing test outputs
├── poisoned_*.jpg         # Poisoned images
└── batch_signature.json   # Batch signature

demo_output/               # Demo outputs
demo_signature.json        # Demo signature
demo_input.mp4             # Demo input video
demo_output_*.mp4          # Demo output videos

temp/                      # Temporary processing files
```

---

## Code Organization

### Core Algorithms (`poison-core/`)

**radioactive_poison.py** - Image poisoning
- `RadioactiveMarker` class
- FGSM (Fast Gradient Sign Method)
- PGD (Projected Gradient Descent, 1-20 steps)
- Signature generation (256-bit cryptographic)
- Detection via feature correlation

**video_poison.py** - Video poisoning
- Optical flow extraction
- Temporal signature encoding
- Per-frame poisoning mode
- Optical flow poisoning mode

**CLI Tools**
- `poison_cli.py` - Image poisoning CLI
- `video_poison_cli.py` - Video poisoning CLI
- `demo_video.py` - Video demo with visualization

### API Layer (`api/`)

**server.py** - Flask REST API
- `POST /api/poison` - Single image poisoning
- `POST /api/batch` - Batch processing
- `GET /api/health` - Health check
- CORS enabled for web UI

### Frontend (`web-ui/`)

**app/page.tsx** - Main React component
- Three modes: Single / Batch / Video
- Drag-and-drop file upload
- PGD steps slider (1-10)
- Epsilon configuration
- Real-time preview
- Batch results display

### Testing (`tests/`)

**55 tests total:**
- 20 tests for `radioactive_poison.py`
- 19 tests for API endpoints
- 16 tests for CLI tools

### Verification (`verification/`)

**create_dataset.py** - Dataset generator
- Generates clean and poisoned images
- Pattern mode (checkerboard, gradient, stripes)
- Random mode (pure noise)
- Configurable epsilon and PGD steps

**verify_poison.py** - Scientific verification
- Trains ResNet-18 on dataset
- Extracts features from trained model
- Computes correlation with signature
- Reports detection results

---

## Dependencies

### Python (Core & API)
```
torch==2.6.0
torchvision==0.21.0
Pillow==11.0.0
numpy==2.2.1
opencv-python==4.10.0
flask==3.1.0
flask-cors==5.0.0
pytest==8.3.4
```

### Node.js (Web UI)
```
next==14.2.11
react==18.3.1
typescript==5.6.2
tailwindcss==3.4.1
```

### Docker
- Python 3.11 base images
- Node 18 for web UI
- Multi-stage builds for optimization

---

## File Naming Conventions

### Code Files
- `snake_case.py` - Python modules
- `PascalCase` - Python classes
- `camelCase` - TypeScript/JavaScript
- `kebab-case.tsx` - React components

### Documentation
- `UPPERCASE.md` - Project-level docs
- `lowercase.md` - Component-level docs

### Generated Files
- `*_signature.json` - Signature files (gitignored)
- `*_metadata.json` - Metadata files (gitignored)
- `poisoned_*.jpg` - Poisoned images (gitignored)
- `demo_*.mp4` - Demo videos (gitignored)

---

## Development Workflow

### 1. Setup
```bash
./setup.sh              # Install dependencies
```

### 2. Testing
```bash
./run_tests.sh          # Run all tests (55 tests)
pytest -v               # Verbose test output
pytest tests/test_api.py -v  # Run specific test file
```

### 3. Development
```bash
# Terminal 1: API
./run_api.sh            # http://localhost:5001

# Terminal 2: Web UI
./run_web.sh            # http://localhost:3000
```

### 4. Docker Deployment
```bash
docker-compose up       # http://localhost:3000
```

### 5. Verification
```bash
# Generate dataset
python verification/create_dataset.py --clean 20 --poisoned 20 --epsilon 0.02 --pgd-steps 5

# Run verification
python verification/verify_poison.py --data verification_data --signature verification_data/signature.json --epochs 10
```

---

## Code Metrics

```
Total Files:        120+
Lines of Code:      15,000+
Python LOC:         3,217
TypeScript LOC:     ~1,500
Test Coverage:      55/55 tests passing (100%)
Documentation:      9 comprehensive guides
Commits:            6 major milestones
```

---

## Project Phases

### Phase 1: Image Poisoning ✅ COMPLETE
- FGSM/PGD implementation
- CLI tools
- Flask API
- Next.js web UI
- Test suite
- Verification proof

### Phase 2: Video Poisoning ✅ COMPLETE
- Optical flow extraction
- Temporal encoding
- Video CLI
- Demo script
- Integration with web UI

### Phase 3: Multi-modal (Future)
- Code poisoning
- Audio poisoning
- Text watermarking
- Honey pot system

---

## Key Design Decisions

### Why This Structure?

1. **Separation of Concerns**
   - `poison-core/` - Pure algorithms (no web dependencies)
   - `api/` - REST API (no UI dependencies)
   - `web-ui/` - Frontend (no backend logic)
   - `verification/` - Scientific validation (independent)

2. **Testability**
   - All core logic in `poison-core/` is testable
   - API endpoints have integration tests
   - CLI tools have end-to-end tests

3. **Deployment Flexibility**
   - CLI-only: Just `poison-core/`
   - API-only: `poison-core/` + `api/`
   - Full stack: Docker Compose
   - Local dev: Bash scripts

4. **Documentation Co-location**
   - Each component has its own README
   - Root-level docs for project-wide info
   - `docs/` for deep technical content

---

## Navigation Guide

**Want to...?**

- **Understand the technique** → [docs/APPROACH.md](docs/APPROACH.md)
- **Use the CLI** → [poison-core/poison_cli.py](poison-core/poison_cli.py)
- **Deploy with Docker** → [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)
- **Run verification** → [verification/README.md](verification/README.md)
- **See test results** → [TESTING_SUMMARY.md](TESTING_SUMMARY.md)
- **Read the proof** → [VERIFICATION_PROOF.md](VERIFICATION_PROOF.md)
- **Contribute code** → [tests/README.md](tests/README.md)
- **Study the research** → [docs/RESEARCH.md](docs/RESEARCH.md)

---

**Last Updated:** December 27, 2025
