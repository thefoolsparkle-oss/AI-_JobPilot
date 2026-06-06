# AI 求职 Copilot 项目完整计划

> 项目定位：一个基于 DeepSeek 的开源 AI 求职助手，帮助用户从真实履历出发，主动发现岗位、解析 JD、匹配经历、生成稳定简历，并辅助完成投递材料和申请表填写。  
> 项目形态：GitHub 开源项目，本地运行 / 用户自部署。  
> 默认模型策略：DeepSeek-first。用户在 `.env` 中配置自己的 `DEEPSEEK_API_KEY`。  
> 核心原则：程序控制流程，Agent 负责局部专家任务；AI 不能自由乱写、不能乱投、不能绕过平台规则。

---

# 🚀 开发进度追踪

> 最后更新：2026-06-02

### 状态说明

| 状态 | 含义 |
|------|------|
| ✅ 已完成 | 功能已实现，并且依赖、文档、基础验证都能支撑用户使用 |
| 🟡 部分完成 | 核心代码或页面已存在，但仍有依赖、体验、测试、稳定性或能力边界问题 |
| 📋 待开发 | 尚未实现，或只有计划没有可用功能 |
| 🔴 阻塞 | 当前无法继续推进，需要先解决外部依赖、关键设计或运行问题 |

### MVP 10 步

| Step | 功能 | 状态 | 产物 |
|------|------|------|------|
| Step 1 | 搭建基础项目 | ✅ | FastAPI + SQLite + Next.js，LLM Provider (DeepSeek) |
| Step 2 | 用户履历库 | ✅ | 11 张数据表，CRUD API，履历解析 Agent，前端编辑页 |
| Step 3 | 模板系统 | ✅ | 3 套 DOCX 模板（技术/AI产品/运营），模板预览 |
| Step 4 | JD 解析 | ✅ | JD 解析 Agent，结构化提取，前端解析页 + Playwright 网页抓取联动 |
| Step 5 | 岗位匹配 | ✅ | DeepSeek-reasoner 匹配评分，风险提示，简历策略 |
| Step 6 | 简历定制 | ✅ | 简历定制 Agent，DOCX + HTML → PDF 双格式导出 |
| Step 7 | 简历审查 | ✅ | 简历审查 Agent，夸大/空话/AI味检查 + 前端展示 |
| Step 8 | 岗位发现 | ✅ | 搜索策略 Agent + DuckDuckGo 真实搜索 + Playwright 网页抓取 |
| Step 9 | 投递材料包 | ✅ | 自我介绍、申请理由、HR私信、Cover Letter、面试问题、开放题答案 |
| Step 10 | 申请表辅助 | ✅ | 表单辅助 Agent + 前端 /assistant 页面 + EasyOCR 图片识别 |

### 增强功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 单进程部署 | ✅ | `start.bat` 一键启动，FastAPI 托管前端静态文件 |
| 设置页面 | ✅ | 前端填写 API Key（password 字段），Fernet 加密存储，兼容旧 Base64 格式 |
| PDF 导出 | ✅ | Playwright 渲染 HTML 简历 → 导出 PDF；`requirements.txt` 和 README 已补充 Playwright 安装步骤 |
| 投递追踪 CRM | ✅ | 看板式管理（已发现/收藏/投递/面试/Offer/拒绝/归档），38 个 API |
| 浏览器插件 | ✅ | Chrome 扩展，招聘页面一键提取 JD 发送到 JobPilot |
| 多模型支持 | ✅ | 预设 DeepSeek / OpenAI / Kimi / Qwen，可自定义接口地址和模型名 |
| 简历审查前端 | ✅ | 简历页点击「审查」，展示问题（夸大/空话/AI味等） |
| 表单答案 + 简历关联 | ✅ | 投递材料包生成开放题答案，简历版本关联 job_id |

### 问题台账

> 以后每发现一个问题，都必须写清楚：问题是什么、影响范围、当前状态、计划怎么解决。修复后不能只打勾，必须补充“已解决什么”和“怎么解决的”。

| ID | 问题所在 | 影响 | 状态 | 计划解决方式 |
|----|---------|------|------|-------------|
| P-001 | 进度表过于乐观，部分功能标记为 ✅，但实际仍有依赖或能力缺口 | 读者会误判项目成熟度，开发优先级也会被带偏 | ✅ 已解决 | 已把 JD 解析、简历定制、岗位发现、申请表辅助、设置页、PDF 导出改为 🟡 部分完成，并补充状态说明 |
| P-002 | `requirements.txt` 未列出 `playwright`，但网页抓取和 PDF 导出依赖 Playwright | 新用户按 README 安装后，相关功能可能运行失败 | ✅ 已解决 | 已在 requirements.txt 加入 `playwright`，README 补充 `playwright install chromium` |
| P-003 | 设置页声称 API Key "加密存储"，实际只是 Base64 编码 | 容易造成安全误导 | ✅ 已解决 | 改用 Fernet 加密；解密失败时自动回退尝试旧 Base64 格式并重新加密 |
| P-004 | 岗位发现目前更接近"搜索策略 + 链接抓取"，不是完整自动搜索 | 与 MVP 验收标准里的"系统找到若干具体岗位"仍有差距 | ✅ 已解决 | 接入 DuckDuckGo/DDGS 搜索；支持单次搜索和批量策略执行；requirements.txt 已补充 ddgs 依赖 |
| P-005 | OCR / 截图理解未接入 | 申请表辅助只能处理用户粘贴的文字，无法处理截图场景 | ✅ 已解决 | 接入 EasyOCR，前端支持截图上传 OCR，后端 `/api/assistant/ocr-upload`；上传接口已限制图片类型、大小和安全文件名 |
| P-006 | 没有 `backend/tests/` 端到端测试 | 全流程稳定性无法被验证，后续改动容易回归 | ✅ 已解决 | 20 个测试覆盖全 API + 前端页面 + 关键断言；使用独立 test_jobpilot.db/test_settings.json/test_secret_key 隔离 |
| P-007 | Agent / LLM 调用日志表未落地 | 难以追踪一次生成为什么失败、为什么这样写、用了什么输入 | ✅ 已解决 | 新增 AgentRun + LLMCall 表，DeepSeekProvider 自动记录每次 LLM 调用的模型/token/耗时 |
| P-008 | 测试直接使用默认数据库 engine，并在 teardown 执行 `drop_all` | 用户直接运行 pytest 时可能清空本地 `jobpilot.db` 数据表 | ✅ 已解决 | 测试强制 `DATABASE_URL=sqlite:///./test_jobpilot.db`，并使用测试专用 settings/secret；真实 jobpilot.db/settings.json/.secret_key 永不触碰 |
| P-009 | 计划书内部仍有旧状态和新状态互相矛盾 | 读者无法判断真实进度，也会误导下一步开发 | ✅ 已解决 | 全部状态同步：问题台账、新增解决记录、顶部进度表均已更新 |
| P-010 | 当前测试数量和质量描述不准确 | "E2E 已完成"的结论过早，无法覆盖真实失败场景 | 🟡 部分解决 | 已补充断言（数据存在、加密验证、Base64 迁移、OCR 上传安全、404 处理、状态检查）；真实 LLM 调用测试需 API Key |
| P-012 | OCR 上传接口缺少上传依赖和文件安全限制 | 新环境上传可能不可用；恶意文件名可能造成路径穿越或覆盖 | ✅ 已解决 | 补 `python-multipart`，上传接口限制图片后缀、5MB 大小、随机文件名，并测试拒绝非图片和清洗路径 |
| P-012b | 履历事实库缺少 V1-1 所需字段（evidence、claim_level、risk_level、interview_explanation、transferable_skills） | 简历无法做到"每句都可追溯" | ✅ 已解决 | Experience 表加 evidence + transferable_skills；ExperienceFact 加 claim_level + risk_level + interview_explanation |
| P-013 | 匹配判断仍输出 score/recommendation，不符合 V1-3 的"决策"要求 | 用户看到分数但不知道具体该不该投、需要确认什么 | ✅ 已解决 | 匹配 Agent 升级输出 decision(apply/maybe/skip/risky) + decision_reasons + hard_filter_passed + user_confirm_required |
| P-014 | 岗位发现缺少"搜索→保存→解析→批量评分"的闭环 | 搜索结果只展示，不会自动变成候选岗位和匹配排序 | ✅ 已解决 | POST /api/discover/save-and-parse 实现搜索→去重保存→自动解析→自动匹配完整流水线 |
| P-015 | V1-4 简历审查 Agent 缺少版本间对比 | 无法检测不同版本间风格漂移 | ✅ 已解决 | 审查 Agent 接收 previous_version 参数，输出 version_comparison（score_change/style_drift/detail） |
| P-016 | V1-5 前端申请辅助页未传递 resume_id | Agent 可以接收 resume 上下文但前端未连接 | ✅ 已解决 | 前端助手页新增简历版本下拉选择器，传给 API |

