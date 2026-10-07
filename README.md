# InsurAI｜個人化保險規劃助手 POC

以繁體中文提供個人、財務、家庭責任風險分析、壽險／醫療險／意外險／重大疾病缺口估算、預算最佳化、可解釋規則推薦、20 年 Monte Carlo 情境比較、AI 解說與可下載健檢報告。金額皆為新台幣。所有模擬商品都標示為 **POC 虛擬商品**。

## 本機啟動

```bash
pip install -r requirements.txt
streamlit run app.py
```

進入左側流程後，可按「載入 Demo User」快速展示。依序完成個人資料、財務資料、家庭責任、風險分析、保障缺口、預算方案、Monte Carlo、AI 解釋及健檢報告。應用程式會將輸入保存在 Streamlit session state，不會自行寫入資料庫。

## AI 模式

未設定 `OPENAI_API_KEY` 時自動使用 Mock AI，完整流程仍可執行。啟用 OpenAI API 時，請在環境變數設定金鑰；可選擇用 `OPENAI_MODEL` 指定模型（預設 `gpt-4.1-mini`）。AI 只解釋 Python 已計算的結果；數字由本機模組計算。

PowerShell 範例：

```powershell
$env:OPENAI_API_KEY="你的API_KEY"
streamlit run app.py
```

## 模組

- `modules/risk_assessment.py`：疾病、意外、財務及家庭責任分數。
- `modules/insurance_calculator.py`：家庭責任、四類保障需求及保障缺口。
- `modules/recommendation.py`：加權排序、預算配置與三種方案。
- `modules/monte_carlo.py`：NumPy 20 年風險路徑及目前／推薦保障比較。
- `modules/ai_advisor.py`：OpenAI 解釋與無金鑰 Mock fallback、分析問答。
- `modules/report_generator.py`：個人化 Markdown 健檢報告。
- `utils/helpers.py`：集中管理 POC 假設、免責聲明及格式化。
- `data/insurance_products.csv`：虛擬商品目錄。
- `data/sample_users.json`：Demo User。

## POC 假設

家庭生活費需求採每月支出 × 12 × 10 年；每名子女教育費 200 萬；醫療及重大疾病保障以固定基礎額度加風險調整；意外保障依年收入及家庭人口估算。Monte Carlo 使用 6,000 次、20 年期模擬，事件率、事件損失、收入成長及資產報酬皆為示意假設，集中於 `utils/helpers.py` 與 `modules/monte_carlo.py`。財務安全定義為模擬期末資產大於零。

## 公開部署

可部署至支援 Streamlit 的託管服務（例如 Streamlit Community Cloud）：將專案放在 GitHub repository，選擇 `app.py` 作為入口並設定 Python dependencies。OpenAI 金鑰若使用，請透過託管平台的 Secrets 管理，切勿放進程式碼或公開 repository。部署平台可能要求登入、服務條款確認或公開 repository；部署前請先審閱平台的發布與資料處理設定。

## 限制與提醒

此 POC 不是保險銷售、核保或財務建議。計算模型、事件率及虛擬商品皆僅供概念展示；不代表真實統計、商品條款、保費或理賠結果。實際規劃請核對正式保單條款並諮詢合格專業人員。
