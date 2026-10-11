"""麦麦惊喜盲盒 · 盲盒随机套餐算法 (pure-python, 无外部依赖)

核心算法模块，负责在用户给定约束（预算 / 人数 / 忌口 / 是否偏好新品）下，
从麦当劳在售餐品中生成一套「惊喜盲盒套餐」，并赋予稀有度标签。

设计要点：
- 与 MCP 解耦：真实菜单数据由 SKILL.md 通过麦当劳 MCP（query-meals 等）获取后传入本模块，
  因此本模块可在无网络 / 无 Token 的本地环境独立测试。
- 预算保护：超预算时自动降级替换，避免「奢靡浪费」，符合活动内容合规要求。
- 稀有度：新品/限定单品被抽中概率更低（采样权重更小），从而让「隐藏款」更具惊喜感。

运行演示：  python3 src/blindbox.py --budget 40 --people 1 --new
单元测试：  PYTHONPATH=$PWD/src python3 tests/test_blindbox.py
"""
from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass, field
from typing import Iterable, Optional

# 餐品分类角色映射（按麦当劳菜单常见分类做容错子串匹配）
MAIN_CATEGORIES = ("汉堡", "主餐", "套餐", "饭", "卷", "堡", "主食")
DRINK_CATEGORIES = ("饮料", "饮品", "冷饮", "热饮", "咖啡", "奶茶", "汽水")
SIDE_CATEGORIES = ("小食", "甜品", "派", "薯条", "鸡块", "玉米", "蛋挞", "甜点")

RARITY_TIERS = {
    "隐藏款": {"emoji": "🌟", "desc": "含新品 / 限定单品的惊喜组合",
               "weight_boost_new": 1.2, "base_weight_new": 0.35},
    "稀有款": {"emoji": "✨", "desc": "含招牌 / 特色单品", "base_weight_feature": 0.6},
    "经典款": {"emoji": "🥡", "desc": "稳健不出错的人气组合", "base_weight": 1.0},
}


@dataclass
class MealItem:
    code: str
    name: str
    category: str
    price: float
    tags: list[str] = field(default_factory=list)

    @property
    def role(self) -> str:
        c = self.category
        if any(k in c for k in MAIN_CATEGORIES):
            return "main"
        if any(k in c for k in DRINK_CATEGORIES):
            return "drink"
        if any(k in c for k in SIDE_CATEGORIES):
            return "side"
        return "other"

    def matches_avoid(self, avoid: Iterable[str]) -> bool:
        return bool(set(self.tags) & set(avoid))


def _load_items(raw_items) -> list[MealItem]:
    items: list[MealItem] = []
    for it in raw_items:
        items.append(MealItem(
            code=str(it.get("code", "")),
            name=str(it.get("name", "")),
            category=str(it.get("category", "")),
            price=float(it.get("price", 0) or 0),
            tags=list(it.get("tags", []) or []),
        ))
    return items


def _is_new(item: MealItem) -> bool:
    return any(t in ("新品", "限定", "new", "limited") for t in item.tags) or "新" in item.name


def _is_feature(item: MealItem) -> bool:
    return any(t in ("招牌", "特色", "feature") for t in item.tags)


def _sampling_weight(item: MealItem, prefer_new: bool) -> float:
    if _is_new(item):
        return (RARITY_TIERS["隐藏款"]["weight_boost_new"]
                if prefer_new else RARITY_TIERS["隐藏款"]["base_weight_new"])
    if _is_feature(item):
        return RARITY_TIERS["稀有款"]["base_weight_feature"]
    return RARITY_TIERS["经典款"]["base_weight"]


def _weighted_pick(pool: list[MealItem], prefer_new: bool, rng: random.Random) -> Optional[MealItem]:
    if not pool:
        return None
    weights = [_sampling_weight(i, prefer_new) for i in pool]
    return rng.choices(pool, weights=weights, k=1)[0]


def _rank_rarity(selected: list[MealItem]) -> dict:
    if any(_is_new(i) for i in selected):
        t = RARITY_TIERS["隐藏款"]
        return {"name": "隐藏款", "emoji": t["emoji"], "desc": t["desc"]}
    if any(_is_feature(i) for i in selected):
        t = RARITY_TIERS["稀有款"]
        return {"name": "稀有款", "emoji": t["emoji"], "desc": t["desc"]}
    t = RARITY_TIERS["经典款"]
    return {"name": "经典款", "emoji": t["emoji"], "desc": t["desc"]}