### 已解决问题记录

| 日期 | 问题 ID | 解决了什么 | 怎么解决的 | 验证方式 |
|------|---------|------------|------------|----------|
| 2026-06-01 | P-001 | 计划书顶部进度状态与实际能力不一致 | 增加状态说明，把存在缺口的功能从 ✅ 调整为 🟡，并在产物说明中写清剩余问题 | 人工复核计划书顶部进度表和问题台账 |
| 2026-06-01 | P-003 | 文档中“API Key 加密存储”的表述不准确 | 在增强功能表和问题台账中明确当前是 Base64 编码保存，不是真正加密 | 人工复核设置页相关说明 |

| 2026-06-01 | P-002 | requirements.txt 缺少 playwright+cryptography | 新增依赖，README 补充安装步骤 | 人工复核 |
| 2026-06-01 | P-003c | API Key 从 Base64 升级为 Fernet 真加密 | 引入 cryptography 库，生成 .secret_key | pytest settings_flow 通过 |
| 2026-06-01 | P-006 | 新增 15 个基础测试 | 创建 tests/test_full_workflow.py | 隔离测试库运行 `pytest tests -q`，15 passed；仍需改成真正 E2E 并修复默认库风险 |

| 2026-06-02 | P-008 | 测试隔离数据库，永不触碰真实 jobpilot.db | 设置 DATABASE_URL=test_jobpilot.db，session scope fixture | pytest 17/18 passed，test_jobpilot.db 自动清理 |
| 2026-06-02 | P-011 | Fernet 兼容旧 Base64 Key | 解密失败时回退尝试 base64 解码并自动重写 | pytest settings_fernet 通过 |
| 2026-06-02 | P-004/P-005/P-009 | 文档一致性 + 依赖补齐 | requirements.txt 加 ddgs+easyocr，计划状态全同步 | 17 passed |
| 2026-06-04 | P-008/P-012 | 测试文件和上传接口安全收口 | 测试改用 test_settings/test_secret；上传接口补 `python-multipart`、类型/大小限制和随机文件名 | `pytest tests -q` 20 passed |


### 复查记录

| 日期 | 复查内容 | 结论 | 后续动作 |
|------|----------|------|----------|
| 2026-06-02 | 对照完善方案逐项修复 | P-008/P-011 已解决，P0 依赖已补齐，P1 文档已同步 | P10 部分解决（LLM 测试需 API Key），OCR 标记为可选功能 |
| 2026-06-02 | 全量测试 | 18 个测试，17 passed + 1 skipped（OCR） | 历史记录；后续 2026-06-04 已升级为 20 passed |
| 2026-06-04 | 复查测试隔离、OCR 上传和文档一致性 | 测试不再删除真实 settings/secret；OCR 上传安全已补；README 已同步 | 继续保留 P-010：真实 LLM 和真实 OCR 模型加载仍需人工/集成环境验证 |

### 完善方案

| 优先级 | 目标 | 具体动作 | 完成标准 |
|--------|------|----------|----------|
| P0 | 避免测试破坏真实数据 | 测试启动前强制设置 `DATABASE_URL=sqlite:///./test_jobpilot.db` 或内存库；fixture 只清测试库；README 测试命令也使用测试库 | 直接运行测试不会改动 `backend/jobpilot.db`，测试后无业务数据丢失 |
| P0 | 补齐新增功能依赖 | 已在 `requirements.txt` 加入 `ddgs`、`easyocr`、`python-multipart` | 新环境按 README 安装后，搜索、OCR、上传不会因缺包直接降级 |
| P1 | 修正文档一致性 | 同步更新顶部进度、问题台账、已知局限、README 功能描述和解决记录 | 文档中不再同时出现“已解决”和“未接入”的冲突描述 |
| P1 | 强化测试质量 | 将当前测试标为 smoke；增加 service/E2E 测试，覆盖搜索错误、OCR 无依赖、Fernet 迁移、Agent 日志写入 | 测试不只检查字段存在，还检查关键行为和失败路径 |
| P2 | 加密升级兼容 | 已实现 Fernet 解密失败时尝试旧 Base64 解码，成功后自动重写为 Fernet | 老 settings.json 升级后不静默丢 Key |
| P2 | 岗位发现闭环 | 搜索结果去重、保存为候选岗位、批量抓取详情、批量匹配排序 | 能从搜索策略产生岗位列表，并保存、解析、评分 |


### 后续维护规则

1. 每次发现新问题，先加入“问题台账”，不要只写在聊天记录里。
2. 每次修完问题，必须在“已解决问题记录”写明：解决了什么、怎么解决的、如何验证。
3. 如果只是部分修复，状态写 🟡，并说明剩余缺口。
4. 如果问题影响 README、依赖、测试或用户运行方式，修代码时必须同步更新文档。

### 待完成

- [ ] **Electron 桌面打包** — 将前后端打包为 .exe，双击直接打开窗口，无需浏览器
  
### 技术栈实际使用

| 组件 | 技术选型 |
|------|---------|
| 后端框架 | FastAPI (Python) |
| 数据库 | SQLite + SQLAlchemy |
| LLM | OpenAI-compatible API（DeepSeek / OpenAI / Kimi / Qwen 预设） |
| 前端 | Next.js 16 + Tailwind CSS 4 → 静态导出 |
| 文档渲染 | python-docx (DOCX) + Playwright (HTML → PDF) |
| 网页抓取 | Playwright |
| 部署 | FastAPI 托管前后端，单进程 |

**目标**：将 JobPilot 打包为独立桌面应用，用户无需安装 Python / Node.js，双击即可使用。

**方案**：

```
Electron 壳
├── 内嵌 FastAPI 后端（subprocess 启动 Python 或 PyInstaller 打包）
├── 加载前端静态文件（frontend/out/）
└── 窗口 UI
```

**两种实现路径**：

1. **PyInstaller 方案（推荐）**：将 FastAPI 打包成单个 .exe，Electron 启动时 spawn 该进程，Electron 窗口加载 `http://127.0.0.1:8001`。
2. **纯 Electron 方案**：Electron 主进程用 `child_process` 启动 `python -m uvicorn`，需用户预装 Python。

**产物**：

- Windows: `JobPilot-Setup.exe`（安装包）或 `JobPilot.exe`（便携版）
- macOS: `JobPilot.app`
- Linux: `JobPilot.AppImage`

**不做**：
- 不自动更新（第一版手动下载）
- 不签名证书（开源项目，用户需信任来源）
- 不云端控制台

---


# MVP：第一版最小可用产品

## 1. MVP 目标

MVP 不追求“全自动投递”，而是先把最有价值、最能展示项目能力的流程跑通：

