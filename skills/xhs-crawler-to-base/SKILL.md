---
name: xhs-crawler-to-base
description: "Crawl Xiaohongshu/RedNote notes from xhslink.com or xiaohongshu.com links, extracting title, body text, note type, engagement counts, images/videos, and optional Feishu/Lark Base insertion with attachment uploads. Use when the user asks to 爬取/采集/下载 小红书笔记, xhslink links, 小红书图片/视频, or store 小红书 notes into 飞书多维表格/Base."
---

# Xiaohongshu Notes To Feishu Base

## Attribution First

This skill is a lightweight workflow wrapper. It does not claim to be a full original crawler.

It relies on:

- public Xiaohongshu/RedNote page-state data in `window.__INITIAL_STATE__`
- browser-like HTTP requests
- Feishu/Lark Base APIs or `lark-cli` for table and attachment work
- `yt-dlp` as a useful reference/helper for media URL workflows
- XHS-Downloader as a dedicated upstream project worth considering when heavier Xiaohongshu crawling is needed

Default to the lean page-state method. Use external crawlers only when that route fails or the user explicitly needs account/search-scale crawling.

## Core Workflow

1. Extract all `xhslink.com` / `xiaohongshu.com` note URLs from the user message.
2. Run the bundled crawler script to resolve short links, parse page state, download media, and emit structured JSON.
3. Inspect the JSON for `title`, `desc`, `type`, `interaction`, `imageUrls`, `videoUrls`, and `mediaFiles`.
4. If the user wants Feishu Base output:
   - Create or locate a Base/table.
   - Prefer separate numeric fields for `点赞数`, `收藏数`, `评论数`, and `分享数`.
   - Write text/select/number fields first.
   - Upload media files to the attachment field after records are created.
   - Create a gallery view when the user wants a visual browsing experience.
5. Verify the result by reading the table records and views.

## Crawler Script

Use the script bundled with this skill:

```bash
python3 <path-to-this-skill>/scripts/crawl_xhs_notes.py \
  --output-dir xhs-crawl/<batch-name> \
  "http://xhslink.com/o/..." \
  "https://www.xiaohongshu.com/discovery/item/..."
```

Outputs:

- `records.json`: normalized records.
- `<note_id>/page.html`: fetched HTML for debugging.
- `<note_id>/image-1.jpg`, `<note_id>/video-1.mp4`, etc.: downloaded media.

If a value is hidden, write `未公开/未抓到` rather than inventing it.

## Feishu Base Fields

Recommended schema:

```json
[
  {"name":"标题","type":"text"},
  {"name":"正文内容","type":"text"},
  {"name":"类型","type":"select","multiple":false,"options":[
    {"name":"单图","hue":"Green","lightness":"Light"},
    {"name":"多图","hue":"Blue","lightness":"Light"},
    {"name":"视频","hue":"Purple","lightness":"Light"}
  ]},
  {"name":"点赞数","type":"number","style":{"type":"plain","precision":0,"thousands_separator":true}},
  {"name":"收藏数","type":"number","style":{"type":"plain","precision":0,"thousands_separator":true}},
  {"name":"评论数","type":"number","style":{"type":"plain","precision":0,"thousands_separator":true}},
  {"name":"分享数","type":"number","style":{"type":"plain","precision":0,"thousands_separator":true}},
  {"name":"附件","type":"attachment"}
]
```

If the user provides their own Feishu/Lark webhook or automation endpoint as a default authorization path, use it when appropriate to trigger table creation or downstream notifications. For direct Base creation, record writes, and attachment uploads, use an authenticated Feishu/Lark API or CLI session.

## Attachment And Gallery View

- Do not write attachment cells as ordinary record values.
- Create records first, then upload attachments using the returned record IDs.
- Use relative file paths for attachment upload commands.
- For visual browsing, create a `gallery` view and set the card cover field to the attachment field.

## Safety

Before sharing or committing outputs:

- Exclude real `records.json`, downloaded media, cookies, tokens, Feishu Base URLs, user domains, and webhooks.
- Do not include local absolute paths from the user's machine.
- Keep only generic examples in public documentation.
