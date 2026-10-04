"""Extension Tests"""
import json
from pathlib import Path

def test_manifest_exists():
    manifest = Path("extension/manifest.json")
    assert manifest.exists(), "manifest.json not found"

def test_manifest_valid():
    manifest = Path("extension/manifest.json")
    data = json.loads(manifest.read_text())
    assert data["manifest_version"] == 3
    assert "permissions" in data

def test_content_script_exists():
    content = Path("extension/content.js")
    assert content.exists(), "content.js not found"

def test_background_script_exists():
    bg = Path("extension/background.js")
    assert bg.exists(), "background.js not found"

def test_popup_exists():
    popup = Path("extension/popup.html")
    assert popup.exists(), "popup.html not found"
