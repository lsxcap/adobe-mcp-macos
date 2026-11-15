# PS / AI 连 Codex 画图

把这个链接发给 Codex，让它帮你安装；安装完成后，可以用中文指令操作 Photoshop 或 Adobe Illustrator。

**这里的 AI 指 Adobe Illustrator。本仓库仅适用于 macOS，不包含 Adobe 软件，也不是 Adobe 官方产品。**

## 复制给 Codex

> 根据 https://github.com/lsxcap/adobe-mcp-macos 的 README 和 INSTALL.md，帮我安装 Photoshop MCP。先检查环境，保留已有配置，安装后测试连接。

> 根据 https://github.com/lsxcap/adobe-mcp-macos 的 README 和 INSTALL.md，帮我安装 Adobe Illustrator MCP。使用正式版，不使用 Beta，安装后测试连接。

想两个都装：把最后的需求改为“安装 PS 和 Illustrator 两个 MCP”。

## 准备条件

- Mac，已安装并可正常使用的 Photoshop / Illustrator 正式版。
- Node.js 22+、npm、Python 3、Codex。
- 可以访问 GitHub 和 npm；Adobe 登录及 macOS 自动化授权需要本人完成。

## 安装

让 Codex 阅读 [安装指南](INSTALL.md)。也可以下载本仓库 ZIP，解压后在目录内运行：

```sh
python3 install.py ps --check
python3 install.py ps
# Illustrator：
python3 install.py ai --check
python3 install.py ai
```

若检测到多个正式版，使用 `--app "/Applications/对应版本/Adobe Illustrator.app"` 明确选择。

安装不会画图、保存或关闭文档。若同名 MCP 或安装目录已经存在，会停止并保留原配置。完成后重启 Codex，开启新对话，要求检查连接状态和工具列表。

## 使用示例

- PS：“在当前画布中央，新建图层画一颗金黄色五角星。”
- Illustrator：“在当前画板中央画一个可编辑的矢量五角星。”
- “先列出当前文档和图层，再告诉我可以做什么。”

## 实测范围与限制

2026-11-16 在 Apple Silicon Mac 上测试：Photoshop 2026 连接、128 个工具列表及独立图层五角星；Illustrator 2026 30.3.0 连接、17 个工具列表及原生矢量五角星。**没有完整验证所有工具、批处理及导出格式，也没有验证 Intel Mac。**

Illustrator Mac 版是本地适配：保留上游绘图逻辑，用 AppleScript 代替 PowerShell / COM，并支持 macOS 文件路径。首次调用可能触发系统自动化授权。安装后的实际连接验证会访问 Adobe 应用；应用未启动时可能启动。

固定上游版本以便复现；不是自动跟随最新版。Illustrator 原包依赖曾报告 9 项漏洞（5 moderate / 4 high），尚未完成逐项可利用性分析；不要将本地服务暴露到公网，不建议处理不可信文件。更新依赖前应重新做兼容测试。

## 来源与许可

- Photoshop：[alisaitteke/photoshop-mcp](https://github.com/alisaitteke/photoshop-mcp)，MIT；安装固定 npm 版本 1.7.38，不在此仓库复制其源码。
- Illustrator：[changhaozhang663-shaxia/codex-science-figure-mcp](https://github.com/changhaozhang663-shaxia/codex-science-figure-mcp/releases/tag/v2026.10.02)，0.2.0 Windows 分享包。本仓库不重新分发原包、源码或第三方依赖；安装时从原作者发布页下载，验证 SHA-256，再在本机适配。未发现上游原创代码的明确再分发许可，不能把本仓库的 MIT 许可理解为对上游的授权。
- 本仓库自行编写的安装程序、Mac 通道和文档采用 MIT，见 LICENSE。

## 卸载

```sh
codex mcp remove photoshop
codex mcp remove illustrator-local
```

仅移除需要卸载的连接。软件位于 `~/.local/share/adobe-mcp-macos/ps` 或 `ai`；删除前检查是否有自己需要保留的运行记录。不会卸载 Adobe 软件。