def build_combo(raw_items, budget: float, people: int = 1, avoid_tags=None,
                prefer_new: bool = False, seed: Optional[int] = None) -> dict:
    """生成一套惊喜盲盒套餐。

    参数:
        raw_items: 麦当劳在售餐品列表（来自 MCP query-meals，每个元素含
                   code/name/category/price/tags）。
        budget:    单人/整单预算上限（元），用于预算保护。
        people:    用餐人数，决定主餐与饮料数量。
        avoid_tags: 忌口标签集合，如 ["辣", "香菜"]。
        prefer_new: 是否偏好新品/限定（提高新品采样权重）。
        seed:      随机种子，便于测试与可复现演示。

    返回: 含 items / total_price / rarity 等字段的字典。
    """
    rng = random.Random(seed)
    avoid = set(avoid_tags or [])
    items = [i for i in _load_items(raw_items) if not i.matches_avoid(avoid)]
    mains = [i for i in items if i.role in ("main", "other")]
    drinks = [i for i in items if i.role == "drink"]
    sides = [i for i in items if i.role == "side"]

    selected: list[MealItem] = []
    # 每人 1 主餐 + 1 饮料
    for _ in range(max(1, people)):
        m = _weighted_pick(mains, prefer_new, rng)
        if m:
            selected.append(m)
        d = _weighted_pick(drinks, prefer_new, rng)
        if d:
            selected.append(d)
    # 预算允许时加 1 份小食，提升满足感
    side = _weighted_pick(sides, prefer_new, rng)
    if side and sum(i.price for i in selected) + side.price <= budget:
        selected.append(side)

    # 预算保护：超预算则用更便宜的主餐替换，避免超支点餐造成浪费
    while selected and sum(i.price for i in selected) > budget:
        main_idx = max(
            (idx for idx, i in enumerate(selected) if i.role in ("main", "other")),
            key=lambda idx: selected[idx].price, default=None)
        if main_idx is None:
            break
        cheaper = [i for i in mains if i.price < selected[main_idx].price]
        if not cheaper:
            selected.pop(main_idx)
            break
        selected[main_idx] = min(cheaper, key=lambda i: i.price)

    total = round(sum(i.price for i in selected), 2)
    rarity = _rank_rarity(selected)
    return {
        "items": [{"code": i.code, "name": i.name, "category": i.category,
                   "price": i.price, "tags": i.tags} for i in selected],
        "total_price": total,
        "budget": budget,
        "people": people,
        "rarity": rarity["name"],
        "rarity_emoji": rarity["emoji"],
        "rarity_desc": rarity["desc"],
        "within_budget": total <= budget + 1e-6,
    }


def _demo_menu() -> list[dict]:
    return [
        {"code": "M1", "name": "巨无霸套餐", "category": "套餐", "price": 32.0, "tags": ["招牌"]},
        {"code": "M2", "name": "麦辣鸡腿堡", "category": "汉堡", "price": 21.0, "tags": ["辣"]},
        {"code": "M3", "name": "板烧鸡腿堡", "category": "汉堡", "price": 22.0, "tags": []},
        {"code": "M4", "name": "双层吉士堡", "category": "汉堡", "price": 18.0, "tags": []},
        {"code": "M5", "name": "新品·黑松露风味堡", "category": "汉堡", "price": 28.0, "tags": ["新品", "限定"]},
        {"code": "D1", "name": "可口可乐(中)", "category": "饮料", "price": 9.0, "tags": []},
        {"code": "D2", "name": "鲜煮咖啡", "category": "热饮", "price": 12.0, "tags": ["招牌"]},
        {"code": "D3", "name": "雪碧(中)", "category": "饮料", "price": 9.0, "tags": []},
        {"code": "S1", "name": "薯条(中)", "category": "小食", "price": 11.0, "tags": []},
        {"code": "S2", "name": "麦辣鸡翅", "category": "小食", "price": 13.0, "tags": ["辣"]},
        {"code": "S3", "name": "苹果派", "category": "派", "price": 7.0, "tags": ["甜品"]},
        {"code": "S4", "name": "新品·樱花麦旋风", "category": "甜品", "price": 15.0, "tags": ["新品", "限定", "甜品"]},
    ]


def _print_reveal(r: dict) -> None:
    print("🎁  正在开启今日麦麦盲盒……\n")
    print(f"{r['rarity_emoji']} 恭喜抽到【{r['rarity']}】— {r['rarity_desc']}\n")
    for it in r["items"]:
        print(f"   · {it['name']:<14} ¥{it['price']}")
    flag = "✅ 预算内" if r["within_budget"] else "⚠️ 超预算"
    print(f"\n合计预估 ¥{r['total_price']} / 预算 ¥{r['budget']}   {flag}")


def main() -> None:
    ap = argparse.ArgumentParser(description="麦麦惊喜盲盒算法演示")
    ap.add_argument("--menu", default=None, help="菜单 JSON 路径（缺省使用内置演示菜单）")
    ap.add_argument("--budget", type=float, default=40.0, help="预算上限（元）")
    ap.add_argument("--people", type=int, default=1, help="用餐人数")
    ap.add_argument("--avoid", default="", help="逗号分隔的忌口标签，如 辣,香菜")
    ap.add_argument("--new", action="store_true", help="偏好新品 / 限定")
    ap.add_argument("--seed", type=int, default=None, help="随机种子")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出便于程序消费")
    args = ap.parse_args()

    if args.menu:
        with open(args.menu, encoding="utf-8") as f:
            menu = json.load(f)
    else:
        menu = _demo_menu()

    result = build_combo(
        menu, budget=args.budget, people=args.people,
        avoid_tags=[t for t in args.avoid.split(",") if t],
        prefer_new=args.new, seed=args.seed)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_reveal(result)


if __name__ == "__main__":
    main()
