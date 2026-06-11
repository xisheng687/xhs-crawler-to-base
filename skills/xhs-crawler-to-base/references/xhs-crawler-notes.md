# Notes

- Short links from `xhslink.com` should be resolved with browser-like headers.
- Image notes can make `yt-dlp` report `No video formats found`; this is expected if page-state parsing works.
- Public HTML usually embeds `window.__INITIAL_STATE__` with `note.noteDetailMap`.
- Engagement fields may be empty strings when hidden; preserve uncertainty as `未公开/未抓到`.
- Feishu Base attachment cells cannot be written as ordinary record values.
- For large batches, create records in batches of at most 200 and upload attachments record-by-record.
