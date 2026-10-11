"""麦麦惊喜盲盒算法单元测试（无需 MCP / Token，本地即可运行）。

运行:  PYTHONPATH=$PWD/src python3 tests/test_blindbox.py
"""
import json
import os
import unittest

from blindbox import build_combo

HERE = os.path.dirname(__file__)
with open(os.path.join(HERE, "sample_menu.json"), encoding="utf-8") as _f:
    MENU = json.load(_f)


class TestBlindBox(unittest.TestCase):
    def test_budget_respected(self):
        r = build_combo(MENU, budget=40, people=1, seed=1)
        self.assertLessEqual(r["total_price"], 40 + 1e-6)
        self.assertTrue(r["within_budget"])

    def test_avoid_tags_excluded(self):
        r = build_combo(MENU, budget=60, people=1, avoid_tags=["辣"], seed=2)
        for it in r["items"]:
            self.assertNotIn("辣", it["tags"])

    def test_people_scales_quantity(self):
        r = build_combo(MENU, budget=120, people=3, seed=3)
        # 3 人应至少包含 3 主餐 + 3 饮料 = 6 件
        self.assertGreaterEqual(len(r["items"]), 6)

    def test_rarity_in_valid_set(self):
        r = build_combo(MENU, budget=80, people=1, prefer_new=True, seed=5)
        self.assertIn(r["rarity"], ("经典款", "稀有款", "隐藏款"))

    def test_deterministic_with_seed(self):
        a = build_combo(MENU, budget=50, people=1, seed=42)
        b = build_combo(MENU, budget=50, people=1, seed=42)
        self.assertEqual(a["items"], b["items"])
        self.assertEqual(a["total_price"], b["total_price"])


if __name__ == "__main__":
    unittest.main()