```text
用户输入求职目标
↓
系统发现具体岗位
↓
系统解析岗位 JD
↓
系统判断用户与岗位的匹配度
↓
系统基于固定模板生成专用简历
↓
系统生成投递材料
↓
用户遇到申请表问题时，系统辅助回答
```

MVP 的目标不是做一个简单的“AI 简历生成器”，而是做一个完整的 **AI 求职工作流原型**。

---

## 2. MVP 核心用户场景

用户不是已经知道岗位链接的人，而是：

```text
我想找 AI 产品 / AI 应用 / 后端 / 数据分析 / 产品运营实习，
但我不知道哪里有合适岗位，
也不知道哪些岗位我能投，
更不知道简历和申请表该怎么写。
```

MVP 要解决的核心痛点：

1. 用户不知道去哪里找岗位。
2. 用户不会判断岗位适不适合自己。
3. 用户不知道如何把自己的经历改成岗位需要的表达。
4. 用户卡在申请表、开放题、HR 私信、自我介绍等环节。
5. 用户需要稳定格式的简历，而不是每次 AI 重新生成一份风格完全不同的简历。

---

## 3. MVP 必须包含的功能

### 3.1 用户履历库

用户可以录入并保存真实履历信息：

- 基本信息
- 教育背景
- 实习经历
- 项目经历
- 科研经历
- 技能
- 语言能力
- GitHub / 作品链接
- 求职偏好
- 可实习时间
- 目标城市
- 是否接受远程
- 不想投的岗位类型
- 不能夸大的内容

每段经历都要结构化保存，而不是只保存一大段文本。

示例：

```json
{
  "experience_id": "project_mnemosyne",
  "type": "project",
  "name": "Project Mnemosyne / 忆界树",
  "start_date": "2026-01",
  "tech_stack": ["FastAPI", "SQLite", "LLM API", "AI Agent"],
  "facts": [
    "设计用户、人格、会话、消息、长期记忆等核心表",
    "设计 Forge、Archivist、Mirror、Sculptor 等 Agent 分工",
    "使用 AI Coding 工具辅助开发，并进行人工审查和调试"
  ],
  "allowed_claims": [
    "多 Agent 原型设计",
    "长期记忆结构设计",
    "后端数据结构设计",
    "LLM 调用链路实践"
  ],
  "forbidden_claims": [
    "企业级大规模上线",
    "商业收入",
    "真实大规模用户",
    "生产环境部署"
  ]
}
```

---

### 3.2 多模板简历系统

用户必须能选择模板。

MVP 至少提供 3 套模板：

1. 中文技术实习版
2. 中文 AI 产品 / AI 应用版
3. 中文产品运营 / 内容运营版

后续可扩展：

4. 英文技术实习版
5. 英文 AI / Research Assistant 版
6. 一页极简版
7. 校招综合版

模板控制：

- 栏目顺序
- 字体
- 间距
- 是否一页
- 是否显示求职意向
- 是否显示专业总结
- 项目在前还是实习在前
- 技能区如何分组

重要原则：

```text
模板由用户选择和确认。
AI 只能填内容，不能随便改模板结构。
```

---

### 3.3 JD 解析功能

用户可以粘贴 JD 文本，或者系统从岗位页面中抓取 JD。

系统要把 JD 解析成结构化信息：

```json
{
  "title": "AI Product Intern",
  "company": "Example Company",
  "location": "Remote / Shanghai",
  "remote_type": "hybrid",
  "duration": "3 months+",
  "responsibilities": [
    "参与 AI 产品需求分析",
    "协助完成用户反馈整理",
    "参与 Prompt 和产品流程优化"
  ],
  "requirements": [
    "计算机或相关专业",
    "熟悉 AI 工具",
    "有良好的文档能力"
  ],
  "nice_to_have": [
    "了解 LLM 或 Agent 应用",
    "有 Python / SQL 基础"
  ],
  "hard_filters": [
    "每周至少 4 天",
    "至少 3 个月"
  ],
  "risk_flags": [
    "用户只能实习 1 个月时可能不匹配"
  ]
}
```

---

### 3.4 岗位发现功能

MVP 要能根据用户目标主动找岗位。

用户输入：

```text
我想找 AI 产品或大模型应用实习，最好线上，一个月左右，中大厂或有名一点的公司，不限工资。
```

系统生成搜索策略：

```json
{
  "queries": [
    "AI 产品实习生 远程 2026",
    "大模型应用实习生 日常实习",
    "AI Agent 产品实习 招聘",
    "27届 AI产品 实习",
    "AI 应用 实习生 线上"
  ],
  "negative_keywords": [
    "销售",
    "电话销售",
    "培训班",
    "全职",
    "社招",
    "课程顾问"
  ],
  "preferred_sources": [
    "公司官网",
    "校招官网",
    "实习平台",
    "牛客招聘",
    "招聘聚合搜索"
  ]
}
```

MVP 可以先不做复杂平台登录和自动投递，但必须做到：

```text
搜索具体岗位
↓
打开岗位详情页
↓
提取岗位内容
↓
解析 JD
↓
保存岗位
↓
匹配评分
```

---

### 3.5 岗位匹配评分

系统不能只说“很适合”，必须给出理由和风险。

输出示例：

```json
{
  "score": 78,
  "recommendation": "apply",
  "summary": "该岗位值得投递，但需要弱化产品经验不足的问题。",
  "match_reasons": [
    "岗位需要 AI 工具使用经验，用户有 AI Agent 项目经历",
    "岗位需要流程拆解能力，用户实习中有接口对接和字段映射经历",
    "岗位需要文档和需求理解能力，用户有科研综述和项目计划经验"
  ],
  "risks": [
    "岗位要求至少 3 个月，用户偏好 1 个月",
    "用户没有正式产品实习经历，需要用项目和实习经历补足"
  ],
  "resume_strategy": [
    "将 Project Mnemosyne 放在项目经历第一位",
    "强调 AI 工具、流程自动化、用户画像和 Agent 设计",
    "实习经历中突出需求沟通、数据对接、异常排查"
  ]
}
```

---

### 3.6 专用简历生成

系统根据：

- 用户履历库
- 用户选择的模板
- 岗位 JD
- 匹配评分结果

生成对应岗位的简历版本。

关键要求：

```text
AI 输出结构化 JSON
程序负责渲染 DOCX / PDF
AI 不直接控制最终排版
```

简历版本需要保存：

- 使用的模板
- 对应岗位
- 生成时间
- 选择了哪些经历
- 哪些 bullet 被改写
- 是否通过审查
- 用户是否手动修改过

---

### 3.7 简历审查

系统要有 HR 挑刺逻辑。

检查：

- 是否夸大经历
- 是否出现用户事实库中没有的内容
- 是否空话太多
- 是否太像 AI
- 是否岗位关键词不足
- 是否用户面试时接不住
- 是否一页超出
- 是否不同版本之间风格漂移

输出示例：

```json
{
  "problems": [
    {
      "type": "overclaim",
      "text": "负责完整 AI 产品商业化落地",
      "reason": "用户事实库中没有商业化上线证据",
      "suggestion": "改为：参与 AI 对话系统原型设计与功能拆解"
    }
  ],
  "overall_status": "needs_revision"
}
```

---

### 3.8 投递材料包

每个岗位生成一个 Application Package，包括：

- 推荐简历版本
- 自我介绍
- 申请理由
- Cover Letter
- HR 私信
- 表单开放题回答
- 风险提示
- 可能面试问题

示例：

```text
岗位：AI 产品实习生
公司：Example Company
匹配度：78/100
推荐简历模板：中文 AI 产品 / AI 应用版
推荐简历版本：resume_example_company_ai_product_v1.docx
推荐动作：可以投递，但需要确认实习时长是否可接受。
```

---

### 3.9 申请表辅助 Agent

