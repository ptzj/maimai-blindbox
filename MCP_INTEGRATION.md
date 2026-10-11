# MCP 集成说明 (MCP_INTEGRATION.md)

本文件说明「麦麦惊喜盲盒点餐」实际使用的麦当劳 MCP Server、Tool、调用流程与业务价值。

## 1. 接入的 MCP Server

| 项 | 值 |
|---|---|
| Server 名称 | `mcd-mcp` |
| 提供方 | 麦当劳中国（金拱门） |
| 接入地址 | `https://mcp.mcd.cn` |
| 传输协议 | Streamable HTTP |
| 鉴权方式 | `Authorization: Bearer ${MCD_MCP_TOKEN}`（Token 来自麦当劳开放平台，仅以环境变量占位符形式出现在配置中） |
| 限流 | 600 次 / 分钟（超频返回 429） |

> 配置示例见 `mcp-config.example.json`，**不含任何真实 Token**。

## 2. 实际调用的 Tool 与用途

| MCP Tool | 在 Skill 中的用途 | 调用阶段 |
|---|---|---|
| `now-time-info` | 获取当前时段，辅助早/午/晚餐品提示 | 步骤 1 |
| `query-meals` | 拉取当前门店在售餐品（分类/编码/标签），作为盲盒算法输入 | 步骤 2 |
| `query-meal-detail` | 解析套餐组成与可替换项 | 步骤 2 |
| `list-nutrition-foods` | （可选）营养参考展示 | 步骤 2 |
| `auto-bind-coupons` | 一键领取麦麦省可用券 | 步骤 5 |
| `query-store-coupons` / `query-my-coupons` | 补充门店/账户可用优惠 | 步骤 5 |
| `calculate-price` | 计算含券后的真实应付、优惠金额、配送费 | 步骤 5 |
| `query-nearby-stores` | 到店 / 得来速场景选择门店 | 步骤 6 |
| `delivery-query-addresses` / `delivery-create-address` | 麦乐送场景选择或新建配送地址 | 步骤 6 |
| `create-order` | 用户确认后创建订单 | 步骤 6 |
| `query-order` | 下单后查询订单状态 / 取餐信息 | 步骤 6 |
| `cancel-order` | 误下单时协助取消 | 步骤 7 |

## 3. 调用流程

```
用户输入偏好(人数/预算/忌口/偏好新品)
        │
        ▼
[now-time-info] ──► 时段提示
        │
        ▼
[query-meals] + [query-meal-detail] ──► 真实菜单
        │
        ▼
盲盒算法(src/blindbox.py)：加权随机 + 稀有度 + 预算保护
        │
        ▼
开奖交互(经典款/稀有款/隐藏款)
        │
        ▼
[auto-bind-coupons] → [query-store-coupons/query-my-coupons] → [calculate-price]
        │
        ▼
二次确认 → [query-nearby-stores / delivery-*] → [create-order] → [query-order]
```

## 4. 业务价值

- **降低决策疲劳**：把「不知道吃什么」转化为有趣的盲盒体验，提升点餐效率。
- **带动转化**：盲盒机制天然提升尝试新品/搭配的意愿，结合自动领券促进下单。
- **合规可控**：预算保护避免超支点餐，杜绝「奢靡浪费」；输出全程标注「仅供参考」。
- **真实可用**：全程基于麦当劳官方 MCP 实时数据，餐品、价格、优惠、下单均真实生效。
