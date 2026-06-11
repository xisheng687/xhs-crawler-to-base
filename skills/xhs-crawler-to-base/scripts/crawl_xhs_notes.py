#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import time
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen


UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"


def fetch(url, referer=None, timeout=25):
    headers = {"User-Agent": UA}
    if referer:
        headers["Referer"] = referer
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as resp:
        return resp.geturl(), resp.read(), resp.headers.get_content_type()


def extract_initial_state(html):
    match = re.search(r"<script>window\.__INITIAL_STATE__=(.*?)</script>", html, re.S)
    if not match:
        raise ValueError("window.__INITIAL_STATE__ not found")
    raw = unescape(match.group(1))
    raw = raw.replace(":undefined", ":null")
    return json.loads(raw)


def note_id_from_url(url):
    match = re.search(r"/(?:discovery/item|explore)/([0-9a-fA-F]+)", url)
    if match:
        return match.group(1)
    parts = [p for p in urlparse(url).path.split("/") if p]
    return parts[-1] if parts else ""


def strip_query(url):
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))


def first_note_detail(state, preferred_id):
    detail_map = (((state.get("note") or {}).get("noteDetailMap")) or {})
    if preferred_id and preferred_id in detail_map:
        return preferred_id, detail_map[preferred_id].get("note") or {}
    if detail_map:
        key = next(iter(detail_map))
        return key, detail_map[key].get("note") or {}
    raise ValueError("note detail missing from initial state")


def pick_image_url(image):
    info = image.get("infoList") or []
    for scene in ("WB_DFT", "WB_PRV"):
        for item in info:
            if item.get("imageScene") == scene and item.get("url"):
                return item["url"]
    return image.get("urlDefault") or image.get("urlPre") or image.get("url") or (info[0].get("url") if info else "")


def collect_video_urls(obj):
    urls = []
    if isinstance(obj, dict):
        for value in obj.values():
            urls.extend(collect_video_urls(value))
    elif isinstance(obj, list):
        for value in obj:
            urls.extend(collect_video_urls(value))
    elif isinstance(obj, str):
        if re.search(r"(mp4|video|stream|vod)", obj, re.I) and obj.startswith(("http://", "https://")):
            urls.append(obj)
    deduped = []
    seen = set()
    for url in urls:
        if url not in seen:
            seen.add(url)
            deduped.append(url)
    return deduped


def interaction_text(interact):
    pairs = [
        ("点赞数", interact.get("likedCount")),
        ("收藏数", interact.get("collectedCount")),
        ("评论数", interact.get("commentCount")),
        ("分享数", interact.get("shareCount")),
    ]
    parts = [f"{k}: {v}" for k, v in pairs if v is not None and str(v) != ""]
    return "；".join(parts) if parts else "未公开/未抓到"


def extension_from_content_type(content_type, fallback):
    if content_type == "image/png":
        return ".png"
    if content_type == "image/webp":
        return ".webp"
    if content_type == "video/mp4":
        return ".mp4"
    if content_type == "image/jpeg":
        return ".jpg"
    return fallback


def download_media(urls, output_dir, note_dir, prefix, referer, skip):
    files = []
    if skip:
        return files
    for index, media_url in enumerate(urls, start=1):
        fallback = ".mp4" if prefix == "video" else ".jpg"
        try:
            _, data, content_type = fetch(media_url, referer=referer)
            ext = extension_from_content_type(content_type, fallback)
            path = note_dir / f"{prefix}-{index}{ext}"
            path.write_bytes(data)
            files.append(str(path.relative_to(output_dir)))
            time.sleep(0.15)
        except (HTTPError, URLError, TimeoutError) as exc:
            print(f"warning: failed to download {media_url}: {exc}", file=sys.stderr)
    return files


def crawl_one(url, output_dir, skip_media):
    final_url, data, _ = fetch(url)
    html = data.decode("utf-8", errors="replace")
    guessed_id = note_id_from_url(final_url)
    state = extract_initial_state(html)
    note_id, note = first_note_detail(state, guessed_id)

    note_dir = output_dir / note_id
    note_dir.mkdir(parents=True, exist_ok=True)
    (note_dir / "page.html").write_text(html, encoding="utf-8")

    image_urls = [pick_image_url(img) for img in (note.get("imageList") or [])]
    image_urls = [u for u in image_urls if u]
    video_urls = collect_video_urls(note.get("video") or note.get("videoInfo") or {})

    note_type = "视频" if (note.get("type") == "video" or video_urls) else ("多图" if len(image_urls) > 1 else "单图")
    media_files = []
    media_files.extend(download_media(image_urls, output_dir, note_dir, "image", final_url, skip_media))
    media_files.extend(download_media(video_urls[:1], output_dir, note_dir, "video", final_url, skip_media))

    return {
        "id": note_id,
        "title": note.get("title") or "",
        "desc": note.get("desc") or "",
        "type": note_type,
        "interaction": interaction_text(note.get("interactInfo") or {}),
        "author": ((note.get("user") or {}).get("nickname")) or "",
        "sourceUrl": f"https://www.xiaohongshu.com/discovery/item/{note_id}",
        "resolvedUrl": strip_query(final_url),
        "imageUrls": image_urls,
        "videoUrls": video_urls,
        "mediaFiles": media_files,
    }


def main():
    parser = argparse.ArgumentParser(description="Crawl Xiaohongshu notes and download media.")
    parser.add_argument("urls", nargs="+", help="xhslink.com or xiaohongshu.com note URLs")
    parser.add_argument("--output-dir", required=True, help="Directory for HTML, media, and records JSON")
    parser.add_argument("--records-name", default="records.json", help="Output JSON filename")
    parser.add_argument("--skip-media", action="store_true", help="Only parse metadata; do not download media")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for url in args.urls:
        try:
            records.append(crawl_one(url, output_dir, args.skip_media))
        except Exception as exc:
            print(f"error: failed to crawl {url}: {exc}", file=sys.stderr)
            records.append({"inputUrl": url, "error": str(exc)})

    out_path = output_dir / args.records_name
    out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(records, ensure_ascii=False, indent=2))
    print(f"\nWrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