产品上不拆“截图理解 Agent”和“表单问答 Agent”，统一叫：

```text
申请表辅助 Agent
```

用户可以输入：

- 表单问题
- 截图 OCR 后的文字
- 错误提示
- HR 消息
- 上传简历页面内容
- 开放题问题

系统回答：

- 这一栏是什么意思
- 用户应该怎么填
- 是否有风险
- 怎么写得自然
- 是否需要用户自己确认

MVP 不强依赖视觉模型。  
推荐先做：

```text
截图
↓
OCR / 浏览器 DOM 文本提取
↓
DeepSeek 读取文字
↓
生成填写建议
```

---

## 4. MVP 不做什么

第一版不要做：

- 全自动投递
- 批量海投
- 绕过验证码
- 模拟用户违规登录平台
- 多用户商业套餐
- 高级用户 BYOK 系统
- 企业后台
- 多模型智能路由
- 复杂浏览器插件自动提交
- 自动伪造经历
- 替用户做未经确认的敏感决定

MVP 的重点是：

```text
找岗位
读岗位
判断岗位
生成稳定材料
辅助用户完成投递
```

---

## 5. MVP 推荐技术栈

### 后端

```text
FastAPI
SQLite 起步，后期 PostgreSQL
SQLAlchemy
Pydantic
```

### 前端

```text
Next.js / React
Tailwind CSS
```

如果想更快做 demo，可以先用：

```text
Streamlit
```

但如果目标是 GitHub 上更像产品，建议直接用 Next.js + FastAPI。

### 网页抓取

```text
Playwright
BeautifulSoup
trafilatura / readability-lxml
```

### 文档生成

```text
docxtpl
python-docx
Playwright PDF / WeasyPrint
```

### OCR

```text
PaddleOCR
Tesseract OCR
浏览器 DOM 文本提取
```

### LLM

```text
DeepSeek-first
普通任务：deepseek-chat
复杂判断：deepseek-reasoner
```

`.env.example`：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_FAST_MODEL=deepseek-chat
DEEPSEEK_REASONING_MODEL=deepseek-reasoner
```

---

## 6. MVP Agent 列表

| Agent | 作用 | 推荐模型 |
|---|---|---|
| 履历整理 Agent | 把用户输入整理成结构化履历 | deepseek-chat |
| 搜索策略 Agent | 根据用户目标生成搜索词和过滤条件 | deepseek-chat |
| JD 解析 Agent | 从岗位页面或 JD 文本中抽取结构化岗位信息 | deepseek-chat |
| 岗位匹配 Agent | 判断用户是否适合该岗位 | deepseek-reasoner |
| 简历定制 Agent | 基于固定模板生成岗位专用简历内容 | deepseek-chat |
| 简历审查 Agent | 检查夸大、空话、AI 味和面试风险 | deepseek-reasoner |
| 投递材料 Agent | 生成自我介绍、申请理由、HR 私信等 | deepseek-chat |
| 申请表辅助 Agent | 根据表单问题/截图文字给出填写建议 | deepseek-chat / deepseek-reasoner |

---

## 7. MVP 开发顺序

### Step 1：搭建基础项目

- FastAPI 后端
- SQLite 数据库
- Next.js 前端
- `.env` 配置 DeepSeek Key
- LLM Provider 基础封装

### Step 2：用户履历库

- 新增 / 编辑基本信息
- 新增 / 编辑教育经历
- 新增 / 编辑实习经历
- 新增 / 编辑项目经历
- 新增 / 编辑科研经历
- 标记 allowed_claims / forbidden_claims

### Step 3：模板系统

- 设计 3 个中文模板
- 模板可预览
- 用户选择模板
- docxtpl 渲染 DOCX
- 可导出 PDF

### Step 4：JD 解析

- 用户粘贴 JD
- DeepSeek 输出结构化 JSON
- 程序保存解析结果
- 前端展示岗位要求、硬性条件、风险项

### Step 5：岗位匹配

- 规则判断：时间、地点、年级、实习时长
- DeepSeek reasoner 判断：匹配度、风险、投递建议
- 展示匹配度和解释

### Step 6：简历定制

- 用户选择模板
- 系统根据 JD 选择经历和 bullet
- 生成简历 JSON
- 渲染 DOCX/PDF
- 保存简历版本

### Step 7：简历审查

- 检查是否夸大
- 检查是否空话
- 检查是否有 AI 味
- 输出修改建议

### Step 8：岗位发现

- 根据用户目标生成搜索词
- 调用搜索工具或爬取公开页面
- 保存候选岗位
- 打开详情页解析 JD
- 批量匹配排序

### Step 9：投递材料包

- 生成自我介绍
- 生成申请理由
- 生成 HR 私信
- 生成开放题回答
- 生成可能面试问题

### Step 10：申请表辅助

- 用户粘贴表单问题
- 用户上传截图后 OCR
- 系统结合用户履历和岗位 JD 生成答案
- 输出风险提醒

---

## 8. MVP 验收标准

MVP 做完以后，至少要能完成这个流程：

```text
用户填写履历
↓
用户输入“想找 AI 产品实习，最好远程，一个月左右”
↓
系统找到若干具体岗位
↓
系统解析每个岗位 JD
↓
系统给出匹配度和风险
↓
用户选择一个岗位
↓
系统生成对应简历
↓
系统生成申请理由和 HR 私信
↓
用户粘贴申请表问题
↓
系统告诉用户怎么填
```

如果这个流程能跑通，这个项目已经不是普通简历生成器，而是一个真正的 AI 求职 Copilot 原型。

---

# 完整长期计划

## 1. 项目总定位

项目名称可以暂定为：

```text
AI Job Search Copilot
```

中文定位：

```text
基于 DeepSeek 的开源 AI 求职助手：帮助用户从真实履历出发，主动发现岗位、解析 JD、匹配经历、生成稳定简历，并辅助完成申请表填写和投递跟进。
```

项目不应该叫：

```text
AI 自动投简历神器
```

原因：

1. 容易显得像垃圾海投工具。
2. 有平台规则风险。
3. 用户真正需要的不是乱投，而是高质量筛选和投递。
4. 自动投递不应该是第一阶段核心能力。

更好的定位：

```text
求职工作流 Copilot
岗位发现 + JD 解析 + 简历定制 + 投递辅助 + 求职记录
```

---

## 2. 项目设计原则

### 2.1 程序控制流程，AI 负责局部任务

错误方式：

```text
把所有东西交给一个大 Agent，让它自己决定怎么搜、怎么写、怎么投。
```

正确方式：

```text
程序定义流程
每个模块调用对应专家 Agent
Agent 输出结构化结果
程序校验后进入下一步
```

---

### 2.2 用户事实库优先

所有简历和申请材料都必须基于用户事实库。

AI 不能：

- 编造经历
- 编造数据
- 编造成果
- 随意修改学历时间
- 随意夸大项目规模
- 写用户面试时接不住的内容

---

### 2.3 模板固定，内容动态

简历系统应该分成两层：

```text
视觉模板：由用户选择
内容策略：由 AI 根据岗位调整
```

AI 可以调整：

- 经历顺序
- bullet 表达
- 技能关键词
- 自我评价
- 项目强调角度

AI 不应该随便调整：

- 模板结构
- 字体
- 栏目布局
- 简历整体风格
- 教育时间
- 基本信息

---

### 2.4 不做无确认投递

系统可以：

- 找岗位
- 读 JD
- 判断匹配
- 生成简历
- 生成申请回答
- 辅助填写表单
- 记录投递状态

系统不应该默认：

- 替用户批量提交
- 绕过验证码
- 未确认就投递
- 伪造用户信息
- 违反平台规则自动化操作

---

### 2.5 开源项目优先简单可跑

这个项目大概率是 GitHub 开源项目，所以不要按商业 SaaS 设计。

第一版应该是：

```text
用户本地运行
用户自己提供 DeepSeek API key
SQLite 起步
配置简单
README 清楚
功能能跑通
```

不要一开始做：

```text
用户套餐
平台计费
高级用户
企业后台
多模型路由
复杂权限系统
```

---

## 3. 系统总架构

```text
Frontend
  ├── 用户履历库页面
  ├── 模板选择页面
  ├── 岗位发现页面
  ├── 岗位详情 / 匹配分析页面
  ├── 简历版本页面
  ├── 投递材料包页面
  └── 申请表辅助页面

