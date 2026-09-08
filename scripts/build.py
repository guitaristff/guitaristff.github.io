"""Package only the public website. No dependencies or build toolchain required."""
from pathlib import Path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"
PUBLIC_FILES = [
    "index.html", "styles.css", "app.js", ".nojekyll",
    "assets/favicon.svg", "assets/github-avatar.png",
    "assets/bmw-r-ninet.svg", "assets/sixiang-cover.jpg",
    "assets/fbsr-scene.png", "assets/raft-fig1.png",
    "assets/uav-platform-01.png", "assets/uav-platform-02.png", "assets/uav-platform-03.png",
]


def build():
    for name in PUBLIC_FILES:
        source = ROOT / name
        if not source.is_file():
            raise FileNotFoundError(f"Missing public asset: {name}")
        target = OUTPUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    archive_path = ROOT / "zhaofeng-du-website.zip"
    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in PUBLIC_FILES:
            archive.write(OUTPUT / name, arcname=name)
    print(f"Built {len(PUBLIC_FILES)} public files in {OUTPUT}")
    print(f"Archive: {archive_path} ({archive_path.stat().st_size:,} bytes)")
    return OUTPUT


if __name__ == "__main__":
    build()
