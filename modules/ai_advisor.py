from __future__ import annotations
import json
import os

def mock_advice(data: dict, question: str | None = None) -> str:
    gaps=data.get("gaps",{}); ranked=sorted(gaps,key=gaps.get,reverse=True)
    top=ranked[0] if ranked and gaps[ranked[0]]>0 else None
    if question:
        q=question.lower()
        if any(word in q for word in ["最大","缺口最大","largest"]):
            if top: return f"依這次計算，估算缺口最大的是「{top}」，約 {gaps[top]:,.0f} 元。這是簡化模型估值，請再核對現有保單內容。"
            return "目前資料不足，無法判斷；依本次估算沒有正向保障缺口。"
        if "預算" in q or "2000" in q or "2,000" in q:
            return f"目前分析使用的月預算是 {data.get('budget',0):,.0f} 元。若改為 2,000 元，請將預算調整後重新計算方案；推薦會按目前的缺口與加權優先序分配，不會假設能補足全部缺口。"
        if "壽險" in q:
            return f"壽險估算主要承接家庭生活費、子女教育、房貸與其他負債，並扣除可動用資產和既有壽險；本次估算缺口為 {gaps.get('壽險',0):,.0f} 元。"
        if "重大疾病" in q or "重疾" in q:
            return f"重大疾病保障的估算缺口為 {gaps.get('重大疾病',0):,.0f} 元，模型用它作為重大醫療與收入中斷的簡化緩衝額度。"
        if "不增加" in q or "不補" in q or "如果我不" in q:
            return f"模型中的目前保障情境，20 年後資產大於零的樣本比例是 {data.get('safety_current',0):.1%}。這只是依示意假設產生的情境比例，不是對個人的預測。"
        return "目前資料不足，無法判斷。你可以詢問本次已計算的保障缺口、預算配置、風險分數或 Monte Carlo 情境結果。"
    result=["以下解讀只使用本次試算結果；模擬不代表未來預測。"]
    if top: result.append(f"目前較大的估算缺口是「{top}」（{gaps[top]:,.0f} 元）。可先理解這項保障希望承接的財務責任，再對照現有保單條款。")
    else: result.append("依這組簡化公式，目前沒有明顯的正向保障缺口；仍建議核對保單定義、保障期間與除外責任。")
    result.append(f"您設定的每月預算為 {data.get('budget',0):,.0f} 元，系統按缺口優先分配，預估使用 {data.get('recommended_premium',0):,.0f} 元。預留緊急預備金有助避免保費壓縮日常現金流。")
    result.append(f"20 年情境模擬中，資產大於零的樣本比例為目前保障 {data.get('safety_current',0):.0%}、推薦情境 {data.get('safety_recommended',0):.0%}。這是模型內比例，會受簡化事件率、資產報酬與支出假設影響。")
    return "\n\n".join(result)

def explain(data: dict, question: str | None = None) -> tuple[str, str]:
    key=os.getenv("OPENAI_API_KEY")
    if not key: return mock_advice(data, question), "Mock AI（未設定 OPENAI_API_KEY）"
    try:
        from openai import OpenAI
        client=OpenAI(api_key=key)
        prompt=("你是 InsurAI 教育型保險規劃 POC 的解說助手。只根據下列已計算 JSON 回答，不能創造商品或數字；" 
                "不給投保指令，不做診斷；資料不足時回答『目前資料不足，無法判斷。』以繁體中文簡明回答。\n"+json.dumps(data,ensure_ascii=False))
        response=client.responses.create(model=os.getenv("OPENAI_MODEL","gpt-4.1-mini"),input=prompt+("\n使用者問題："+question if question else "\n請提供4點摘要。"))
        return response.output_text, "OpenAI API"
    except Exception as exc:
        return mock_advice(data, question)+f"\n\n（LLM 暫時無法使用，已切換 Mock AI：{type(exc).__name__}）", "Mock AI fallback"