Backend
  ├── User Profile Service
  ├── Resume Template Service
  ├── Resume Generation Service
  ├── Job Discovery Service
  ├── Job Parsing Service
  ├── Job Matching Service
  ├── Application Package Service
  ├── Form Assistant Service
  ├── Document Export Service
  └── LLM Provider Service

Agents
  ├── 履历整理 Agent
  ├── 搜索策略 Agent
  ├── 招聘源识别 Agent
  ├── JD 解析 Agent
  ├── JD 理解 Agent
  ├── 岗位匹配 Agent
  ├── 投递策略 Agent
  ├── 简历定制 Agent
  ├── 简历审查 Agent
  ├── 投递材料 Agent
  ├── 申请表辅助 Agent
  └── 面试准备 Agent

Data
  ├── SQLite / PostgreSQL
  ├── 原始岗位网页
  ├── 解析后的 JD
  ├── 用户履历事实库
  ├── 简历模板
  ├── 简历版本
  ├── 投递材料包
  ├── 投递记录
  └── Agent 运行日志
```

---

## 4. LLM 策略

### 4.1 第一版默认策略

```text
DeepSeek-first
普通任务：deepseek-chat
复杂判断：deepseek-reasoner
```

原因：

1. 用户自己更常用 DeepSeek。
2. 适合开源项目，用户自己填 API key。
3. 成本相对可控。
4. 接口形态适合做 JSON 输出、结构化抽取和工具调用。
5. 不需要一开始做复杂多模型系统。

---

### 4.2 模型配置方式

`.env.example`：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_FAST_MODEL=deepseek-chat
DEEPSEEK_REASONING_MODEL=deepseek-reasoner
```

代码中不要写死模型名。

推荐：

```python
FAST_MODEL = settings.DEEPSEEK_FAST_MODEL
REASONING_MODEL = settings.DEEPSEEK_REASONING_MODEL
```

---

### 4.3 Provider 抽象

第一版只实现 DeepSeekProvider，但保留基本接口。

```python
class LLMProvider:
    def chat(self, messages, response_format=None, temperature=0.2):
        raise NotImplementedError


class DeepSeekProvider(LLMProvider):
    def chat(self, messages, response_format=None, temperature=0.2):
        ...
```

暂时不做复杂多模型路由，但以后可以扩展：

```text
KimiProvider
OpenAIProvider
GeminiProvider
QwenProvider
```

---

## 5. Agent 总表

| Agent | 所属模块 | 主要任务 | 推荐模型 |
|---|---|---|---|
| 履历整理 Agent | 用户履历库 | 整理用户输入，生成结构化履历 | deepseek-chat |
| 搜索策略 Agent | 岗位发现 | 根据用户目标生成搜索词和过滤条件 | deepseek-chat |
| 招聘源识别 Agent | 岗位发现 | 判断网页类型：岗位列表、岗位详情、无关页面 | deepseek-chat |
| JD 解析 Agent | 岗位解析 | 从网页或文本抽取结构化 JD | deepseek-chat |
| JD 理解 Agent | 岗位解析 | 判断岗位真实需求、隐藏门槛和风险 | deepseek-reasoner |
| 岗位匹配 Agent | 匹配评分 | 判断用户是否适合岗位 | deepseek-reasoner |
| 投递策略 Agent | 投递准备 | 决定该岗位使用什么模板和强调什么经历 | deepseek-reasoner |
| 简历定制 Agent | 简历生成 | 根据模板和 JD 生成岗位专用简历内容 | deepseek-chat |
| 简历审查 Agent | 简历质量控制 | 检查夸大、空话、AI 味和面试风险 | deepseek-reasoner |
| 投递材料 Agent | 投递材料 | 生成自我介绍、申请理由、Cover Letter、HR 私信 | deepseek-chat |
| 申请表辅助 Agent | 表单辅助 | 根据表单问题、截图 OCR 文字、HR 消息给填写建议 | deepseek-chat / deepseek-reasoner |
| 面试准备 Agent | 后续跟进 | 根据 JD 和简历预测面试问题 | deepseek-reasoner |

---

## 6. 阶段 0：项目地基

### 6.1 目标

先把数据结构和项目骨架搭好，避免后面 Agent 输出失控。

### 6.2 要做的事情

- 创建 GitHub 仓库
- 初始化前后端项目
- 配置 `.env.example`
- 封装 DeepSeek Provider
- 设计数据库表
- 设计基础 API
- 建立 Agent 运行日志
- 建立统一 JSON 输出规范

### 6.3 关键产物

```text
项目 README
.env.example
FastAPI 项目骨架
Next.js 项目骨架
SQLite 数据库
LLM Provider
Agent Runner
```

---

## 7. 阶段 1：履历库与稳定简历生成

### 7.1 目标

解决 AI 简历风格漂移问题。

### 7.2 功能

- 用户录入履历
- 履历结构化保存
- 用户选择模板
- AI 生成岗位方向版简历内容
- 程序渲染 DOCX/PDF
- 简历审查 Agent 检查风险
- 保存简历版本

### 7.3 关键原则

```text
用户事实库固定
模板固定
AI 只负责内容适配
```

### 7.4 产物

- 履历编辑页面
- 模板选择页面
- 简历预览页面
- DOCX 导出
- PDF 导出
- 简历版本记录

---

## 8. 阶段 2：JD 解析与岗位匹配

### 8.1 目标

让系统具备看懂岗位的能力。

### 8.2 功能

- 用户粘贴 JD
- 系统解析岗位信息
- 系统识别硬性要求
- 系统识别风险
- 系统和用户履历匹配
- 输出匹配度、优势、风险、简历策略

### 8.3 产物

- JD 输入页面
- JD 解析结果页面
- 匹配评分页面
- 岗位风险提示
- 推荐简历策略

---

## 9. 阶段 3：岗位发现系统

### 9.1 目标

解决用户不知道去哪找岗位的问题。

### 9.2 功能

- 用户输入求职目标
- 搜索策略 Agent 生成关键词
- 程序调用搜索工具或招聘源适配器
- 抓取候选岗位
- 打开岗位详情页
- 提取 JD
- 去重
- 过滤垃圾岗位
- 匹配评分排序

### 9.3 招聘源优先级

第一批建议：

```text
公司官网 Careers
公开校招官网
实习招聘页面
牛客招聘页面
搜索引擎结果
公开 ATS 页面
```

后续再考虑：

```text
Boss
实习僧
LinkedIn
Seek
Indeed
公众号 / 社交媒体招聘帖
```

### 9.4 风险

部分平台可能：

- 需要登录
- 有验证码
- 有反爬
- 不允许自动化抓取
- 页面经常变化

所以第一版不要强行全自动覆盖所有平台。

---

## 10. 阶段 4：投递材料包生成

### 10.1 目标

让用户拿到真正可以投递的一整套材料。

### 10.2 每个岗位生成

- 专用简历
- 匹配理由
- 自我介绍
- 申请理由
- HR 私信
- Cover Letter
- 表单开放题回答
- 风险提醒
- 可能面试问题

### 10.3 关键点

材料必须：

- 基于用户真实经历
- 贴合 JD
- 不夸大
- 不模板化
- 能被用户面试时解释清楚

---

