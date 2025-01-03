# Release Process

## Overview

This project uses GitHub Actions for automated releases. When you push a tag starting with 'v', it automatically:
1. Builds the Python package
2. Creates a GitHub release
3. Attaches distribution files to the release

## Making a Release

### 1. Prepare for Release
1. Ensure all changes are committed and pushed
2. Verify tests pass on the main branch
3. Update documentation if needed
4. Review the changelog

### 2. Choose Version Number
We follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features, backwards-compatible
- PATCH: Bug fixes, backwards-compatible

For pre-releases, append:
- Alpha: `-alpha.1`, `-alpha.2`, etc.
- Beta: `-beta.1`, `-beta.2`, etc.
- Release Candidate: `-rc.1`, `-rc.2`, etc.

### 3. Create and Push Tag
```bash
# Create tag
git tag v1.0.0  # Replace with your version

# Push tag
git push origin v1.0.0
```

### 4. Monitor Release
1. Go to GitHub Actions tab
2. Watch the "Release" workflow
3. Once complete, verify the release on GitHub releases page

## Release Types

### Production Release
- Tag format: `v1.0.0`
- Creates a standard GitHub release
- Builds and attaches distribution files
- Generates release notes automatically

### Pre-release
- Tag formats: 
  - Alpha: `v1.0.0-alpha.1`
  - Beta: `v1.0.0-beta.1`
  - RC: `v1.0.0-rc.1`
- Marked as pre-release on GitHub
- Useful for testing before production release

## Release Artifacts

Each release includes:
- Source distribution (.tar.gz)
- Wheel distribution (.whl)
- Auto-generated release notes
- Git tag

## Troubleshooting

If the release fails:
1. Check the GitHub Actions logs
2. Verify tag format is correct
3. Ensure all tests pass
4. Check if you have the necessary permissions

## Post-Release

After a successful release:
1. Verify the release appears on GitHub
2. Download and test the released artifacts
3. Update documentation with new version if needed
4. Announce the release if appropriate 