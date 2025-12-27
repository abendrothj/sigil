# 🚀 Public Launch Checklist

## Pre-Launch Tasks

### ✅ Code Complete
- [x] Core algorithm (radioactive_poison.py)
- [x] PGD implementation (robust poisoning)
- [x] CLI tool (single + batch)
- [x] Flask API server
- [x] Next.js web UI
- [x] Video poisoning (beta)
- [x] Test suite (75+ tests)
- [x] Docker setup
- [x] Documentation

### ✅ Infrastructure
- [x] Docker containerization
- [x] docker-compose.yml
- [x] .dockerignore
- [x] Health checks
- [ ] GitHub Actions CI/CD
- [ ] Automated tests on push

### 📸 Marketing Assets Needed

#### 1. Verification Proof Screenshot (CRITICAL)

**Run this:**
```bash
source venv/bin/activate
python verification/verify_poison.py --epochs 5
```

**Capture screenshot showing:**
- Clean Model Confidence: ~0.001
- Poisoned Model Confidence: ~0.8+
- Detection: ✅ DETECTED

**Add to README at top:**
```markdown
## Proof It Works

![Verification Results](docs/assets/verification_proof.png)

*Trained a ResNet-18 on poisoned data - signature detected with 89% confidence*
```

#### 2. Before/After Comparison

Create visual showing:
- Original image
- Poisoned image (looks identical)
- Difference map (amplified 100x - shows perturbation)

**Tool:**
```python
import numpy as np
from PIL import Image

original = np.array(Image.open('original.jpg'))
poisoned = np.array(Image.open('poisoned.jpg'))
diff = np.abs(original - poisoned) * 100  # Amplify
Image.fromarray(diff.astype(np.uint8)).save('difference.jpg')
```

#### 3. Web UI Screenshots

Capture:
- Upload interface (drag-and-drop)
- Epsilon slider
- Download results screen
- Success message

### 🎯 "Honey Pot" Demo Site

**Purpose:** Live demonstration that catches scrapers

**Setup:**
1. Generate 50 poisoned images (high-res textures)
2. Upload to: `free-ai-textures.com` (or similar)
3. SEO optimize:
   - Title: "Free 4K Textures - Public Domain"
   - Tags: CC0, royalty-free, AI training
   - robots.txt: Allow all

4. Wait 3-6 months
5. Test new models for signature
6. Blog post: "We Caught Model X Training on Our Honey Pot"

**Images to Generate:**
```bash
# Create honey pot images
python poison-core/poison_cli.py batch \
  ./honeypot/sources/ \
  ./honeypot/poisoned/ \
  --epsilon 0.02 \
  --pgd-steps 5

# Save signature
cp ./honeypot/poisoned/batch_signature.json ./honeypot/SIGNATURE_ARCHIVE.json
```

### 📝 Content Creation

#### Blog Post 1: "Introducing Basilisk"

**Outline:**
1. The Problem (AI training scrapes without permission)
2. Existing Solutions (watermarks fail, lawsuits slow)
3. Our Solution (radioactive marking)
4. How It Works (simple explanation)
5. Try It Now (docker-compose up)

**Target:** Hacker News, Reddit r/MachineLearning

#### Blog Post 2: "We Poisoned 1000 Images. Here's What Happened."

**Outline:**
1. The Experiment Setup
2. Training a Model
3. Detection Results
4. Compression Testing
5. Lessons Learned

**Target:** Medium, Towards Data Science

#### Blog Post 3: "Video Poisoning: Defending Against Sora"

**Outline:**
1. Why Image Poisoning Doesn't Work for Video
2. Our Novel Approach (Optical Flow)
3. Technical Deep Dive
4. Early Results
5. Call for Collaborators

**Target:** Academic audience, CVPR/ICCV workshop

### 🎬 Video Content

#### Demo Video (3 minutes)

**Script:**
0:00 - Problem statement
0:30 - Show drag-and-drop UI
1:00 - Download poisoned image
1:30 - Show verification (model detection)
2:00 - CLI demonstration
2:30 - Call to action

**Platforms:**
- YouTube
- Twitter/X
- TikTok (60s version)

### 🌐 Community Strategy

#### GitHub
- [ ] Add CONTRIBUTING.md
- [ ] Create issue templates
- [ ] Set up discussions
- [ ] Pin important issues
- [ ] Create GitHub Project board

#### Social Media
- [ ] Twitter/X thread (technical deep dive)
- [ ] Reddit r/StableDiffusion (artist protection angle)
- [ ] Reddit r/MachineLearning (research angle)
- [ ] Hacker News (Show HN: Basilisk)

#### Outreach
- [ ] Email to Karla Ortiz (artist plaintiff in AI lawsuit)
- [ ] Email to Spawning AI (Have I Been Trained creators)
- [ ] Email to Glaze/Nightshade team (complementary, not competitive)
- [ ] Post on ArtStation forums
- [ ] Post on VFX Reddit

### 📊 Analytics Setup

**Metrics to Track:**
- GitHub stars/forks
- Docker pulls
- Website visits (if deployed publicly)
- Twitter impressions
- Reddit upvotes
- Issue/PR count

**Tools:**
- GitHub Insights (built-in)
- Google Analytics (if public site)
- Twitter Analytics
- PostHog (open-source analytics)

### 🔒 Security Review

**Before Launch:**
- [ ] Audit for secrets in code (API keys, etc.)
- [ ] Review .gitignore (no credentials)
- [ ] Test Docker security (non-root user)
- [ ] Sanitize error messages (no path disclosure)
- [ ] Rate limiting on API (prevent abuse)
- [ ] Input validation (prevent injection)

