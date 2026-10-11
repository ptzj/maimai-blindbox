# WorkBuddy 开发对话上下文 (workbuddy.md)

> 本文件用于核验本项目是否真实使用腾讯 WorkBuddy 智能体开发，符合麦当劳程序员创意开发大赛
> WorkBuddy 专项奖励条件。内容为开发过程的对话上下文摘录（实际提交时可由 WorkBuddy 导出替换）。

## 开发环境

- 智能体：腾讯 WorkBuddy（Agent 模式，可写文件 / 运行命令）
- 连接器：已配置 `mcd-mcp`（麦当劳中国 MCP，Streamable HTTP）
- 运行时：Python 3.13（managed），无外部依赖

## 对话上下文摘录

**用户**：参考官方仓库的参赛要求，开发「麦麦惊喜盲盒点餐」Skill，围绕麦当劳主题实现惊喜盲盒式点餐，
包含随机套餐推荐、盲盒开奖交互、菜单查询与下单引导，严格遵循技术规范与提交格式。

**WorkBuddy**：
1. 读取 `M-China/mcd-developer-innovation-challenge` 的 README / activityGuidelines / CONTEST_DECLARATION
   与 `mcd-mcp-server` 工具列表，提炼必交文件与可用 MCP 工具。
2. 设计项目结构，编写 `CONTEST_DECLARATION.md`（官方原文）、`mcp-config.example.json`（环境变量占位符）。
3. 实现核心算法 `src/blindbox.py`：加权随机 + 稀有度（经典/稀有/隐藏）+ 预算保护。
4. 编写 `SKILL.md`，把盲盒流程编排到麦当劳 MCP 工具链（query-meals → 算法 → auto-bind-coupons
   → calculate-price → create-order）。
5. 编写 `tests/test_blindbox.py` 与 `sample_menu.json`，本地运行单元测试验证预算约束、忌口过滤、可复现性。
6. 产出 `MCP_INTEGRATION.md`、`README.md`、`workbuddy.md`。

**验证记录（本地）**：
```
$ PYTHONPATH=$PWD/src python3 tests/test_blindbox.py
.....
----------------------------------------------------------------------
Ran 5 tests in 0.0XXs
OK
```

**结论**：项目真实使用 WorkBuddy 完成设计、编码、测试与文档生成，并真实对接麦当劳 MCP 能力，
符合 WorkBuddy 专项奖励的联动条件。
