from __future__ import annotations
import pandas as pd

TYPE_MAP = {"壽險":"life", "醫療險":"medical", "意外險":"accident", "重大疾病":"critical"}

def rank_gaps(needs: dict, risks: dict) -> list[dict]:
    factors = {"壽險": risks["家庭責任風險"], "醫療險": risks["疾病風險"], "意外險": risks["意外風險"], "重大疾病": risks["疾病風險"]}
    rows = []
    for kind, gap in needs["gaps"].items():
        coverage_ratio = gap / max(1, needs["needs"][kind])
        score = factors[kind] * .4 + coverage_ratio * 100 * .3 + risks["家庭責任風險"] * .2 + risks["財務風險"] * .1
        rows.append({"類型": kind, "缺口": gap, "推薦分數": round(score), "風險分數": factors[kind]})
    return sorted(rows, key=lambda row: row["推薦分數"], reverse=True)

def optimize_budget(needs: dict, ranking: list[dict], products: pd.DataFrame, monthly_budget: float, age: int) -> dict:
    # Greedy purchase of useful coverage units by explainable recommendation priority.
    catalog = products[(products.target_age_min <= age) & (products.target_age_max >= age)].copy()
    left = max(0, float(monthly_budget)); chosen = {k: {"coverage": 0.0, "premium": 0.0, "product": ""} for k in needs["gaps"]}
    for row in ranking:
        kind = row["類型"]; gap = needs["gaps"][kind]
        candidates = catalog[catalog.product_type == TYPE_MAP[kind]].sort_values("monthly_premium")
        for product in candidates.itertuples():
            units = min(gap / product.coverage, left / product.monthly_premium)
            if units <= 0: continue
            coverage = units * product.coverage; premium = units * product.monthly_premium
            chosen[kind] = {"coverage": coverage, "premium": premium, "product": product.product_name}
            gap -= coverage; left -= premium
            if gap <= 0 or left < candidates.monthly_premium.min(): break
    return {"items": chosen, "premium": monthly_budget - left, "remaining_budget": left}

def build_plans(needs: dict, ranking: list[dict], products: pd.DataFrame, budget: float, age: int) -> list[dict]:
    plans = []
    for name, fraction, subtitle in [("A｜基礎保障", .45, "以預算約四成五補足優先缺口"), ("B｜平衡保障", .75, "以預算約四分之三平衡配置"), ("C｜高保障", 1, "用滿設定預算，加深缺口補足")]:
        cap = budget * fraction
        plan = optimize_budget(needs, ranking, products, cap, age)
        total_cover = sum(x["coverage"] for x in plan["items"].values())
        weighted_gap = sum(max(0, needs["gaps"][k] - plan["items"][k]["coverage"]) for k in needs["gaps"])
        plan.update({"name": name, "subtitle": subtitle, "annual_premium": plan["premium"]*12,
                     "completeness": round(100 * (1-weighted_gap/max(1,sum(needs["needs"].values())))),
                     "total_cover": total_cover, "limitation": "虛擬商品與簡化額度；未納入核保、除外責任及保費變動。"})
        plans.append(plan)
    return plans