**Security Considerations:**
- This is a defensive tool (artist protection)
- Not designed for malicious attacks
- Clear disclaimer in README
- Ethical use policy

### 📜 Legal/Compliance

**Before Launch:**
- [ ] Add MIT LICENSE file
- [ ] Copyright attribution (Facebook AI Research paper)
- [ ] Disclaimer about dual-use
- [ ] Privacy policy (if collecting any data)
- [ ] Terms of service (if public deployment)

**Disclaimers to Add:**
```markdown
## ⚠️ Responsible Use

This tool is for:
✅ Protecting your own creative work
✅ Academic research on data provenance
✅ Defensive security testing

This tool is NOT for:
❌ Poisoning datasets you don't own
❌ Malicious attacks on public resources
❌ Violating terms of service

Users are responsible for legal compliance.
```

### 🚢 Deployment Options

#### Option 1: GitHub Only (Easiest)
- README with Docker instructions
- Users self-host
- Zero cost

#### Option 2: Demo Site (Marketing)
- Deploy to Fly.io or Railway
- Allow 10 images/day per IP (free tier)
- Link in README: "Try Live Demo"
- Cost: ~$5-10/month

#### Option 3: Full SaaS (Future)
- Stripe integration
- User accounts
- Cloud GPU workers
- Much more complex

**Recommendation:** Start with Option 1, add Option 2 after getting traction.

---

## Launch Day Sequence

### T-1 Week
- [ ] Run verification, capture screenshot
- [ ] Create honey pot site
- [ ] Write blog post
- [ ] Record demo video
- [ ] Set up analytics

### T-1 Day
- [ ] Final code review
- [ ] Test Docker build
- [ ] Prepare social media posts
- [ ] Draft Hacker News/Reddit posts

### Launch Day

**Morning:**
1. Push final commit
2. Create GitHub release v1.0.0
3. Update README with verification proof

**Afternoon:**
1. Post on Hacker News (Show HN)
2. Post on Reddit r/MachineLearning
3. Tweet thread with demo video
4. Email outreach to key people

**Evening:**
1. Monitor comments/issues
2. Respond to questions
3. Fix any critical bugs

### T+1 Day
- Post on Reddit r/StableDiffusion
- Post on ArtStation forums
- Email follow-ups

### T+1 Week
- Publish blog post on Medium
- Post on LinkedIn (professional angle)
- Gather user feedback
- Plan next iteration

---

## Success Metrics

### Week 1 Goals
- 100+ GitHub stars
- 500+ Docker pulls
- 5+ community contributions (issues/PRs)
- 1+ media mention

### Month 1 Goals
- 500+ GitHub stars
- 2000+ Docker pulls
- Featured on Hacker News front page
- 10+ community contributions
- 1 academic citation

### Month 3 Goals
- 1000+ GitHub stars
- 5000+ users
- Published research paper
- Integration into popular tools (Photoshop plugin?)

---

## Post-Launch Priorities

### Phase 1 (Week 1-2)
1. Bug fixes from user reports
2. Documentation improvements
3. Add more examples
4. Improve error messages

### Phase 2 (Week 3-4)
1. GPU acceleration
2. Web UI improvements
3. Video poisoning refinement
4. Compression testing

### Phase 3 (Month 2-3)
1. Academic paper submission
2. Large-scale validation study
3. Honey pot results analysis
4. Phase 3 features (audio, code)

---

## Known Risks

### Technical
- PyTorch dependency large (500MB+)
- Compression may degrade signature (PGD helps)
- Detection untested on real models (need validation)

**Mitigation:**
- Docker handles dependencies
- PGD + tunable epsilon
- Verification script provides proof-of-concept

### Social/Political
- AI companies may view as attack
- Could trigger adversarial research (signature removal)
- Legal gray area (data poisoning)

**Mitigation:**
- Frame as defensive tool
- Open research (transparency)
- Clear ethical guidelines
- Academic legitimacy (cite papers)

### Competitive
- Glaze/Nightshade already established
- They have funding, team, GUI

**Mitigation:**
- We have detection (they don't)
- We have video (they don't)
- Open source (they're closed)
- Complementary, not competitive

---

## Final Pre-Launch Check

**Run this command before pushing:**

```bash
# Test Docker build
docker-compose build

# Test Docker run
docker-compose up -d
sleep 30
curl http://localhost:5000/health  # Should return 200
curl http://localhost:3000  # Should return HTML

# Test CLI
source venv/bin/activate
python poison-core/poison_cli.py info  # Should work

# Run tests
./run_tests.sh  # All should pass

# Clean up
docker-compose down
```

**If all pass:** ✅ Ready to launch!

---

## The "Go" Decision

**Launch when:**
- ✅ Docker works one-command
- ✅ Verification proof screenshot ready
- ✅ Blog post written
- ✅ Demo video recorded
- ✅ All tests passing
- ✅ Security reviewed
- ✅ Legal disclaimers added

**Don't wait for:**
- ❌ Perfect code (iterate after launch)
- ❌ All features (ship MVP first)
- ❌ Academic paper published (cite existing)
- ❌ Marketing site (GitHub README is fine)

---

**Last Check:** Read this entire checklist. If >80% complete, you're ready.

**Launch Date Target:** [SET DATE]

**Post-Launch:** Celebrate! You built something real that helps artists. 🎉
