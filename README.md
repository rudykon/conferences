<img src="assets/logo.svg" alt="会议论文导航标志" width="72">

# 会议论文导航

一个可离线使用的会议论文检索网页，支持按会议、年份和研究主题浏览论文，并切换中英文标题和摘要。

## 收录范围

| 会议 | 年份 | 论文数 | 范围 |
| --- | --- | ---: | --- |
| WWW | 2026 | 950 | 研究、产业、短论文及社会公益论文 |
| ICDE | 2026 | 261 | 官方录用的研究论文 |
| CVPR | 2026 | 4,042 | CVF 官方主会论文 |
| ACL | 2026 | 4,812 | 主会长短论文、产业、系统演示、学生研究、教程和 Findings |

中文标题和摘要包含机器翻译或整理内容，仅供辅助阅读。部分论文缺少摘要或原文链接；WWW 2026 当前数据未收录英文摘要。论文内容和发表信息请以原文及出版方页面为准。

主要来源：[WWW 2026 录用论文](https://www2026.thewebconf.org/accepted/research-tracks.html)、[ICDE 2026 录用论文](https://icde2026.github.io/accepted-papers.html)、[CVPR 2026 论文目录](https://openaccess.thecvf.com/CVPR2026?day=all)、[ACL 2026 论文目录](https://aclanthology.org/events/acl-2026/)。

ACL 2026 论文元数据和英文摘要来自 ACL Anthology，原始内容版权归 ACL 及相应权利人所有，按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 授权使用。中文标题和完整中文摘要使用 HY-MT1.5 机器翻译，部分术语经校正。主题基于标题和摘要自动分类，并非官方分类；翻译、导读及分类均可能有误。每篇记录保留作者、原文和许可链接。第三方来源与许可见 [许可说明](docs/third-party-notices.md)，尚需复核的译文检查项见 [ACL 2026 翻译核查清单](docs/acl-2026-translation-review.md)。

## 使用

下载或克隆仓库后，双击 `index.html` 即可使用。检索、筛选和切换会议无需联网；打开论文原文或来源链接需要联网。

网页按需加载 `assets/` 中对应会议的数据，请保持 `index.html` 和 `assets/` 的相对位置不变。页面支持搜索中英文标题、作者、摘要和主题，以及按主题、论文类型和摘要状态筛选。

## 更新数据

`data/` 中每个会议年份对应一个 JSON 文件，例如 `WWW-2026.json`。新增或修改数据后，在项目目录运行：

```bash
python update_data.py --sync
```

该命令会校验格式，更新网页中的会议目录，并重新生成 `assets/` 中的离线数据文件。只需检查数据时运行：

```bash
python update_data.py
```

脚本使用 Python 标准库。提交更新时，请同时提交修改过的 `data/`、生成的 `assets/` 和 `index.html`。字段、命名规则和新增会议的方法见 [数据格式说明](docs/data-format.md)。

## 项目结构

```text
├── index.html              # 网页入口
├── data/                   # 按会议和年份存放的论文数据
├── assets/                 # 由脚本生成的离线加载数据
├── docs/data-format.md     # 数据格式说明
├── papers.schema.json      # JSON Schema
└── update_data.py          # 数据校验与资源生成
```
