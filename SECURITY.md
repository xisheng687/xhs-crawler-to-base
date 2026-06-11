# 安全与隐私

请不要提交、公开或转发以下内容：

- 飞书 / Lark token、webhook、Base 链接、用户域名、app ID、app secret 或其他密钥
- 小红书 cookie、浏览器会话数据、账号态请求参数或真实 `xsec_token`
- 真实客户的 `records.json`、下载媒体、页面 HTML、数据库或日志
- 本机绝对路径、个人邮箱、手机号、客户名称或内部项目名称
- 任何可能还原真实业务场景、客户数据或私有账号状态的信息

## 推荐做法

- 使用 `xhs-output/` 或 `xhs-crawl/` 作为输出目录；这些目录已被 `.gitignore` 忽略。
- 不要把真实 webhook、token 或 Base 链接写进 issue、README、示例、提交记录或共享聊天。
- 优先使用本机已授权 CLI、环境变量或密钥管理器保存第三方服务凭证。
- 分享问题时，请使用脱敏后的示例链接、示例字段和示例输出。
- 如果需要提交测试文件，请只提交人工构造的最小样本，不要提交真实抓取结果。

## 发布前检查

发布或提交前，建议运行：

```bash
git status --short
git status --ignored --short
git grep -nE '(<LOCAL_HOME>|<BASE_URL>|<APP_TOKEN>|<TABLE_ID>|<RECORD_ID>|<FIELD_ID>|<VIEW_ID>|webhook|token|secret|cookie|Authorization|Bearer|xsec_token)'
find . -type f -maxdepth 4 | sort
```

也建议检查 Git 历史中是否误提交过敏感信息：

```bash
git log --format='%h %an <%ae> %s' --all
git grep -n -I -E '(token|secret|cookie|Authorization|Bearer|webhook|xsec_token|app_token|table_id|record_id|/Users)' $(git rev-list --all)
```

## 如果已经泄露

如果不小心公开了 token、cookie、webhook、Base 链接或其他密钥：

1. 立即在对应平台吊销或轮换密钥。
2. 检查是否有异常访问、异常记录写入或异常下载。
3. 从公开仓库中删除相关内容。
4. 如需彻底移除 Git 历史中的敏感内容，使用历史重写工具处理后强推，并提醒所有协作者重新克隆。

如果发现本仓库存在安全问题，请通过 GitHub issue 提交脱敏后的复现说明；不要在 issue 中粘贴真实密钥、真实客户数据或真实私有链接。
