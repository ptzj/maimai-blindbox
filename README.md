# 🎁 麦麦惊喜盲盒点餐 (MaiMai Blind Box)

> 把「今天吃什么」的纠结，变成开盲盒的惊喜。  
> 基于 **麦当劳中国 MCP** 真实菜单数据，在预算与忌口约束下，随机生成带稀有度的套餐，  
> 并一键完成领券、计价与下单引导。

本 Skill 是 [麦当劳程序员创意开发大赛](https://github.com/M-China/mcd-developer-innovation-challenge) 参赛作品，  
由参赛者独立开发，非麦当劳官方产品。

---

## ✨ 功能特性

- 🎲 **随机套餐推荐**：加权随机算法，新品/限定更难抽中，让「隐藏款」更有惊喜。
- 🌟 **盲盒开奖交互**：经典款 / 稀有款 / 隐藏款三档稀有度，悬念式开奖话术，适合截图分享。
- 🍔 **真实菜单查询**：通过麦当劳 MCP `query-meals` / `query-meal-detail` 拉取在售餐品。
- 🎟️ **优惠与计价**：自动领麦麦省券、`calculate-price` 实时算出实付与优惠。
- 🛒 **下单引导**：到店 / 麦乐送 / 得来速全场景，`create-order` 前二次确认，防误单。
- 💰 **预算保护**：超预算自动降级替换，拒绝奢靡浪费（符合活动合规要求）。

## 🎯 目标用户

- 选择困难、一个人不知道吃什么的用户
- 想尝试麦当劳新品但怕踩雷的用户
- 朋友聚会 / 破冰场景
- 喜欢「盲盒」「抽卡」趣味机制、乐于分享的年轻用户

## 📦 安装方法

### 方式 A：作为 WorkBuddy Skill 使用（推荐，可获 WorkBuddy 专项积分）

1. 申请麦当劳 MCP Token：登录 [麦当劳开放平台](https://open.mcd.cn/mcp) → 控制台 → 激活 → 复制 Token。
2. 在 WorkBuddy 左侧【专家·技能·连接器】→【连接器】→【自定义连接器】→【配置 MCP】，填入：
   ```json
   {
     "mcpServers": {
       "mcd-mcp": {
         "type": "streamablehttp",
         "url": "https://mcp.mcd.cn",
         "headers": { "Authorization": "Bearer 你的真实Token" }
       }
     }
   }
   ```
3. 启用 `mcd-mcp` 连接器。
4. 将本仓库 `SKILL.md` 作为 Skill 安装到 WorkBuddy 用户级目录 `~/.workbuddy/skills/maimai-blindbox/`。
5. 在对话框输入「帮我随便点个麦当劳」「来个盲盒」即可触发。

### 方式 B：本地运行算法（无需 Token，用于开发/测试）

```bash
# 演示（使用内置菜单）
python3 src/blindbox.py --budget 40 --people 1 --new

# JSON 输出
python3 src/blindbox.py --budget 50 --people 2 --avoid 辣 --json

# 运行单元测试
PYTHONPATH=$PWD/src python3 tests/test_blindbox.py
```

## 💬 使用示例

```
用户：不知道吃啥，给我抽个麦当劳，两个人，预算 80，不要辣
麦麦盲盒：🎁 正在开启今日麦麦盲盒……
        ✨ 恭喜抽到【稀有款】— 含招牌 / 特色单品
           · 巨无霸套餐  ¥32
           · 板烧鸡腿堡  ¥22
           · 鲜煮咖啡 ×2 ¥24
        合计预估 ¥78 / 预算 ¥80  ✅ 预算内
        （已自动领券）用券后实付 ¥68，已省 ¥10
        是否以「麦乐送」下单？回复"确认"即下单。
```

## 🗂️ 项目结构

```
maimai-blindbox/
├── SKILL.md                 # Skill 定义（核心智能体逻辑 / 源代码）
├── src/blindbox.py          # 盲盒随机算法（纯 Python，可本地测试）
├── tests/                   # 单元测试与示例菜单
│   ├── test_blindbox.py
│   └── sample_menu.json
├── README.md                # 本文件
├── CONTEST_DECLARATION.md   # 参赛声明（官方原文，不可修改）
├── MCP_INTEGRATION.md       # MCP 集成说明
├── mcp-config.example.json  # 脱敏配置示例（仅环境变量占位符）
└── workbuddy.md             # WorkBuddy 开发对话上下文（参与专项奖励用）
```

## ⚠️ 免责声明

本工具为麦当劳程序员节创意开发大赛参赛作品，由参赛者独立开发，非麦当劳官方产品。  
输出仅供参考，不构成医疗、营养或其他专业建议；餐品信息、价格及供应状态以麦当劳官方渠道的实时结果为准。

## 📜 许可

代码以 MIT 许可证开源，仅供非商业学习与交流使用；麦当劳相关商标归其权利人所有。
