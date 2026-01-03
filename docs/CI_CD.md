# CI/CD Pipeline Documentation

## Overview

Sigil uses GitHub Actions for continuous integration and deployment. This document describes the CI/CD pipeline, workflows, and best practices.

## Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual dispatch

**Jobs:**

#### Test Suite
- Runs on Python 3.8, 3.9, 3.10, and 3.11
- Installs system dependencies (FFmpeg, OpenCV libs)
- Runs pytest with coverage
- Uploads coverage to Codecov (Python 3.11 only)

**Status:** ✅ Required for merge

#### Code Quality
- Runs Ruff linter (fast Python linting)
- Checks Black code formatting (informational)
- Checks isort import sorting (informational)

**Status:** ⚠️ Informational (warnings don't block merge)

#### Docker Build
- Builds API Docker image
- Builds Web UI Docker image
- Validates docker-compose configuration
- Uses GitHub Actions cache for faster builds

**Status:** ✅ Required for merge

#### Security Scan
- Checks dependencies with Safety
- Runs Bandit security scanner
- Reports vulnerabilities (informational)

**Status:** ⚠️ Informational

### 2. Release Workflow (`.github/workflows/release.yml`)

**Triggers:**
- Git tags matching `v*.*.*` pattern (e.g., `v1.0.0`)

**Jobs:**

#### Create Release
- Generates changelog from git commits
- Creates GitHub Release with notes
- Includes installation instructions

#### Publish Docker Images
- Builds and pushes images to GitHub Container Registry (GHCR)
- Tags images with:
  - Full version (e.g., `1.0.0`)
  - Major.minor (e.g., `1.0`)
  - Major only (e.g., `1`)
  - `latest`

**Publishing a Release:**

```bash
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0

# Or create a tag with annotation
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 3. Weekly Code Quality Report (`.github/workflows/weekly-report.yml`)

**Triggers:**
- Every Monday at 9 AM UTC
- Manual dispatch

**Actions:**
- Calculates cyclomatic complexity
- Generates maintainability index
- Runs security scans
- Checks for vulnerable dependencies
- Counts lines of code
- Creates GitHub issue with report

## Dependabot Configuration

**File:** `.github/dependabot.yml`

Automatically creates PRs for:
- Python dependencies (weekly)
- GitHub Actions versions (weekly)
- Docker base images (weekly)

**Settings:**
- Runs every Monday
- Maximum 5 open PRs per ecosystem
- Auto-labels PRs
- Requests review from maintainers

## Branch Protection Rules

**Recommended settings for `main` branch:**

1. Require pull request reviews before merging
2. Require status checks to pass:
   - ✅ Test Suite (all Python versions)
   - ✅ Docker Build
3. Require branches to be up to date
4. Do not allow force pushes
5. Require linear history (optional)

## CI/CD Best Practices

### For Contributors

1. **Run tests locally before pushing:**
   ```bash
   ./run_tests.sh
   ```

2. **Check code style:**
   ```bash
   ruff check .
   black --check .
   isort --check .
   ```

3. **Build Docker images locally:**
   ```bash
   docker-compose build
   ```

4. **Watch CI status:**
   - Check Actions tab after pushing
   - Fix failures promptly
   - Don't ignore warnings

### For Maintainers

1. **Review CI logs for failures**
2. **Monitor Dependabot PRs:**
   - Review dependency updates weekly
   - Test breaking changes locally
   - Merge security updates promptly

3. **Release process:**
   ```bash
   # Update CHANGELOG.md
   # Commit changes
   git add CHANGELOG.md
   git commit -m "chore: prepare v1.0.0 release"
   
   # Create and push tag
   git tag v1.0.0
   git push origin main
   git push origin v1.0.0
   ```

4. **Monitor GitHub Container Registry:**
   - Check image sizes
   - Clean up old tags periodically
   - Verify image security scans

## Troubleshooting

### Common CI Failures

#### Test Failures
- Check test logs in Actions tab
- Reproduce locally: `./run_tests.sh verbose`
- Ensure dependencies are up to date

#### Docker Build Failures
- Check Dockerfile syntax
- Verify base image availability
- Test locally: `docker-compose build`

#### Linting Failures
- Run `ruff check .` locally
- Auto-fix issues: `ruff check . --fix`
- Check `pyproject.toml` configuration

### Performance Issues

#### Slow CI Builds
- Use GitHub Actions cache (already configured)
- Parallelize independent jobs
- Optimize Docker layer caching

#### Flaky Tests
- Increase timeouts for network operations
- Add retries for external dependencies
- Mock external services

## Secrets and Configuration

### Required GitHub Secrets

**For Release Workflow:**
- `GITHUB_TOKEN` (automatically provided)

**Optional:**
- `CODECOV_TOKEN` (for private repos)

### Environment Variables

Set in workflow files as needed:
- `PYTHONPATH`
- `CI=true` (automatically set)

## Metrics and Monitoring

### Key Metrics

1. **Test Pass Rate:** Should be 100%
2. **Code Coverage:** Target >80%
3. **Build Time:** Monitor for increases
4. **Docker Image Size:** Keep optimized

### Dashboards

- **GitHub Actions:** View workflow runs
- **Codecov:** Code coverage trends
- **Dependabot:** Dependency updates

## Future Enhancements

### Planned

- [ ] Deployment to staging environment
- [ ] Performance benchmarking in CI
- [ ] Automated security scanning with Snyk
- [ ] Integration tests with real video files
- [ ] Canary deployments

### Under Consideration

- [ ] Multi-architecture Docker builds (ARM64)
- [ ] Automated API documentation generation
- [ ] Nightly builds with extended tests
- [ ] Integration with academic repositories (arXiv)

## Support

For CI/CD issues:
1. Check workflow logs in Actions tab
2. Review this documentation
3. Open an issue with `ci/cd` label
4. Contact maintainers: @abendrothj

---

**Last Updated:** January 3, 2026  
**Maintained By:** Sigil Team
