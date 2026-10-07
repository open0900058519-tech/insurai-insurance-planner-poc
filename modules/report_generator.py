from __future__ import annotations
from datetime import datetime
from utils.helpers import money, level, DISCLAIMER

def report_markdown(profile, finance, risks, needs, plan, simulation, advice):
    rows="\n".join(f"| {k} | {money(needs['current'][k])} | {money(needs['needs'][k])} | {money(needs['gaps'][k])} |" for k in needs["needs"])
    risk_lines="\n".join(f"- {k}：{level(v)}（{v}/100）" for k,v in risks.items() if k.endswith("風險"))
    return f"""# InsurAI｜AI 保險健檢報告

產生日期：{datetime.now().strftime('%Y-%m-%d')}  
分析對象：{profile.get('name') or '匿名使用者'}，{profile['age']} 歲

## 保險健康分數
**{needs['completeness']} / 100**（保障完整度簡化指標）

## 目前風險
{risk_lines}

## 保障缺口
| 類型 | 目前保障 | 建議估算 | 缺口 |
|---|---:|---:|---:|
{rows}

## 選擇方案：{plan['name']}
- 月保費估算：{money(plan['premium'])}；年保費：{money(plan['annual_premium'])}
- 組合保障完整度：{plan['completeness']} / 100

## 20 年情境模擬
- 目前保障財務安全比例：{simulation['safety_current']:.1%}
- 推薦情境財務安全比例：{simulation['safety_recommended']:.1%}
- 模擬次數：{simulation['simulations']:,}

## AI 解讀
{advice}

## 假設與提醒
家庭生活費採每月支出 × 12 × 10 年；子女教育需求每名 200 萬。產品資料均為 POC 虛擬商品。模擬使用示意事件率與資產報酬假設，非精算或真實統計。

{DISCLAIMER}
"""
