#!/usr/bin/env python3
"""Fast bulk or single-file media conversion by extension."""

from __future__ import annotations
import argparse
import importlib
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from typing import Any, Final, Iterable, cast

VERSION: Final[str] = "1.0.1"
logger = logging.getLogger("m2m")
MP3_BITRATE: Final[str] = "320k"
AAC_BITRATE: Final[str] = "256k"
OPUS_BITRATE: Final[str] = "192k"
VIDEO_CRF: Final[str] = "18"
VIDEO_PRESET: Final[str] = "slow"
WEBM_CRF: Final[str] = "30"
IMAGE_EXTS: Final[set[str]] = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".avif", ".heic", ".heif"}
ICON_EXTS: Final[set[str]] = {".ico"}
VEC_EXTS: Final[set[str]] = {".svg", ".eps"}
AUDIO_EXTS: Final[set[str]] = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".wma", ".opus", ".aiff"}
VIDEO_EXTS: Final[set[str]] = {".mp4", ".mov", ".wmv", ".avi", ".mkv", ".webm", ".flv", ".m4v", ".mpg", ".mpeg", ".3gp", ".ogv"}
COMMON_MEDIA_EXT: Final[set[str]] = IMAGE_EXTS | ICON_EXTS | VEC_EXTS | AUDIO_EXTS | VIDEO_EXTS
EXT_TO_CATEGORY: Final[dict[str, str]] = {**{e: "image" for e in IMAGE_EXTS}, **{e: "icon" for e in ICON_EXTS}, **{e: "vector" for e in VEC_EXTS}, **{e: "audio" for e in AUDIO_EXTS}, **{e: "video" for e in VIDEO_EXTS}}

def outs_for(input_ext_dot: str) -> set[str]:
    cat = EXT_TO_CATEGORY.get(input_ext_dot)
    if cat is None:
        return set()
    if cat == "audio":
        return {e.lstrip(".") for e in AUDIO_EXTS}
    if cat == "video":
        return {e.lstrip(".") for e in VIDEO_EXTS}
    if cat == "vector":
        return {e.lstrip(".") for e in IMAGE_EXTS}
    if cat == "image":
        return {e.lstrip(".") for e in IMAGE_EXTS} | {"ico"}
    if cat == "icon":
        return {e.lstrip(".") for e in IMAGE_EXTS} | {"ico"}
    return set()

def a_codec(out_ext: str) -> list[str]:
    return {"mp3": ["-c:a", "libmp3lame", "-b:a", MP3_BITRATE], "wav": ["-c:a", "pcm_s16le"], "ogg": ["-c:a", "libvorbis", "-q:a", "8"], "opus": ["-c:a", "libopus", "-b:a", OPUS_BITRATE], "flac": ["-c:a", "flac", "-compression_level", "8"], "aac": ["-c:a", "aac", "-b:a", AAC_BITRATE], "m4a": ["-c:a", "aac", "-b:a", AAC_BITRATE], "aiff": ["-c:a", "pcm_s16be"], "wma": ["-c:a", "wmav2", "-b:a", OPUS_BITRATE]}.get(out_ext, [])

def v_codec(out_ext: str) -> list[str]:
    return {"mp4": ["-c:v", "libx264", "-crf", VIDEO_CRF, "-preset", VIDEO_PRESET, "-c:a", "aac", "-b:a", AAC_BITRATE, "-movflags", "+faststart"], "mkv": ["-c:v", "libx264", "-crf", VIDEO_CRF, "-preset", VIDEO_PRESET, "-c:a", "aac", "-b:a", AAC_BITRATE], "mov": ["-c:v", "libx264", "-crf", VIDEO_CRF, "-preset", VIDEO_PRESET, "-c:a", "aac", "-b:a", AAC_BITRATE], "m4v": ["-c:v", "libx264", "-crf", VIDEO_CRF, "-c:a", "aac", "-b:a", AAC_BITRATE], "webm": ["-c:v", "libvpx-vp9", "-crf", WEBM_CRF, "-b:v", "0", "-c:a", "libopus", "-b:a", OPUS_BITRATE], "avi": ["-c:v", "libx264", "-crf", VIDEO_CRF, "-c:a", "libmp3lame", "-b:a", MP3_BITRATE], "wmv": ["-c:v", "wmv2", "-c:a", "wmav2", "-b:a", OPUS_BITRATE], "flv": ["-c:v", "flv", "-c:a", "libmp3lame", "-b:a", "128k"], "mpg": ["-c:v", "mpeg2video", "-b:v", "5000k", "-c:a", "mp2", "-b:a", "256k"], "mpeg": ["-c:v", "mpeg2video", "-b:v", "5000k", "-c:a", "mp2", "-b:a", "256k"], "3gp": ["-c:v", "h263", "-b:v", "500k", "-c:a", "aac", "-b:a", "64k", "-s", "320x240"], "ogv": ["-c:v", "libtheora", "-q:v", "7", "-c:a", "libvorbis", "-q:a", "5"]}.get(out_ext, [])

