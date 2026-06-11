# Security And Privacy

Do not commit:

- Feishu/Lark tokens, webhooks, Base URLs, user domains, app IDs, or app secrets
- Xiaohongshu cookies or browser session data
- real customer crawl outputs
- downloaded images or videos from private tasks
- local absolute paths from a user's machine

Before publishing, run both:

```bash
git status --short
git grep -nE '(<LOCAL_HOME>|<BASE_URL>|<APP_TOKEN>|<TABLE_ID>|<RECORD_ID>|<FIELD_ID>|<VIEW_ID>|webhook|token|secret|cookie|Authorization|Bearer)'
find . -type f -maxdepth 4 | sort
```