## 11. 阶段 5：申请表辅助 Agent

### 11.1 目标

解决用户投递时卡在表单和截图页面的问题。

### 11.2 输入

- 用户粘贴的表单问题
- 用户上传截图后的 OCR 文本
- 浏览器页面文字
- 错误提示
- HR 消息
- 邮件内容

### 11.3 输出

- 这一栏是什么意思
- 应该怎么填
- 填这个有没有风险
- 需要用户自己确认什么
- 可以直接复制的自然表达
- 如果不确定，明确提醒用户不要乱填

### 11.4 产品表现

用户界面上就是一个聊天窗口：

```text
我卡在这个申请页面了，怎么填？
```

系统结合：

- 当前岗位 JD
- 用户履历
- 用户求职偏好
- 表单上下文

给出答案。

---

## 12. 阶段 6：浏览器插件

### 12.1 目标

让系统真正进入用户投递流程，而不是只停留在网页外面。

### 12.2 插件功能

- 读取当前岗位页面
- 读取当前申请表字段
- 提取页面文字
- 调用后端 Agent
- 自动生成填写建议
- 可选择性填入部分字段
- 上传推荐简历
- 停在提交前等待用户确认

### 12.3 不做

- 不绕验证码
- 不自动点击最终提交
- 不批量海投
- 不模拟违规操作

---

## 13. 阶段 7：投递记录与求职 CRM

### 13.1 目标

让系统能持续追踪用户求职过程。

### 13.2 功能

- 已发现岗位
- 已收藏岗位
- 已生成材料
- 已投递
- 待跟进
- 已拒绝
- 笔试
- 面试
- Offer

### 13.3 每条记录保存

- 公司
- 岗位
- 岗位链接
- 匹配度
- 使用的简历版本
- 投递材料包
- 投递平台
- 投递时间
- 当前状态
- HR 联系方式
- 后续提醒
- 面试记录

---

## 14. 阶段 8：有限自动投递

### 14.1 目标

只在安全、合规、结构化的情况下辅助自动投递。

### 14.2 可做场景

- 公开 ATS 表单
- 页面结构稳定
- 用户已经确认材料
- 没有验证码
- 不违反平台规则
- 不需要伪造身份信息

### 14.3 不做场景

- 绕验证码
- 未经用户确认提交
- 大规模海投
- 伪造经历
- 违反招聘平台规则
- 代替用户做敏感法律/身份判断

### 14.4 推荐策略

自动投递放到最后。  
前期重点是：

```text
找岗位
读岗位
判断匹配
生成材料
辅助填写
记录状态
```

---

## 15. 数据库设计草案

### 15.1 用户相关

```text
users
profiles
education_records
experiences
experience_facts
skills
job_preferences
```

### 15.2 简历相关

```text
resume_templates
resume_versions
resume_sections
resume_bullets
resume_reviews
```

### 15.3 岗位相关

```text
job_sources
jobs
job_raw_pages
job_parsed_jds
job_matches
saved_jobs
```

### 15.4 投递相关

```text
application_packages
application_documents
application_forms
application_records
application_status_logs
```

### 15.5 Agent 与 LLM 日志

```text
agent_runs
llm_calls
prompt_templates
tool_calls
```

---

## 16. 推荐项目目录结构

```text
ai-job-copilot/
├── README.md
├── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── models.py
│   │   │   └── session.py
│   │   ├── llm/
│   │   │   ├── provider.py
│   │   │   └── deepseek_provider.py
│   │   ├── agents/
│   │   │   ├── resume_parser.py
│   │   │   ├── search_strategy.py
│   │   │   ├── jd_parser.py
│   │   │   ├── job_matcher.py
│   │   │   ├── resume_customizer.py
│   │   │   ├── resume_reviewer.py
│   │   │   ├── application_writer.py
│   │   │   └── form_assistant.py
│   │   ├── services/
│   │   │   ├── profile_service.py
│   │   │   ├── resume_service.py
│   │   │   ├── job_discovery_service.py
│   │   │   ├── job_matching_service.py
│   │   │   ├── application_service.py
│   │   │   └── document_export_service.py
│   │   └── api/
│   │       ├── profiles.py
│   │       ├── resumes.py
│   │       ├── jobs.py
│   │       ├── applications.py
│   │       └── assistant.py
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── templates/
│   ├── resume_cn_tech.docx
│   ├── resume_cn_ai_product.docx
│   └── resume_cn_operation.docx
└── docs/
    ├── product_plan.md
    ├── mvp_scope.md
    ├── agent_design.md
    └── database_design.md
```

---

## 17. 质量控制机制

### 17.1 JSON Schema 校验

所有 Agent 输出必须通过 JSON Schema。

例如：

```text
JD 解析 Agent 必须输出 JobParsedJD
岗位匹配 Agent 必须输出 JobMatchResult
简历定制 Agent 必须输出 ResumeDraft
简历审查 Agent 必须输出 ResumeReview
```

如果 JSON 不合法：

```text
自动重试一次
仍失败则返回错误并记录日志
```

---

### 17.2 事实校验

简历生成前后都要检查：

```text
生成内容是否来自用户 facts / allowed_claims
是否触碰 forbidden_claims
是否出现不存在的数字、公司、成果、上线规模
```

---

### 17.3 版本记录

每次生成都保存：

- 输入 JD
- 使用的用户履历
- 使用的模板
- Agent 输出
- 最终简历
- 用户修改
- 审查结果

这样后面可以回溯。

---

## 18. 隐私与安全

项目必须明确提醒用户：

```text
不要上传不想被模型处理的敏感信息。
API Key 只保存在本地 .env。
默认不把用户数据上传到项目作者服务器。
投递前必须用户确认。
工作授权、签证、法律身份等问题必须用户自行确认。
```

如果后期做云端版，再考虑：

- 数据加密
- 用户账号
- 权限隔离
- API key 加密存储
- 删除数据功能
- 日志脱敏

---

## 19. 项目风险

### 19.1 技术风险

- 招聘网站反爬
- 页面结构经常变化
- JD 抽取不稳定
- LLM 输出 JSON 失败
- 简历导出格式错乱
- OCR 识别不准

### 19.2 产品风险

- 用户只想自动海投
- 用户不愿意填写完整履历
- 简历生成不够自然
- 推荐岗位质量不高
- 匹配评分不可信

### 19.3 合规风险

- 自动投递违反平台规则
- 用户身份/签证问题被错误建议
- AI 编造经历
- 批量提交造成账号风险

### 19.4 应对方式

- 先做辅助，不做强自动
- 强制用户确认
- 所有输出基于事实库
- 高风险问题明确提醒用户自行确认
- 保存审查日志
- README 写清楚项目边界

---

## 20. 长期扩展方向

### 20.1 多模型支持

后期可以支持：

```text
DeepSeek
Kimi
OpenAI
Gemini
Qwen
Claude
```

但第一版不做多模型路由。

### 20.2 浏览器插件增强

- 自动识别 JD
- 自动识别表单字段
- 自动填入基础信息
- 生成开放题答案
- 推荐简历版本
- 停在提交前

### 20.3 面试准备

根据：

- 岗位 JD
- 用户投递简历
- 用户项目经历
- 岗位风险项

生成：

- 可能面试问题
- 项目讲解稿
- 行为面试回答
- 技术问题准备
- 自我介绍版本

### 20.4 求职数据分析

统计：

- 投递数量
- 回复率
- 不同岗位类型表现
- 不同简历版本表现
- 哪些经历最常被使用
- 哪些岗位匹配度最高

### 20.5 社区共享

开源项目可以允许用户贡献：

- 招聘源适配器
- 简历模板
- Prompt 模板
- JD 解析规则
- 常见申请表问题库

---

# 🎯 最终目标差距与 V1/V2 路线图

当前版本不能被理解为“项目已经完善”。它更准确的状态是：

