"""Shared assumptions and formatting helpers for the InsurAI POC."""
from __future__ import annotations

ASSUMPTIONS = {
    "family_years": 10,
    "education_per_child": 2_000_000,
    "medical_base": 1_000_000,
    "critical_illness_base": 1_000_000,
    "emergency_months": 6,
    "simulations": 6000,
    "horizon_years": 20,
    "safety_floor": 0,
    "event_cost_health": (500_000, 2_500_000),
    "event_cost_critical": (1_000_000, 4_000_000),
    "event_cost_accident": (200_000, 1_800_000),
    "annual_income_growth_mean": 0.02,
    "annual_income_growth_sd": 0.035,
    "annual_asset_return_mean": 0.025,
    "annual_asset_return_sd": 0.07,
}

DISCLAIMER = (
    "⚠️ 本系統為教育與概念驗證用途，計算結果為模擬結果，不構成實際保險、投資或財務建議。"
    "實際保險需求與商品內容應以保險公司正式條款及專業人員評估為準。"
)

def money(value: float) -> str:
    return f"NT$ {value:,.0f}"

def level(score: float) -> str:
    return "低" if score < 35 else "中" if score < 68 else "高"

def short_money(value: float) -> str:
    if abs(value) >= 100_000_000:
        return f"{value / 100_000_000:.1f} 億"
    if abs(value) >= 10_000:
        return f"{value / 10_000:.0f} 萬"
    return money(value)
