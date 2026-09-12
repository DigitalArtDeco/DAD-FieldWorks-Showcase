"""Create approved, pixel-preserving company-site screenshot crops.

Usage: python scripts/prepare_company_screenshots.py ORIGINAL_DIRECTORY [RECIPE]
Original files are read only. All outputs stay in this website repository.
"""
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/images/dad-fieldworks/application-2026-09-09"
RECIPE = OUTPUT / "source-selection.json"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    sources = Path(sys.argv[1]).resolve(strict=True)
    recipe = Path(sys.argv[2]).resolve(strict=True) if len(sys.argv) > 2 else RECIPE
    assert recipe.is_relative_to(ROOT / "assets/images/dad-fieldworks")
    output = recipe.parent
    selection = json.loads(recipe.read_text(encoding="utf-8"))
    records = []
    for entry in selection["sources"]:
        original = sources / entry["original"]
        assert original.resolve().is_relative_to(sources)
        assert sha(original.read_bytes()) == entry["source_sha256"], entry["original"]
        with Image.open(original) as image:
            assert list(image.size) == entry["source_size"]
            image = image.convert("RGBA")
            left, top, right, bottom = entry["crop"]
            assert 0 <= left < right <= image.width and 0 <= top < bottom <= image.height
            cropped = image.crop((left, top, right, bottom))
        target = output / (entry["id"] + ".png")
        cropped.save(target, format="PNG", optimize=True)
        with Image.open(target) as check:
            assert check.convert("RGBA").tobytes() == cropped.tobytes()
        extra = {}
        if "preview_crop" in entry:
            with Image.open(original) as image:
                image = image.convert("RGBA")
                left, top, right, bottom = entry["preview_crop"]
                assert 0 <= left < right <= image.width and 0 <= top < bottom <= image.height
                preview = image.crop((left, top, right, bottom))
            preview_path = output / (entry["id"] + "-preview.png")
            preview.save(preview_path, format="PNG", optimize=True)
            with Image.open(preview_path) as check:
                assert check.convert("RGBA").tobytes() == preview.tobytes()
            extra["preview"] = {"derivative": preview_path.name, "width": preview.width,
                "height": preview.height, "sha256": sha(preview_path.read_bytes()),
                "rgba_sha256": sha(preview.tobytes()), "bytes": preview_path.stat().st_size}
        records.append({
            **entry, "derivative": target.name,
            "width": cropped.width, "height": cropped.height,
            "sha256": sha(target.read_bytes()),
            "rgba_sha256": sha(cropped.tobytes()), "bytes": target.stat().st_size,
            "detail": "views/" + entry["id"] + ".html", **extra
        })
    manifest = {
        "date": selection["date"],
        "processing": "Rectangular crop and lossless PNG encoding only; no resampling, retouching or color changes.",
        "coordinates": "left, top, right, bottom; right and bottom exclusive",
        "context": selection.get("context", "Tuto shows construction. Via Transition shows results from a different project. The field is a saved time-domain component, not a field at a plot marker frequency."),
        "captures": records
    }
    if "date_context" in selection:
        manifest["date_context"] = selection["date_context"]
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"captures": len(records), "bytes": sum(x["bytes"] for x in records)}))

if __name__ == "__main__":
    main()
