from __future__ import annotations

def assess_risks(profile: dict, finance: dict, family: dict) -> dict:
    age = profile["age"]
    disease = min(100, max(10, 18 + max(0, age - 25) * 1.15 + (15 if profile["work_type"] == "高風險工作" else 0)))
    accident = 20 + (30 if profile["work_type"] == "高風險工作" else 12 if profile["work_type"] == "一般勞務" else 0)
    accident += 20 if profile["transport"] == "機車" else 9 if profile["transport"] == "汽車" else 0
    emergency_months = (finance["savings"] + finance["investments"]) / max(1, finance["monthly_expenses"] + finance["housing_monthly"])
    reserve_score = 82 if emergency_months < 3 else 52 if emergency_months <= 6 else 25
    financial = min(100, max(10, reserve_score + min(25, finance["debts"] / max(1, finance["annual_income"]) * 8)))
    family_score = min(100, 12 + family["dependents"] * 14 + family["children"] * 9 + (18 if profile["marital_status"] == "已婚" else 0) + min(20, finance["mortgage"] / 1_000_000 * 3))
    return {"疾病風險": round(disease), "意外風險": round(min(100, accident)), "財務風險": round(financial), "家庭責任風險": round(min(100, family_score)), "emergency_months": emergency_months}