class ConversionError(RuntimeError):
    pass

def _norm_ext(value: str) -> str:
    value = value.strip().lower()
    if not value:
        raise argparse.ArgumentTypeError("extension cannot be empty")
    if value == "any":
        return "any"
    value = value.lstrip(".")
    if not value.replace("_", "").replace("-", "").isalnum():
        raise argparse.ArgumentTypeError(f"invalid extension: {value!r}")
    return value

def need_ffmpeg() -> None:
    if not shutil.which("ffmpeg"):
        raise ConversionError("Missing dependency: ffmpeg (https://ffmpeg.org/download.html)")

def run_ff(cmd: list[str], timeout: int) -> None:
    try:
        p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        raise ConversionError(f"ffmpeg timed out after {timeout}s") from e
    if p.returncode != 0:
        raise ConversionError(p.stderr.strip() or f"ffmpeg exited with code {p.returncode}")

def iter_in(src: str, in_ext: str) -> Iterable[str]:
    if os.path.isfile(src):
        yield src
        return
    if not os.path.isdir(src):
        raise ConversionError(f"Source is not a file or directory: {src}")
    want = None if in_ext == "any" else f".{in_ext}"
    for name in sorted(os.listdir(src)):
        path = os.path.join(src, name)
        if os.path.isdir(path) or os.path.islink(path):
            continue
        _, ext = os.path.splitext(path)
        ext = ext.lower()
        if want is not None and ext != want:
            continue
        if want is None and ext not in COMMON_MEDIA_EXT:
            continue
        yield path

def tmp_path(dest_dir: str, out_ext: str) -> str:
    fd, path = tempfile.mkstemp(prefix=".m2m_", suffix=f".{out_ext}", dir=dest_dir)
    os.close(fd)
    return path

def keep_times(src_path: str, out_path: str) -> None:
    try:
        st = os.stat(src_path)
        os.utime(out_path, (st.st_atime, st.st_mtime))
    except OSError:
        return

