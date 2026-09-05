"""Prepare approved screenshot copies with documented, non-generative crops."""
import hashlib
import json
import sys
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/images/dad-fieldworks/native-workflow-2026-09"
ENTRIES = [
 ("01-main-current-viewer-actions.png", "simulation-results", (0,0,1440,860), "Simulation and results", "hero and workflow overview", "The Stepped Impedance Quick Tour project shows its complex S matrix and actions for opening Cartesian, Smith and native field views.", "DAD FieldWorks project window with a complex two-port S matrix and separate result-viewer actions."),
 ("Screenshot (13).png", "compiled-geometry", (0,0,1440,860), "Compiled solver geometry", "project workflow", "Inspect the compiled conductor volumes beside the editable geometry list. The shielded structure extends beyond the original view; its color is a geometry display, not a metal-loss result.", "Compiled 3D conductor geometry of the Stepped Impedance Quick Tour, partially outside the original viewport."),
 ("Screenshot (10).png", "cartesian-s-parameters", (30,24,1117,737), "Cartesian S parameters", "result inspection", "Select S(1,1) and S(2,1) magnitude traces and a frequency marker. The chart joins the available frequency samples with straight segments.", "Separate Cartesian window showing S(1,1) and S(2,1) magnitude in dB at the available frequency samples."),
 ("Screenshot (4).png", "smith-chart", (0,0,1440,860), "Smith chart", "result inspection", "Inspect diagonal S(1,1) reflection with a 900 MHz marker, Gamma and normalized impedance. Its selected frequency need not match the matrix view.", "Native Smith chart with a blue S(1,1) reflection trace, 900 MHz marker, Gamma and normalized impedance readouts."),
 ("Screenshot (7).png", "native-hy-field", (0,0,1440,860), "Native magnetic field", "saved native field inspection", "Signed Hy in A/m at saved step 8192 on Z slice 9. Select the job, field component, saved step and slice in a separate native window.", "Native field window showing signed Hy in A/m at saved step 8192 on Z slice 9, with axes and a signed color scale."),
 ("Screenshot (6).png", "native-ez-field", (0,0,1440,860), "Native electric field", "saved native field inspection", "Signed Ez in V/m at saved step 768 on Y slice 10. This saved time-domain view has its own component, slice and color scale.", "Native field window showing signed Ez in V/m at saved step 768 on Y slice 10, with axes and a signed color scale."),
]
def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()
def pixel_sha(img):
 return hashlib.sha256(img.convert("RGBA").tobytes()).hexdigest()
def main():
 if len(sys.argv) != 2:
  raise SystemExit("Usage: prepare_showcase_screenshots.py <ignored local source-copy directory>")
 incoming = Path(sys.argv[1]).resolve()
 if not incoming.is_relative_to(ROOT / ".local_temp"):
  raise SystemExit("Processing requires source copies inside the ignored .local_temp directory.")
 source_manifest = json.loads((incoming / "source-manifest.json").read_text(encoding="utf-8-sig"))
 originals = {r["filename"]: r for r in source_manifest["files"]}
 for name, row in originals.items():
  p = incoming / name
  assert sha(p) == row["sha256"] and p.stat().st_size == row["bytes"], name
 OUT.mkdir(parents=True, exist_ok=True)
 images = []
 for name, slug, crop, title, role, caption, alt in ENTRIES:
  with Image.open(incoming / name) as original:
   assert original.size == (1440,900)
   cropped = original.crop(crop)
   variants = []
   for kind, img in [("full",cropped), ("preview",cropped.resize((720,round(cropped.height * 720/cropped.width)), Image.Resampling.LANCZOS))]:
    file = OUT / (slug + ("-720" if kind == "preview" else "") + ".png")
    # Copy pixel storage to omit metadata without changing pixel values.
    clean = Image.frombytes(img.mode, img.size, img.tobytes())
    encoded = BytesIO()
    clean.save(encoded, format="PNG", optimize=True)
    # A downsampled UI screenshot can compress worse than the original pixels.
    if kind == "preview" and len(encoded.getvalue()) >= variants[0]["bytes"]:
     continue
    file.write_bytes(encoded.getvalue())
    with Image.open(file) as check:
     assert check.size == img.size and check.convert("RGBA").tobytes() == img.convert("RGBA").tobytes()
    variants.append(dict(kind=kind,path=file.relative_to(ROOT).as_posix(),format="PNG",width=img.width,height=img.height,bytes=file.stat().st_size,sha256=sha(file),rgba_pixel_sha256=pixel_sha(img)))
   images.append(dict(id=slug,title=title,source_filename=name,source_sha256=originals[name]["sha256"],source_width=1440,source_height=900,crop=dict(left=crop[0],top=crop[1],right=crop[2],bottom=crop[3],coordinates="right and bottom exclusive"),role=role,caption=caption,alt=alt,derivatives=variants))
 manifest=dict(schema_version=1,asset_set="Native workflow development preview, September 2026",owner="DigitalArtDeco Labs UG (haftungsbeschränkt)",source_date="2026-09-05",publication_scope="User-authorized development preview. File identity does not establish software acceptance or physical accuracy.",executable_provenance="Not supplied with the screenshots; no association with a product commit or promoted software release is asserted.",processing="Rectangular crops remove the taskbar or isolate the complete Cartesian foreground window. Full-size PNG crop pixels are preserved. Metadata is omitted. 720-pixel downscaled PNG website previews are retained only when smaller in bytes than the full PNG.",scientific_content_changed=False,generated_scientific_images=0,images=images)
 (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps(dict(assets=len(images),derivatives=sum(len(i["derivatives"]) for i in images),total_bytes=sum(v["bytes"] for i in images for v in i["derivatives"]))))
if __name__ == "__main__":
 main()
