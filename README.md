# xhs-crawler-to-base

> This project is a thin workflow wrapper, not an original crawler ecosystem.
>
> It stands on existing tools, public web behavior, and platform APIs. The heavy lifting belongs to the original authors and platforms. In particular:
>
> - Xiaohongshu/RedNote public web pages expose note data in `window.__INITIAL_STATE__`.
> - [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) is an excellent reference and helper for resolving media-oriented URLs.
> - [`XHS-Downloader`](https://github.com/JoeanAmier/XHS-Downloader) is a dedicated Xiaohongshu downloader/crawler project and inspired the “normalize note metadata + media files” workflow.
> - Feishu/Lark Base creation and attachment upload are handled through `lark-cli` / Feishu Open Platform capabilities.
>
> This repository only packages a small, practical method: resolve shared Xiaohongshu links, parse public page-state data, download exposed media, normalize records, and optionally guide an agent to write those records into Feishu Base. Be conservative about credit: roughly 90% of the value belongs to the upstream tool authors, platform APIs, and public web behavior; this repo is mainly glue, documentation, and minor workflow polish.

## What It Does

- Accepts `xhslink.com` or `xiaohongshu.com` note URLs.
- Resolves short links with browser-like headers.
- Parses `window.__INITIAL_STATE__` from the public note page.
- Extracts:
  - title
  - body text
  - note type: `单图`, `多图`, or `视频`
  - engagement counts: likes, collects, comments, shares
  - author nickname when visible
  - image/video URLs when present
- Downloads exposed media files.
- Emits a normalized `records.json`.
- Includes a reusable Codex skill that can write records into Feishu/Lark Base with attachments.

## Quick Start

```bash
python3 scripts/crawl_xhs_notes.py \
  --output-dir ./xhs-output/batch-001 \
  "http://xhslink.com/o/example"
```

Output:

```text
xhs-output/batch-001/
├── records.json
└── <note-id>/
    ├── page.html
    ├── image-1.jpg
    └── image-2.jpg
```

Example record:

```json
{
  "id": "note id",
  "title": "note title",
  "desc": "body text",
  "type": "多图",
  "interaction": "点赞数: 145；收藏数: 94；评论数: 498；分享数: 62",
  "author": "nickname",
  "sourceUrl": "https://www.xiaohongshu.com/discovery/item/<id>",
  "imageUrls": [],
  "videoUrls": [],
  "mediaFiles": []
}
```

## Codex Skill

The reusable skill lives at:

```text
skills/xhs-crawler-to-base/
```

Install it by copying that folder into your Codex skills directory, for example:

```bash
mkdir -p ~/.codex/skills
cp -R skills/xhs-crawler-to-base ~/.codex/skills/
```

Trigger examples:

- “爬取这些小红书链接，下载图片，并写入飞书多维表格”
- “把这批 xhslink 笔记采集成 records.json”
- “抓小红书笔记标题、正文、互动数、图片附件”

## Feishu/Lark Base Workflow

The script itself only crawls and downloads. For Feishu/Lark Base automation, use your own authorized credentials.

Recommended fields:

- `标题`
- `正文内容`
- `类型`
- `点赞数`
- `收藏数`
- `评论数`
- `分享数`
- `附件`

The skill includes prompts for agents to create a Base table, write rows, and upload attachments through `lark-cli`.

If your environment supports a Feishu/Lark webhook or automation endpoint, you can provide it as a default authorization channel. The agent can then use that endpoint to trigger Base creation or notify downstream workflows. For direct Base creation and attachment upload, an authenticated Feishu/Lark API or CLI setup is still required.

## Method Priority

Use the simplest working method first:

1. Public page-state parsing from `window.__INITIAL_STATE__`.
2. `yt-dlp` as a helper/reference for URL handling or video cases.
3. Dedicated projects such as XHS-Downloader when page-state parsing fails or when account/search-scale crawling is needed.

## Privacy Notes

Before publishing or sharing crawled output:

- Do not commit `records.json` from real customer work.
- Do not commit downloaded media from private or sensitive tasks.
- Do not commit Feishu/Lark tokens, Base URLs, user domains, webhook URLs, cookies, or browser session data.
- Treat Xiaohongshu content rights and platform terms seriously.

## License

This repository is released under the MIT License for the original glue code and documentation here. It does not relicense upstream projects or platform APIs. Respect the licenses and terms of the tools and services you use with it.