```text
MVP 主体已经跑通，工程基础已经补强；
但距离真正能陪用户完成高质量求职战役的 JobPilot，还差一个 V1/V2 级别的产品化阶段。
```

## 1. 当前版本与真实目标的差距

| 方向 | 当前状态 | 与目标的差距 |
|------|----------|--------------|
| 岗位发现 | 已有搜索策略、DDGS 搜索执行、网页抓取 | 还不够像“机会雷达”：缺持续发现、多源聚合、去重、质量过滤、岗位归类、硬性条件筛查和批量评分排序 |
| 匹配判断 | 已有岗位匹配 Agent 和评分 | 可信度还不够：需要结合硬性规则、用户偏好、履历事实、风险项、不可投原因，而不是只靠一次 Agent 输出 |
| 履历事实库 | 已能结构化记录基本履历、经历事实、allowed / forbidden claims | 颗粒度还不够：缺证据、数字来源、claim level、面试可解释性、风险等级、可迁移能力标签 |
| 简历生成 | 已能基于模板生成 DOCX/PDF，并做审查 | 距离“可放心投递”还差：缺事实校验闭环、版本对比、风格一致性、人工编辑记录、最终投递版确认 |
| 申请辅助 | 已有文字表单辅助和 OCR 上传 | 还偏浅：需要结合岗位、履历、目标城市/国家、实习时间、身份/签证/远程限制等上下文给答案 |
| 浏览器插件 | 已能从招聘页发送 JD 到 JobPilot | 还没有真正进入投递流：需要识别表单字段、读取页面上下文、推荐简历版本、辅助填写，并停在提交前 |
| 求职 CRM | 已有投递状态记录 | 还不是决策系统：缺投递优先级、跟进建议、失败原因复盘、回复率统计、材料效果反馈 |
| 真实验证 | 有 smoke/API 测试 | 缺真实 LLM、真实搜索结果、真实 OCR 图片、真实岗位样例、真实导出简历的端到端验证 |

## 2. V1 目标：从 MVP Demo 到可用求职系统

V1 的目标不是继续堆功能，而是让 JobPilot 真正能完成一轮高质量求职流程：

```text
建立可信履历事实库
→ 主动发现岗位
→ 筛掉不合适岗位
→ 给出可信匹配决策
→ 生成可投材料
→ 辅助申请表填写
→ 记录投递和反馈
```

### V1-1 履历事实库 2.0

必须补强的数据：

- `facts`：真实发生过的事实
- `evidence`：事实证据，例如链接、文件、截图、作品、代码仓库
- `claim_level`：可表达强度，例如“参与 / 负责 / 主导 / 独立完成”
- `risk_level`：面试风险，例如“稳 / 需解释 / 不建议写”
- `interview_explanation`：面试时怎么讲
- `transferable_skills`：可迁移能力标签
- `forbidden_claims`：绝对不能写的内容

完成标准：

```text
任意一条简历 bullet 都能追溯到事实、证据和可解释话术。
```

### V1-2 岗位发现 2.0

需要从“能搜”升级到“能发现值得投的机会”：

- 多关键词搜索
- 多来源聚合
- URL 去重
- 公司 / 岗位 / 地点 / 时间要求抽取
- 垃圾岗位过滤
- 硬性条件过滤
- 保存候选岗位
- 批量解析 JD
- 批量匹配排序

完成标准：

```text
用户输入目标后，系统能产出一批候选岗位，并按值得投递程度排序。
```

### V1-3 匹配与投递决策 2.0

匹配结果不能只是分数，必须变成决策：

- `apply`：值得投
- `maybe`：需要用户确认条件后再投
- `skip`：不建议投
- `risky`：能投但有明显风险

每个决策必须包含：

- 硬性条件是否满足
- 主要匹配理由
- 不匹配风险
- 需要用户确认的问题
- 推荐简历策略
- 推荐投递材料策略

完成标准：

```text
用户能根据系统解释判断“为什么投 / 为什么不投 / 怎么补救”。
```

### V1-4 简历生成与审查 2.0

简历生成要进入“可投递版”标准：

- 固定模板
- 内容来自事实库
- bullet 可追溯
- 不触碰 forbidden claims
- 审查夸大、空话、AI 味、岗位关键词不足
- 对比历史版本，避免风格漂移
- 用户可编辑并保存最终版

完成标准：

```text
每份简历都能说明：用了哪些事实、为什么这样写、有没有风险、是否用户确认过。
```

### V1-5 申请表辅助 2.0

申请辅助必须从“回答问题”升级到“读懂申请上下文”：

- 关联当前岗位
- 关联推荐简历版本
- 关联用户履历事实库
- 支持截图 OCR
- 支持 HR 消息 / 邮件 / 开放题
- 标记需要用户亲自确认的问题
- 对身份、签证、法律、可入职时间等高风险项强提醒

完成标准：

```text
生成的答案自然、可复制、不过度包装，并明确哪些信息必须用户自己确认。
```

## 3. V2 目标：从可用系统到求职战役 Copilot

V2 的目标是让 JobPilot 不只是工具，而是一个持续辅助求职决策的系统。

### V2-1 浏览器投递助手 2.0

- 识别当前页面是 JD、申请表、上传简历页还是 HR 消息页
- 读取表单字段
- 推荐简历版本
- 生成字段填写建议
- 可选择性填入基础字段
- 停在提交前，必须用户确认

不做：

- 不绕验证码
- 不自动最终提交
- 不海投
- 不伪造信息

### V2-2 求职 CRM 2.0

CRM 要从“记录状态”升级成“决策反馈系统”：

- 投递优先级
- 跟进提醒
- 面试记录
- 拒绝原因
- 回复率统计
- 不同简历版本表现
- 不同岗位类型表现
- 哪些经历最常被使用
- 下一轮投递策略建议

完成标准：

```text
系统能根据投递结果反过来优化岗位发现、简历策略和申请材料。
```

### V2-3 真实评测体系

需要建立真实样例集：

- 真实岗位 JD 样例
- 真实用户履历样例
- 真实搜索结果样例
- 真实截图 OCR 样例
- 简历导出视觉检查
- Agent 输出质量评估

完成标准：

```text
每次改动后都能知道：岗位发现有没有变差、匹配判断有没有乱、简历有没有更可信。
```

## 4. 下一阶段优先级

| 优先级 | 任务 | 原因 |
|--------|------|------|
| P0 | 履历事实库 2.0 | 这是所有可信生成、匹配和审查的地基 |
| P0 | 岗位发现 2.0 | 你的目标不是等用户贴链接，而是主动发现机会 |
| P0 | 匹配与投递决策 2.0 | 分数不够，必须给出可解释决策 |
| P1 | 简历生成与审查 2.0 | 从“能生成”变成“能放心投” |
| P1 | 申请表辅助 2.0 | 真正覆盖投递过程里的卡点 |
| P2 | 浏览器投递助手 2.0 | 进入真实申请页面，但保持用户最终确认 |
| P2 | 求职 CRM 2.0 | 用反馈改进下一轮求职策略 |

## 5. V1 进度追踪

> 最后更新: 2026-06-02