def to_ico(src_path: str, tmp_out: str) -> None:
    try:
        Image = cast(Any, importlib.import_module("PIL.Image"))
    except ModuleNotFoundError as e:
        raise ConversionError("Output .ico requires Pillow (pip install pillow)") from e
    ICON_SIZES: Final[tuple[tuple[int, int], ...]] = ((16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256))
    with Image.open(src_path) as img:
        img_rgba = img.convert("RGBA")
        w, h = img_rgba.size
        side = max(w, h)
        if w != h:
            canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
            canvas.paste(img_rgba, ((side - w) // 2, (side - h) // 2))
            img_rgba = canvas
        img_rgba.save(tmp_out, format="ICO", sizes=ICON_SIZES)

def vec_to_ras(tmp_out: str, src_path: str, out_ext: str) -> None:
    try:
        svg2rlg = cast(Any, importlib.import_module("svglib.svglib")).svg2rlg
        renderPM = cast(Any, importlib.import_module("reportlab.graphics.renderPM"))
    except ModuleNotFoundError as e:
        raise ConversionError("Converting .svg/.eps requires svglib + reportlab") from e
    drawing = svg2rlg(src_path)
    if drawing is None:
        raise ConversionError("Failed to parse vector file")
    renderPM.drawToFile(drawing, tmp_out, fmt=out_ext.upper())

def ras_pil(src_path: str, tmp_out: str, out_ext: str) -> bool:
    try:
        Image = cast(Any, importlib.import_module("PIL.Image"))
    except ModuleNotFoundError:
        return False
    try:
        with Image.open(src_path) as img:
            img.save(tmp_out, format=out_ext.upper())
        return True
    except Exception:
        return False

def convert(src_path: str, out_ext: str, dest_dir: str, overwrite: bool, timeout: int) -> str:
    base = os.path.basename(src_path)
    stem, _ = os.path.splitext(base)
    out_path = os.path.join(dest_dir, f"{stem}.{out_ext}")
    src_ext = os.path.splitext(src_path)[1].lower()
    allowed = outs_for(src_ext)
    if not allowed:
        raise ConversionError(f"Unsupported input extension: {src_ext}")
    if out_ext not in allowed:
        raise ConversionError(f".{out_ext} is not valid for input {src_ext}. Allowed: {', '.join(sorted(allowed))}")
    if os.path.abspath(src_path) == os.path.abspath(out_path):
        return "skip(same)"
    if not overwrite and os.path.exists(out_path):
        return "skip(exists)"
    tmp_out = tmp_path(dest_dir, out_ext)
    try:
        if out_ext == "ico":
            to_ico(src_path, tmp_out)
        elif src_ext in VEC_EXTS and out_ext in {e.lstrip('.') for e in IMAGE_EXTS}:
            vec_to_ras(tmp_out, src_path, out_ext)
        elif src_ext in IMAGE_EXTS or src_ext == ".ico":
            if not ras_pil(src_path, tmp_out, out_ext):
                need_ffmpeg()
                cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error" if not logger.isEnabledFor(logging.DEBUG) else "warning", "-i", src_path, "-y", tmp_out]
                run_ff(cmd, timeout)
        else:
            need_ffmpeg()
            src_cat = EXT_TO_CATEGORY.get(src_ext)
            cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error" if not logger.isEnabledFor(logging.DEBUG) else "warning", "-i", src_path, "-y"]
            if src_cat == "audio":
                cmd += ["-map", "0:a:0?", "-vn", "-sn", "-dn", "-map_metadata", "0"]
                cmd += a_codec(out_ext)
            elif src_cat == "video":
                cmd += ["-map", "0:v:0?", "-map", "0:a:0?", "-sn", "-dn", "-map_metadata", "0"]
                cmd += v_codec(out_ext)
            cmd.append(tmp_out)
            run_ff(cmd, timeout)
        os.replace(tmp_out, out_path)
        keep_times(src_path, out_path)
        return "ok"
    finally:
        try:
            if os.path.exists(tmp_out):
                os.remove(tmp_out)
        except OSError:
            pass

def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    p = argparse.ArgumentParser(description="Bulk/single-file media converter")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    p.add_argument("--src", help="Source file or directory")
    p.add_argument("--out", "-o", required=True, type=_norm_ext, help="Output extension (e.g., png, ogg, wmv)")
    p.add_argument("--input", "-i", default="any", type=_norm_ext, help="Input extension to filter (default: any)")
    p.add_argument("--dest", help="Output directory (default: same as src file/dir)")
    p.add_argument("--dir", "-d", dest="src", help="Alias for --src (directory)")
    p.add_argument("--res", "-r", dest="dest", help="Alias for --dest")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs")
    p.add_argument("--timeout", type=int, default=900, help="ffmpeg timeout in seconds (default: 900)")
    p.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="[%(levelname)s] %(message)s")
    if not args.src:
        raise SystemExit("--src/--dir is required")
    src = os.path.abspath(os.path.expanduser(args.src))
    out_ext = args.out
    in_ext = args.input
    if args.timeout <= 0:
        raise SystemExit("--timeout must be positive")
    if os.path.isfile(src):
        default_dest = os.path.dirname(src)
    else:
        default_dest = src
    dest = os.path.abspath(os.path.expanduser(args.dest)) if args.dest else default_dest
    os.makedirs(dest, exist_ok=True)
    files = list(iter_in(src, in_ext))
    if not files:
        logger.info("No matching files found.")
        return 0
    ok = fail = skip = 0
    logger.info("Converting %d file(s) -> .%s", len(files), out_ext)
    for path in files:
        try:
            status = convert(path, out_ext, dest, args.overwrite, args.timeout)
            if status == "ok":
                ok += 1
            else:
                skip += 1
        except Exception as e:
            fail += 1
            logger.error("%s: %s", os.path.basename(path), e)
            if logger.isEnabledFor(logging.DEBUG):
                traceback.print_exc()
    if skip:
        logger.info("Done: %d ok, %d failed, %d skipped", ok, fail, skip)
    else:
        logger.info("Done: %d ok, %d failed", ok, fail)
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
