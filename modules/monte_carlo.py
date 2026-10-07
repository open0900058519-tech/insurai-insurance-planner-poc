from __future__ import annotations
import numpy as np
import pandas as pd
from utils.helpers import ASSUMPTIONS

def simulate(finance: dict, profile: dict, selected_plan: dict, simulations: int = 6000, years: int = 20, seed: int = 42) -> tuple[pd.DataFrame, dict]:
    rng = np.random.default_rng(seed)
    n = simulations
    initial = finance["savings"] + finance["investments"]
    base_expenses = (finance["monthly_expenses"] + finance["housing_monthly"]) * 12
    income = np.full(n, finance["annual_income"], dtype=float)
    current = np.full(n, initial, dtype=float); recommended = current.copy(); alive=np.ones(n,dtype=bool)
    records=[]; event_rates={"health": .035 + max(0, profile["age"]-35)*.0007, "critical": .012 + max(0,profile["age"]-40)*.00035, "accident": .025 + (.02 if profile["work_type"]=="高風險工作" else .008 if profile["transport"]=="機車" else 0), "death": .003 + max(0,profile["age"]-45)*.0002}
    covers=selected_plan.get("items", {})
    for year in range(1, years+1):
        growth=np.clip(rng.normal(ASSUMPTIONS["annual_income_growth_mean"], ASSUMPTIONS["annual_income_growth_sd"], n), -.15,.15)
        income *= 1+growth
        expense=base_expenses*(1.02**year)*rng.lognormal(0,.04,n)
        returns=rng.normal(ASSUMPTIONS["annual_asset_return_mean"],ASSUMPTIONS["annual_asset_return_sd"],n)
        health=rng.random(n)<event_rates["health"]; critical=rng.random(n)<event_rates["critical"]; accident=rng.random(n)<event_rates["accident"]
        death=alive & (rng.random(n)<event_rates["death"])
        alive &= ~death
        income_disruption=(health|critical|accident)&(rng.random(n)<.25)
        earned_income=np.where(alive,np.where(income_disruption,income*rng.uniform(.25,.75,n),income),0)
        health_cost=health*rng.uniform(*ASSUMPTIONS["event_cost_health"],n); critical_cost=critical*rng.uniform(*ASSUMPTIONS["event_cost_critical"],n); accident_cost=accident*rng.uniform(*ASSUMPTIONS["event_cost_accident"],n)
        loss=health_cost+critical_cost+accident_cost
        current_cover={"醫療險":finance["medical_cover"],"重大疾病":finance["critical_cover"],"意外險":finance["accident_cover"],"壽險":finance["life_cover"]}
        extra={k:covers.get(k,{}).get("coverage",0) for k in current_cover}
        current_payout=(health*np.minimum(current_cover["醫療險"],health_cost)+critical*np.minimum(current_cover["重大疾病"],critical_cost)+accident*np.minimum(current_cover["意外險"],accident_cost)+death*current_cover["壽險"])
        recommended_payout=(health*np.minimum(current_cover["醫療險"]+extra["醫療險"],health_cost)+critical*np.minimum(current_cover["重大疾病"]+extra["重大疾病"],critical_cost)+accident*np.minimum(current_cover["意外險"]+extra["意外險"],accident_cost)+death*(current_cover["壽險"]+extra["壽險"]))
        premium=float(selected_plan.get("premium",0))*12
        survivor_expense=np.where(alive,expense,expense*.7)
        current=np.maximum(0,current*(1+returns)+earned_income-survivor_expense-finance["debts"]/5-loss+current_payout)
        recommended=np.maximum(0,recommended*(1+returns)+earned_income-survivor_expense-finance["debts"]/5-loss+recommended_payout-premium)
        records.extend([{"年數":year,"情境":"目前保障","資產":x} for x in current[::max(1,n//500)]])
        records.extend([{"年數":year,"情境":"推薦保障","資產":x} for x in recommended[::max(1,n//500)]])
    safe_current=float(np.mean(current>0)); safe_recommended=float(np.mean(recommended>0))
    metrics={"current":current,"recommended":recommended,"safety_current":safe_current,"safety_recommended":safe_recommended,
             "simulations":n,"years":years,"current_quantiles":np.quantile(current,[.1,.5,.9]),"recommended_quantiles":np.quantile(recommended,[.1,.5,.9]),"event_rates":event_rates}
    return pd.DataFrame(records), metrics
