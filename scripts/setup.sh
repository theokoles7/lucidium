#!/bin/bash
# Setup script for Lucidium development environment

set -e

echo "Setting up Lucidium development environment..."

# Make scripts executable
chmod +x scripts/*.py
chmod +x scripts/*.sh

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit
fi

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Create directories if they don't exist
mkdir -p .github/workflows

echo "✓ Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  python scripts/bump_version.py patch    # Bump patch version"
echo "  python scripts/bump_version.py minor    # Bump minor version" 
echo "  python scripts/bump_version.py major    # Bump major version"
echo "  python scripts/bump_version.py --to 1.2.3  # Set specific version"
echo ""
echo "GitHub Actions will automatically create releases when you push version tags."