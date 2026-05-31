# JobPilot — AI Job Search Copilot

基于 DeepSeek 的开源 AI 求职助手：从真实履历出发，主动发现岗位、解析 JD、匹配经历、生成稳定简历，辅助完成投递。

> 程序控制流程，Agent 负责局部专家任务。AI 不编造经历、不乱投、不绕过平台规则。

## 快速开始

```bash
# 1. 克隆项目
git clone <repo-url> && cd JobPilot

# 2. 配置 API Key
cp .env.example backend/.env
# 编辑 backend/.env，填入你的 DEEPSEEK_API_KEY

# 3. 安装依赖（仅首次）
pip install -r backend/requirements.txt

# 4. 启动
# Windows: 双击 start.bat
# macOS/Linux: cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001

# 5. 打开浏览器 http://127.0.0.1:8001
```

> 前端已预编译为静态文件，无需安装 Node.js。如需修改前端，见[开发](#开发)。

## 功能

1. **履历库** — 结构化录入教育/实习/项目/技能，标记 allowed_claims / forbidden_claims
2. **模板系统** — 3 套中文简历模板（技术实习、AI产品、产品运营），可预览
3. **JD 解析** — 粘贴岗位描述或贴链接自动抓取网页，AI 提取结构化信息
4. **岗位匹配** — DeepSeek-reasoner 评分 0-100，给出优势、风险、简历策略
5. **简历生成** — 基于模板 + JD + 事实库生成专用简历，导出 DOCX + PDF
6. **简历审查** — 检查夸大、空话、AI 味、面试承接风险
7. **岗位发现** — 搜索策略 + Playwright 网页抓取
8. **投递材料包** — 自我介绍、申请理由、HR 私信、Cover Letter、面试问题
9. **申请表辅助** — 粘贴表单问题，AI 给出填写建议
10. **投递追踪** — 看板式管理投递状态（发现→收藏→投递→面试→Offer）
11. **浏览器插件** — Chrome 扩展，招聘页一键发送 JD 到 JobPilot
12. **多模型** — 预设 DeepSeek / OpenAI / Kimi / Qwen，前端设置页配置 API Key

### 设置页面

启动后在浏览器中打开应用，点击右上角「设置」：
- 填写 API Key（password 字段，不显示明文）
- 选择模型预设（DeepSeek / OpenAI / Kimi / Qwen）
- Key 加密存储在 `settings.json` 中

### 浏览器插件

1. 打开 Chrome，访问 `chrome://extensions`
2. 开启「开发者模式」
3. 点击「加载已解压的扩展程序」，选择 `extension/` 文件夹
4. 在任意招聘详情页点击插件图标 → 一键发送 JD 到 JobPilot

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI + SQLAlchemy + SQLite |
| 前端 | Next.js 16 + Tailwind CSS 4 |
| LLM | DeepSeek (chat + reasoner) |
| 文档 | python-docx |
| 部署 | 单进程 FastAPI 托管前后端 |

## 项目结构

```
JobPilot/
├── start.bat                 # 一键启动
├── .env.example              # 环境变量模板
├── backend/
│   └── app/
│       ├── main.py           # FastAPI 入口
│       ├── core/config.py    # 配置
│       ├── db/models.py      # 11 张数据表
│       ├── llm/              # LLM Provider (DeepSeek)
│       ├── agents/           # 8 个 AI Agent
│       ├── services/         # 业务服务层
│       └── api/              # REST API
├── frontend/                 # Next.js 项目 (输出在 out/)
└── templates/                # DOCX 简历模板
```

## 开发

前端修改后需要重新编译静态文件：

```bash
cd frontend
npm install
npm run build      # 输出到 frontend/out/
```

后端开发模式（支持热重载）：

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8001
```
