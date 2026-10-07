from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from modules.risk_assessment import assess_risks
from modules.insurance_calculator import calculate_needs
from modules.recommendation import rank_gaps, build_plans
from modules.monte_carlo import simulate
from modules.ai_advisor import explain
from modules.report_generator import report_markdown
from utils.helpers import ASSUMPTIONS, DISCLAIMER, money, short_money, level

ROOT=Path(__file__).parent
st.set_page_config(page_title="InsurAI｜個人化保險規劃助手",page_icon="◈",layout="wide",initial_sidebar_state="expanded")
st.markdown("""<style>
.stApp{background:#f7f8f4}.block-container{max-width:1320px;padding-top:1.2rem}.hero{padding:2rem 2.3rem;border-radius:24px;background:linear-gradient(115deg,#102f35,#176a56);color:white;margin:0 0 1.2rem}.hero h1{font-size:2.5rem;margin:0 0 .4rem}.hero p{color:#d2e6dd;font-size:1rem;margin:0}.eyebrow{letter-spacing:.16em;color:#c4df74;font-size:.75rem;font-weight:700}.disclaimer{padding:.75rem 1rem;background:#fff6e8;border:1px solid #f0d4a8;border-radius:12px;color:#654814;font-size:.86rem}.kpi{padding:1rem 1.2rem;border:1px solid #e3e9e4;border-radius:16px;background:white}.muted{color:#687a75}.small{font-size:.82rem;color:#687a75}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="eyebrow">INSURTECH · PERSONAL COVERAGE PLANNER</div><h1>InsurAI｜個人化保險規劃助手</h1><p>不是推薦你買什麼，而是先讓你看見自己缺什麼。</p></div>',unsafe_allow_html=True)
st.markdown(f'<div class="disclaimer">{DISCLAIMER}</div>',unsafe_allow_html=True)

if "profile" not in st.session_state:
    st.session_state.profile={"name":"","age":35,"gender":"不指定","occupation":"一般職員","work_type":"辦公室","marital_status":"已婚","children":2,"dependents":2,"transport":"機車"}
if "finance" not in st.session_state:
    st.session_state.finance={"annual_income":600000,"monthly_expenses":30000,"housing_monthly":15000,"savings":200000,"investments":0,"mortgage":5000000,"debts":0,"life_cover":3000000,"medical_cover":500000,"accident_cover":1000000,"critical_cover":0,"budget":3000}
if "selected_plan" not in st.session_state: st.session_state.selected_plan=1
steps=["個人資料","財務資料","家庭責任","風險分析","保障缺口","預算與方案","Monte Carlo","AI 解釋","健檢報告"]
def go_to(index):
    st.session_state.page=steps[index]
with st.sidebar:
    st.markdown("### ◈ InsurAI")
    page=st.radio("健檢流程",steps,index=steps.index(st.session_state.get("page",steps[0])),key="page")
    st.progress((steps.index(page)+1)/len(steps),text=f"第 {steps.index(page)+1} 步 / 共 {len(steps)} 步")
    st.caption("新台幣｜資料僅供本次工作階段展示")
    if st.button("載入 Demo User",use_container_width=True):
        demo=json.loads((ROOT/"data/sample_users.json").read_text(encoding="utf-8"))
        st.session_state.profile={k:demo[k] for k in ["name","age","gender","occupation","work_type","marital_status","children","dependents","transport"]}
        st.session_state.finance={k:demo[k] for k in ["annual_income","monthly_expenses","housing_monthly","savings","investments","mortgage","debts","life_cover","medical_cover","accident_cover","critical_cover","budget"]}
        st.rerun()
    st.caption("產品均為 POC 虛擬商品")

def form_profile():
    d=st.session_state.profile
    st.header("01｜個人資料")
    st.caption("年齡與工作、通勤情況會影響模型中的疾病及意外風險假設。")
    with st.form("personal"):
        a,b,c=st.columns(3)
        d["name"]=a.text_input("姓名（選填）",d["name"])
        d["age"]=b.number_input("年齡",18,80,int(d["age"]))
        d["gender"]=c.selectbox("性別",["不指定","女","男"],index=["不指定","女","男"].index(d["gender"]))
        a,b,c=st.columns(3)
        d["occupation"]=a.text_input("職業",d["occupation"])
        d["work_type"]=b.selectbox("工作型態",["辦公室","一般勞務","高風險工作"],index=["辦公室","一般勞務","高風險工作"].index(d["work_type"]))
        d["marital_status"]=c.selectbox("婚姻狀況",["單身","已婚"],index=["單身","已婚"].index(d["marital_status"]))
        a,b,c=st.columns(3)
        d["children"]=a.number_input("子女數",0,10,int(d["children"]))
        d["dependents"]=b.number_input("扶養人口",0,10,int(d["dependents"]))
        d["transport"]=c.selectbox("每日主要交通方式",["大眾運輸","汽車","機車","步行"],index=["大眾運輸","汽車","機車","步行"].index(d["transport"]))
        st.form_submit_button("儲存並繼續 →",use_container_width=True,on_click=go_to,args=(1,))

def form_finance():
    d=st.session_state.finance
    st.header("02｜財務資料")
    st.caption("所有金額以新台幣計算；既有保障請填保單主要保障額度的概估。")
    with st.form("financial"):
        a,b,c=st.columns(3)
        d["annual_income"]=a.number_input("年收入",0,100_000_000,int(d["annual_income"]),step=50_000)
        d["monthly_expenses"]=b.number_input("每月生活支出",0,10_000_000,int(d["monthly_expenses"]),step=1_000)
        d["housing_monthly"]=c.number_input("每月房貸／房租",0,10_000_000,int(d["housing_monthly"]),step=1_000)
        a,b,c=st.columns(3)
        d["savings"]=a.number_input("現有存款",0,1_000_000_000,int(d["savings"]),step=10_000)
        d["investments"]=b.number_input("投資資產",0,1_000_000_000,int(d["investments"]),step=10_000)
        d["mortgage"]=c.number_input("房貸剩餘金額",0,1_000_000_000,int(d["mortgage"]),step=100_000)
        a,b=st.columns(2)
        d["debts"]=a.number_input("其他負債",0,1_000_000_000,int(d["debts"]),step=50_000)
        d["budget"]=b.number_input("每月保險預算",0,1_000_000,int(d["budget"]),step=500)
        st.markdown("**現有保障額度**")
        a,b,c,e=st.columns(4)
        for col,key,label in [(a,"life_cover","壽險"),(b,"medical_cover","醫療險"),(c,"accident_cover","意外險"),(e,"critical_cover","重大疾病")]: d[key]=col.number_input(label,0,1_000_000_000,int(d[key]),step=100_000)
        st.form_submit_button("儲存並繼續 →",use_container_width=True,on_click=go_to,args=(2,))

p=st.session_state.profile; f=st.session_state.finance
risks=assess_risks(p,f,p); analysis=calculate_needs(p,f,p,risks); ranking=rank_gaps(analysis,risks)
catalog=pd.read_csv(ROOT/"data/insurance_products.csv")
plans=build_plans(analysis,ranking,catalog,f["budget"],p["age"])
chosen=plans[st.session_state.selected_plan]
simulation_df,sim=simulate(f,p,chosen,ASSUMPTIONS["simulations"],ASSUMPTIONS["horizon_years"])
ai_data={"age":p["age"],"annual_income":f["annual_income"],"dependents":p["dependents"],"gaps":analysis["gaps"],"risks":risks,"budget":f["budget"],"recommended_premium":chosen["premium"],"safety_current":sim["safety_current"],"safety_recommended":sim["safety_recommended"],"plan":chosen["name"]}

if page=="個人資料": form_profile()
elif page=="財務資料": form_finance()
elif page=="家庭責任":
    st.header("03｜家庭責任分析")
    st.info("POC 假設：家庭生活需求 = 每月生活支出 × 12 × 10 年；每名子女教育費 200 萬元。家庭保障責任再加房貸及其他負債、扣除可動用資產。")
    a,b,c=st.columns(3); a.metric("生活需求估算",money(f["monthly_expenses"]*12*ASSUMPTIONS["family_years"])); b.metric("子女教育需求",money(p["children"]*ASSUMPTIONS["education_per_child"])); c.metric("家庭保障責任",money(analysis["family_liability"]))
    st.write(f"目前家庭情況：{p['marital_status']}、{p['children']} 名子女、{p['dependents']} 名扶養人口。負債含房貸 {money(f['mortgage'])}、其他負債 {money(f['debts'])}；可動用資產為 {money(analysis['available_assets'])}。")
    st.button("前往風險分析 →",on_click=go_to,args=(3,))
elif page=="風險分析":
    st.header("04｜個人風險分析")
    fig=go.Figure(go.Bar(x=list(risks.values())[:4],y=list(risks.keys())[:4],orientation="h",marker_color=["#eea56d" if x>=68 else "#176a56" if x<35 else "#7695b5" for x in list(risks.values())[:4]],text=[f"{x} · {level(x)}" for x in list(risks.values())[:4]],textposition="outside")); fig.update_layout(xaxis_range=[0,115],height=340,margin=dict(l=10,r=45,t=15,b=10),showlegend=False)
    st.plotly_chart(fig,use_container_width=True)
    a,b,c=st.columns(3); a.metric("緊急預備金",f"{risks['emergency_months']:.1f} 個月"); b.metric("財務風險",f"{risks['財務風險']} · {level(risks['財務風險'])}"); c.metric("家庭責任風險",f"{risks['家庭責任風險']} · {level(risks['家庭責任風險'])}")
    st.caption("風險分數為簡化規則模型，並非疾病機率或核保結果。預備金以存款與投資資產除以每月必要支出估算。")
elif page=="保障缺口":
    st.header("05｜保障需求與缺口")
    table=pd.DataFrame([{"保險類型":k,"目前保障":analysis["current"][k],"建議保障":analysis["needs"][k],"保障缺口":analysis["gaps"][k],"狀態":"高缺口" if analysis["gaps"][k]/max(1,analysis["needs"][k])>.6 else "中缺口" if analysis["gaps"][k]>0 else "已達估算"} for k in analysis["needs"]])
    st.dataframe(table,hide_index=True,use_container_width=True,column_config={k:st.column_config.NumberColumn(format="NT$ %d") for k in ["目前保障","建議保障","保障缺口"]})
    fig=go.Figure([go.Bar(name="目前保障",x=table["保險類型"],y=table["目前保障"],marker_color="#7695b5"),go.Bar(name="建議保障",x=table["保險類型"],y=table["建議保障"],marker_color="#176a56")]); fig.update_layout(barmode="group",height=360,yaxis_title="新台幣",margin=dict(t=20,b=10)); st.plotly_chart(fig,use_container_width=True)
    st.metric("保障完整度",f"{analysis['completeness']} / 100",help="以現有保障相對需求加權計算")
elif page=="預算與方案":
    st.header("06｜預算最佳化與推薦方案")
    f["budget"]=st.slider("每月保險預算（新台幣）",0,30000,int(min(30000,f["budget"])),step=500)
    st.caption("推薦系統以風險 40%＋缺口 30%＋家庭責任 20%＋財務風險 10% 加權排序，再按優先序配置虛擬商品。")
    rank=pd.DataFrame(ranking); st.dataframe(rank[["類型","缺口","風險分數","推薦分數"]],hide_index=True,use_container_width=True,column_config={"缺口":st.column_config.NumberColumn(format="NT$ %d")})
    cols=st.columns(3)
    for i,(col,plan) in enumerate(zip(cols,plans)):
        with col:
            st.markdown(f"### {plan['name']}")
            st.caption(plan["subtitle"])
            st.metric("月保費",money(plan["premium"]))
            st.write(f"年保費：{money(plan['annual_premium'])}")
            st.write(f"保障完整度：**{plan['completeness']} / 100**")
            for k,item in plan["items"].items(): st.write(f"{k}：{short_money(item['coverage'])}｜{money(item['premium'])}/月")
            st.caption("主要限制："+plan["limitation"])
            if st.button("選擇此方案",key=f"plan{i}",use_container_width=True): st.session_state.selected_plan=i; st.rerun()
    st.success(f"目前選擇：{plans[st.session_state.selected_plan]['name']}")
elif page=="Monte Carlo":
    st.header("07｜20 年 Monte Carlo 情境模擬")
    st.caption(f"NumPy 模擬 {sim['simulations']:,} 條路徑，納入疾病、重大醫療、意外、收入變動、家庭支出、資產報酬及情境理賠。")
    a,b=st.columns(2); a.metric("目前保障｜20 年後資產大於 0",f"{sim['safety_current']:.1%}"); b.metric("推薦保障｜20 年後資產大於 0",f"{sim['safety_recommended']:.1%}",delta=f"{(sim['safety_recommended']-sim['safety_current']):+.1%}")
    # Display a robust percentile band and median to keep the chart legible.
    quant=[]
    for scenario,array in [("目前保障",sim["current"]),("推薦保障",sim["recommended"])]:
        q=np.quantile(array,[.1,.5,.9]); quant.extend([{"情境":scenario,"分位":label,"資產":value} for label,value in zip(["最差 10%","中位數","最佳 10%"],q)])
    qdf=pd.DataFrame(quant); qfig=px.bar(qdf,x="分位",y="資產",color="情境",barmode="group",color_discrete_map={"目前保障":"#7695b5","推薦保障":"#176a56"}); qfig.update_layout(height=330,yaxis_title="20 年後資產（新台幣）")
    st.plotly_chart(qfig,use_container_width=True)
    st.caption("財務安全機率定義為模擬期末資產大於零的樣本比例。模擬假設為概念驗證用途，不是預測或真實統計。")
elif page=="AI 解釋":
    st.header("08｜AI 保險顧問")
    answer,mode=explain(ai_data); st.caption(f"目前模式：{mode}。LLM 只負責解釋 Python 已計算的結果，不產生保費或保障數字。")
    st.markdown(answer)
    question=st.text_input("也可以詢問本次分析",placeholder="例如：哪個保障缺口最大？")
    if question:
        response,mode=explain(ai_data,question); st.markdown(f"**InsurAI｜{mode}**\n\n{response}")
    st.caption("提示：為什麼需要壽險？預算只有 2,000 元怎麼辦？如果不增加保障會怎樣？")
else:
    st.header("09｜個人化 AI 保險健檢報告")
    st.subheader(f"{p.get('name') or '您的'}保險健康分數：{analysis['completeness']} / 100")
    st.markdown("### 目前風險")
    st.write("　｜　".join(f"{k}：{level(v)}（{v}/100）" for k,v in risks.items() if k.endswith("風險")))
    st.markdown("### 最大保障缺口")
    for row in ranking[:2]: st.write(f"**{row['類型']}**　目前 {money(analysis['current'][row['類型']])} → 建議 {money(analysis['needs'][row['類型']])}，缺口 {money(row['缺口'])}。")
    advice,mode=explain(ai_data); st.markdown("### AI 建議"); st.caption(mode); st.markdown(advice)
    st.markdown("### 模擬結果"); a,b=st.columns(2); a.metric("目前保障安全比例",f"{sim['safety_current']:.1%}"); b.metric("推薦方案安全比例",f"{sim['safety_recommended']:.1%}")
    report=report_markdown(p,f,risks,analysis,chosen,sim,advice)
    st.download_button("下載完整健檢報告（Markdown）",report,file_name="InsurAI_保險健檢報告.md",mime="text/markdown")
    st.markdown("### 完整報告預覽"); st.markdown(report)

st.divider()
st.markdown(f"<div class='small'>{DISCLAIMER}<br>產品目錄內所有保險名稱、額度與價格均為 <b>POC 虛擬商品</b>，不可視為真實商品。</div>",unsafe_allow_html=True)
