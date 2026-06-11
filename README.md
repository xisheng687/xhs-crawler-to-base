# xhs-crawler-to-base

这是一个面向 WorkBuddy / Codex 的轻量工作流 Skill，用来把小红书 / RedNote 笔记链接解析成结构化数据，下载公开页面中可见的图片或视频，并在已授权环境中继续整理到飞书 / Lark 多维表格。

这个项目不是完整原创爬虫生态，也不内置任何私有账号、cookie、飞书 token、Base 链接或 webhook。它主要做的是把公开页面状态、媒体下载、结构化记录和飞书多维表格写入流程串起来。

## 项目定位

本仓库主要依赖这些公开能力和上游工具思路：

- 小红书 / RedNote 公开网页中的 `window.__INITIAL_STATE__` 页面状态数据。
- 浏览器风格的 HTTP 请求，用于解析短链接和读取公开页面。
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) 在媒体 URL 处理方面的经验和参考。
- [`XHS-Downloader`](https://github.com/JoeanAmier/XHS-Downloader) 对“小红书笔记元数据 + 媒体文件”工作流的启发。
- 飞书 / Lark Open Platform、`lark-cli` 或使用者自己的自动化入口，用于创建多维表格、写入记录和上传附件。

请保守理解这个项目的价值边界：大部分能力来自上游工具作者、平台 API 和公开 Web 行为；本仓库主要提供轻量封装、流程说明和少量工作流打磨。

## 最简单用法

1. 打开自己的 WorkBuddy 或 Codex。
2. 说：`帮我安装这个 skill：https://github.com/xisheng687/xhs-crawler-to-base`。
3. 安装后直接给一条或多条小红书链接，例如：`帮我采集这条小红书笔记，下载图片，并整理成飞书多维表格记录：<小红书链接>`。

## 能做什么

- 接收 `xhslink.com` 或 `xiaohongshu.com` 笔记链接。
- 解析短链接，读取公开笔记页面。
- 提取标题、正文、笔记类型、互动数、作者昵称、图片 URL 和视频 URL。
- 下载公开页面中暴露的图片或视频文件。
- 输出标准化的 `records.json`。
- 在使用者已授权的飞书 / Lark 环境中，引导 agent 创建多维表格、写入记录并上传附件。

## 本地脚本测试

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
  "resolvedUrl": "https://www.xiaohongshu.com/discovery/item/<id>",
  "imageUrls": [],
  "videoUrls": [],
  "mediaFiles": []
}
```

## 安装 Skill

可复用的 Skill 位于：

```text
skills/xhs-crawler-to-base/
```

如果手动安装到 Codex，可以复制到本机 skills 目录：

```bash
mkdir -p ~/.codex/skills
cp -R skills/xhs-crawler-to-base ~/.codex/skills/
```

安装后可以这样触发：

- `爬取这些小红书链接，下载图片，并写入飞书多维表格`
- `把这批 xhslink 笔记采集成 records.json`
- `抓小红书笔记标题、正文、互动数、图片附件`

## 飞书 / Lark 多维表格说明

脚本本身只负责采集公开页面和下载媒体。创建飞书 / Lark 多维表格、写入记录、上传附件，需要使用者自己的授权环境。

推荐字段：

- `标题`
- `正文内容`
- `类型`
- `点赞数`
- `收藏数`
- `评论数`
- `分享数`
- `附件`

如果使用者提供了自己的飞书 / Lark webhook 或自动化入口，agent 可以优先使用它触发表格创建或后续通知。直接创建 Base、写入记录和上传附件，仍然需要已授权的飞书 / Lark API、CLI 或等价能力。

## 方法优先级

默认使用最轻的方法：

1. 优先解析公开页面里的 `window.__INITIAL_STATE__`。
2. 遇到视频或 URL 处理问题时，再参考或调用 `yt-dlp`。
3. 当公开页面状态不可用，或者需要账号态、搜索级、批量级采集时，再考虑 XHS-Downloader 等更完整的上游项目。

如果某个字段不可见或无法抓到，应写成 `未公开/未抓到`，不要自行编造。

## 隐私和安全

公开、提交或转发结果前，请不要包含：

- 真实客户的 `records.json`
- 下载到本地的真实图片或视频
- 小红书 cookie 或浏览器会话数据
- 飞书 / Lark token、Base 链接、webhook、用户域名、app ID 或 app secret
- 本机绝对路径

仓库已经默认忽略 `xhs-output/`、`xhs-crawl/`、`records.json`、常见媒体文件、`.env`、cookie 和数据库文件。

## 许可证

本仓库中的轻量封装代码和文档使用 MIT License。它不会重新授权上游项目、平台 API 或平台内容。使用时请遵守相关工具许可证、平台规则和内容权益要求。