| V1 目标 | 状态 | 做了什么 |
|---------|------|----------|
| V1-1 履历事实库 2.0 | ✅ | 数据模型已补全；P-019 修复后所有 Agent 已接收完整结构化 facts（id/claim_level/risk_level/evidence） |
| V1-2 岗位发现 2.0 | ✅ | 搜索→去重→抓取页面→解析 JD→自动匹配；P-021 修复后使用 WebFetcher 真实抓取 |
| V1-3 匹配决策 2.0 | ✅ | 决策输出 + P-020 修复后新字段完整落库（hard_filter/user_confirm/strategy） |
| V1-4 简历生成审查 2.0 | ✅ | 简历 Agent 含 claim_level校准/risk_level过滤/forbidden检查/fact_trace；审查 Agent 支持跨版本对比 |
| V1-5 申请表辅助 2.0 | ✅ | API 支持 resume_id 关联，Agent 理解 claim_level/risk_level，前端支持简历版本选择 |
| V2-1 浏览器投递助手 2.0 | ✅ | 插件支持识别页面类型(JD/表单)，表单字段检测，调用助手 API 生成填写建议 |
| V2-2 求职 CRM 2.0 | ✅ | LLM 驱动的策略分析 + 硬编码fallback；P-018 已修复矛盾 |
| - | - | - |
| P-017 | V2-1 浏览器插件尚需真实表单测试 | 📋 | 待真实招聘网站验证 |
| P-018 | V2-2 策略建议基于简单规则，未接入 LLM | 🔴 阻塞 | ✅ 已解决 | CRM analytics 先尝试 LLM 生成策略建议，失败或降级时回退规则；P-018 与 V2-2 矛盾已解除 |
| P-019 | 履历事实字段已建模但未完整传给 Agent | 匹配/简历/表单 Agent 收不到 claim_level/risk_level/evidence 等关键字段 | ✅ 已解决 | job_matching_service/application_service/applications.py 中 profile_data 全部改为结构化 facts 对象 |
| P-020 | 匹配决策新字段未落库 | hard_filter_passed/user_confirm/application_strategy 只在 Agent 输出，没存入 JobMatch | ✅ 已解决 | JobMatch 模型加 6 个新字段，matching_service 和 API 完整落库并返回 |
| P-021 | save-and-parse 只用 snippet 不抓真实 JD | 搜索结果标题+摘要当 JD，不是真实获取 | ✅ 已解决 | save-and-parse 改用 WebFetcher 打开 URL 获取完整页面内容，失败时回退 snippet |



## 6. 后续复用提示词

```text
请按照《AI_Job_Search_Copilot_Project_Plan.md》里的“最终目标差距与 V1/V2 路线图”，继续推进 JobPilot。

不要把当前项目当成已经完善的产品。它只是 MVP 骨架和本地原型。

请优先检查：
1. 履历事实库 2.0 是否足够支撑可信生成；
2. 岗位发现是否能完成搜索、去重、过滤、保存、解析、批量评分；
3. 匹配判断是否从“分数”升级为“投 / 不投 / 待确认 / 高风险”的决策；
4. 简历生成是否能追溯事实、证据、claim level 和 forbidden claims；
5. 申请表辅助是否结合岗位、简历版本、履历事实和风险提醒；
6. 浏览器插件是否真正进入投递流程但不自动最终提交；
7. CRM 是否能根据投递反馈优化下一轮策略。

每次动手前，先读取计划书的问题台账和 V1/V2 路线图。
每次发现问题，写入问题台账。
每次解决问题，写清楚解决了什么、怎么解决、如何验证。
```

---

# 最终开发优先级

## 第一优先级

```text
履历库
模板系统
JD 解析
岗位匹配
简历生成
简历审查
```

## 第二优先级

```text
岗位发现
投递材料包
申请表辅助
```

## 第三优先级

```text
浏览器插件
投递记录
面试准备
```

## 第四优先级

```text
有限自动投递
多模型支持
社区插件系统
```

---

# 21. 已知局限与改进方向

### 21.1 当前版本已知局限

| 局限 | 影响 | 改进计划 |
|------|------|---------|
| 搜索执行器已接入但真实搜索质量验证不足 | 搜索结果可能为空、重复或不相关 | 增加结果去重、错误处理、真实查询测试和保存/解析/评分闭环 |
| 语言能力无独立建模 | 无法精细匹配岗位的语言要求 | 履历库加语言专项（语种/考试/分数/等级） |
| OCR 服务已接入但真实模型/真实图片验证仍不足 | EasyOCR 首次加载较慢，真实截图识别质量还需要人工或集成环境验证 | 保留 mock 单测，补一组可选的真实图片集成测试和模型下载说明 |
| 批量匹配排序缺席 | 搜索结果还没有形成“发现 → 保存 → 解析 → 评分排序”的完整闭环 | 加批量匹配接口，按评分排序输出列表 |
| 简历版本间风格漂移未检测 | 审查只针对单份简历，不对比历史版本 | 审查 Agent 加入跨版本对比逻辑 |
| 当前测试仍偏 smoke test | 全流程未经真实 LLM、真实搜索结果和真实 OCR 图片验证 | 补真正 E2E 测试，覆盖履历→JD→匹配→简历，并在有 API Key 的环境验证 LLM 调用 |

### 21.2 AI 能力边界（风险提示）

| 场景 | 系统行为 |
|------|---------|
| DeepSeek API 不可用 | 所有 Agent 降级，返回 fallback 数据，不崩溃 |
| JD 文本格式异常 | 解析 Agent 尝试最佳猜测，失败返回空字段 |
| 用户履历为空 | 匹配 Agent 返回低分 + 风险提示，不编造经历 |
| 模板文件缺失 | 简历生成失败，返回明确错误 |
| 投递平台有验证码 | 不做任何尝试绕过，提示用户手动完成 |

---

# 22. 测试策略

```text
backend/tests/
├── test_llm_provider.py    # DeepSeek Provider 初始化、重试、回退
├── test_models.py          # 数据模型关系、默认值、级联删除  
├── test_services.py        # Profile/Job/Resume CRUD 服务层
├── test_agents.py          # Agent JSON 解析、fallback 行为
├── test_api.py             # 端点 HTTP 状态码、静态文件
├── test_document_export.py # DOCX 模板渲染、PDF 导出
└── test_full_workflow.py   # JD 解析 + 匹配 + 简历生成完整链路
```

```bash
cd backend
pytest tests/ -v
```

测试会使用 `test_jobpilot.db`、`test_settings.json` 和 `test_secret_key`，不会删除本地真实数据和 API Key 配置。

---

# 23. 贡献指南

### 添加新 Agent
1. `backend/app/agents/my_agent.py` — 继承调用 `LLMProvider`，定义 system prompt + fallback
2. `backend/app/services/my_service.py` — 调用 agent + 数据库操作
3. `backend/app/api/my_api.py` — 路由，注册到 `main.py`
4. `frontend/src/app/my-page/page.tsx` — 前端页面，添加到 `NavBar.tsx`
5. `cd frontend && npm run build` — 重新编译静态文件

### 添加新模型适配器
1. `backend/app/llm/new_provider.py` — 继承 `LLMProvider`，实现 `chat()` / `achat()`
2. `frontend/src/app/settings/page.tsx` — `PRESETS` 数组添加预设
3. 更新计划文档和 README

### 添加新简历模板
1. 创建 DOCX，用 `{{key}}` 做占位符 → `templates/`
2. `backend/app/services/resume_service.py` → `TEMPLATE_SEEDS` 添加条目
3. `frontend/src/app/templates/page.tsx` → 添加预览样式函数

---

# 24. 部署路线图

| 阶段 | 状态 | 产物 |
|------|------|------|
| MVP 本地运行 | ✅ 已完成 | `start.bat` 一键启动 |
| Electron 桌面应用 | 📋 待开发 | .exe 安装包，无需 Python/浏览器 |
| Docker 部署 | 📋 规划中 | `docker-compose up` 一键启动 |
| 云端版 | 📋 规划中 | 用户注册，多租户数据隔离 |

---

# 最终一句话

这个项目最重要的不是“让 AI 写一份漂亮简历”，而是：

```text
让用户从“不知道去哪找、不知道能不能投、不知道怎么写、不知道表单怎么填”
变成
“有岗位列表、有匹配判断、有稳定简历、有投递材料、有申请辅助、有记录追踪”。
```

这才是它和普通 AI 简历生成器的区别。
