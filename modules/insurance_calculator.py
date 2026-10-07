from __future__ import annotations
from utils.helpers import ASSUMPTIONS

def calculate_needs(profile: dict, finance: dict, family: dict, risks: dict) -> dict:
    available = finance["savings"] + finance["investments"]
    living = finance["monthly_expenses"] * 12 * ASSUMPTIONS["family_years"]
    education = family["children"] * ASSUMPTIONS["education_per_child"]
    household_liability = max(0, living + education + finance["mortgage"] + finance["debts"] - available)
    medical = ASSUMPTIONS["medical_base"] * (1 + max(0, risks["疾病風險"] - 35) / 100)
    accident = finance["annual_income"] * (4 + family["dependents"] * .5) * (1 + risks["意外風險"] / 250)
    critical = max(ASSUMPTIONS["critical_illness_base"], finance["annual_income"] * 2.5 * (1 + risks["疾病風險"] / 300))
    needs = {"壽險": household_liability, "醫療險": medical, "意外險": accident, "重大疾病": critical}
    current = {"壽險": finance["life_cover"], "醫療險": finance["medical_cover"], "意外險": finance["accident_cover"], "重大疾病": finance["critical_cover"]}
    gaps = {k: max(0, needs[k] - current[k]) for k in needs}
    completeness = round(sum(min(current[k], needs[k]) for k in needs) / max(1, sum(needs.values())) * 100)
    return {"needs": needs, "current": current, "gaps": gaps, "family_liability": household_liability, "available_assets": available, "completeness": completeness}
