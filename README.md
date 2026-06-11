# xhs-crawler-to-base

## 中文说明

这是一个面向 WorkBuddy / Codex 的轻量工作流 Skill：把小红书 / RedNote 笔记链接解析成结构化数据，下载公开页面里可见的图片或视频，并可继续交给已授权的飞书 / Lark 环境写入多维表格。

它不是完整原创爬虫生态，也不内置任何私有账号、cookie、飞书 token 或 Base 地址。直接创建多维表格、上传附件等动作，需要使用者自己的飞书 / Lark 授权、CLI、API 或自动化入口。

### 给客户的最简单用法

1. 打开自己的 WorkBuddy 或 Codex。
2. 把这个仓库里的 `skills/xhs-crawler-to-base` 完整提供给它，并说：`帮我安装这个 skill`。
3. 安装后直接给一条或多条小红书链接，例如：`帮我采集这条小红书笔记，下载图片，并整理成飞书多维表格记录：<小红书链接>`。

如果客户只想先测试，不接飞书，也可以说：`先只生成 records.json，不写入飞书`。

### 能做什么

- 接收 `xhslink.com` 或 `xiaohongshu.com` 笔记链接。
- 解析公开页面里的 `window.__INITIAL_STATE__`。
- 提取标题、正文、类型、互动数、作者昵称、图片 / 视频 URL。
- 下载公开页面暴露的媒体文件。
- 输出标准化 `records.json`。
- 在已授权环境中，引导 agent 把记录和附件写入飞书 / Lark Base。

### 本地脚本测试

```bash
python3 scripts/crawl_xhs_notes.py \
  --output-dir ./xhs-output/batch-001 \
  "http://xhslink.com/o/example"
```

输出示例：

```text
xhs-output/batch-001/
├── records.json
└── <note-id>/
    ├── page.html
    ├── image-1.jpg
    └── image-2.jpg
```

记录示例：

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

### 隐私提醒

不要公开提交真实客户的 `records.json`、下载图片 / 视频、cookie、飞书 / Lark token、Base 链接、webhook、用户域名或本机绝对路径。

## English

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

For WorkBuddy or Codex users:

1. Open your own WorkBuddy or Codex.
2. Provide the full `skills/xhs-crawler-to-base` folder and say: `Install this skill for me`.
3. After installation, send a Xiaohongshu / RedNote link and ask: `Crawl this note, download the media, and prepare Feishu/Lark Base records`.

For a local script test:

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
