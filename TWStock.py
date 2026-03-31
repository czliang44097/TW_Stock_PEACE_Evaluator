import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import requests
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. 頁面設定
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PEACE 台股品質分析 (雙引擎版)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. CSS 主題樣式管理
# -----------------------------------------------------------------------------
def inject_custom_css(theme_mode):
    base_css = """
    <style>
        .metric-card { padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .val-card { padding: 15px; border-radius: 10px; margin-bottom: 15px; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; }
        .val-label { font-size: 0.85rem; font-weight: 600; margin-bottom: 4px; }
        .val-value { font-size: 1.2rem; font-weight: 700; }
        .sentiment-card { padding: 15px; border-radius: 10px; border: 1px solid; text-align: center; margin-bottom: 15px; height: 100%; display: flex; flex-direction: column; justify-content: center; }
        .sentiment-label { font-size: 0.85rem; margin-bottom: 5px; font-weight: bold; }
        .sentiment-val { font-size: 1.4rem; font-weight: 800; }
        .sentiment-sub { font-size: 0.75rem; margin-top: 2px; }
        .check-item { display: flex; justify-content: space-between; align-items: flex-start; padding: 8px 0; border-bottom: 1px solid; }
        .check-item:last-child { border-bottom: none; }
        .check-label { font-weight: 500; font-size: 0.95rem; }
        .check-sub { font-size: 0.8rem; margin-top: 2px; }
        .status-pass { font-weight: bold; }
        .status-fail { font-weight: bold; }
        .strategy-box { padding: 15px; border-radius: 10px; margin-top: 20px; color: white !important; font-weight: 500; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .strategy-title { font-size: 1.2rem; font-weight: bold; margin-bottom: 5px; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 5px; color: white !important; }
        .strategy-desc { font-size: 0.95rem; margin-bottom: 8px; opacity: 0.95; color: white !important; }
        .strategy-tech { font-family: monospace; font-size: 0.85rem; background: rgba(0,0,0,0.2); padding: 5px; border-radius: 4px; color: #eee !important; }
    """
    
    light_css = """
        html, body, [class*="css"], .stMarkdown, .stMetric { color: #333333 !important; }
        .stApp { background-color: #f8fafc !important; }
        .metric-card { background-color: white !important; border: 1px solid #e2e8f0; }
        .val-card { background-color: #f0f9ff !important; border: 1px solid #bae6fd; }
        .val-label { color: #64748b !important; }
        .val-value { color: #0f172a !important; }
        .sentiment-card { border-color: #ddd; }
        .sentiment-label { color: #666 !important; }
        .sentiment-sub { color: #888 !important; }
        .check-item { border-bottom-color: #f1f5f9; }
        .check-label { color: #334155 !important; }
        .check-sub { color: #94a3b8 !important; }
        .status-pass { color: #22c55e !important; }
        .status-fail { color: #ef4444 !important; }
        .header-P { border-left: 5px solid #3b82f6; background: #eff6ff; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-weight:bold; color: #333 !important;}
        .header-E1 { border-left: 5px solid #22c55e; background: #f0fdf4; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-weight:bold; color: #333 !important;}
        .header-A { border-left: 5px solid #eab308; background: #fefce8; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-weight:bold; color: #333 !important;}
        .header-C { border-left: 5px solid #a855f7; background: #faf5ff; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-weight:bold; color: #333 !important;}
        .header-E2 { border-left: 5px solid #f97316; background: #fff7ed; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-weight:bold; color: #333 !important;}
    """
    
    dark_css = """
        html, body, [class*="css"], .stMarkdown, .stMetric { color: #e2e8f0 !important; }
        .stApp { background-color: #0e1117 !important; }
        .metric-card { background-color: #1e293b !important; border: 1px solid #334155; box-shadow: none; }
        .val-card { background-color: #172554 !important; border: 1px solid #1e3a8a; }
        .val-label { color: #94a3b8 !important; }
        .val-value { color: #f8fafc !important; }
        .sentiment-card { border-color: #334155; background-color: #1e293b !important; }
        .sentiment-label { color: #94a3b8 !important; }
        .sentiment-sub { color: #64748b !important; }
        .check-item { border-bottom-color: #334155; }
        .check-label { color: #e2e8f0 !important; }
        .check-sub { color: #94a3b8 !important; }
        .status-pass { color: #4ade80 !important; }
        .status-fail { color: #f87171 !important; }
        .header-P { border-left: 5px solid #3b82f6; background: #172554; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-weight:bold; color: #e2e8f0 !important;}
        .header-E1 { border-left: 5px solid #22c55e; background: #064e3b; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-weight:bold; color: #e2e8f0 !important;}
        .header-A { border-left: 5px solid #eab308; background: #422006; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-weight:bold; color: #e2e8f0 !important;}
        .header-C { border-left: 5px solid #a855f7; background: #3b0764; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-weight:bold; color: #e2e8f0 !important;}
        .header-E2 { border-left: 5px solid #f97316; background: #431407; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-weight:bold; color: #e2e8f0 !important;}
    """
    selected_css = dark_css if theme_mode == 'dark' else light_css
    st.markdown(base_css + selected_css + "</style>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. 雙引擎架構 - 資料獲取
# -----------------------------------------------------------------------------

# 【引擎 A】YFinance (處理即時股價、VIX、年度大表)
@st.cache_data(ttl=3600)
def fetch_stock_data_yf(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = {
            'symbol': ticker, 'shortName': ticker, 'currency': 'TWD',
            'currentPrice': 0, 'targetMeanPrice': 0,
            'longBusinessSummary': '無法獲取詳細簡介',
            'debtToEquity': None, 'currentRatio': None,
            'trailingPE': None, 'forwardPE': None, 'pegRatio': None, 
            'hist_pe_avg': None, 'hist_pe_min': None
        }
        try:
            full = stock.info
            if full and 'symbol' in full:
                for k in info.keys():
                    if k in full: info[k] = full[k]
        except: pass

        if info['currentPrice'] == 0:
            try: info['currentPrice'] = stock.fast_info.last_price
            except: pass

        def get_combined(annual, mode='sum'):
            try:
                ann = annual.T.sort_index()
                ann = ann[ann.index <= pd.Timestamp.now()].dropna(how='all')
                if not ann.empty:
                    ann.index = ann.index.astype(str).str[:4]
                    return ann
            except: pass
            return pd.DataFrame()

        fin = get_combined(stock.financials, 'sum')
        bal = get_combined(stock.balance_sheet, 'latest')
        cf = get_combined(stock.cashflow, 'sum')
        
        hist_price = pd.DataFrame()
        try: hist_price = stock.history(period="10y")
        except: pass

        return {'info': info, 'fin': fin, 'bal': bal, 'cf': cf, 'history': hist_price}, None
    except Exception as e: return None, f"YFinance API 錯誤: {e}"

# 【引擎 B】FinMind (處理精準台股季報)
@st.cache_data(ttl=3600)
def fetch_finmind_q_data(stock_id):
    # 去除 YF 的 .TW 後綴
    pure_id = stock_id.replace('.TW', '').replace('.TWO', '')
    url = "https://api.finmindtrade.com/api/v4/data"
    start_date = (pd.Timestamp.now() - pd.DateOffset(years=3)).strftime("%Y-%m-%d")
    
    params = {
        "dataset": "TaiwanStockFinancialStatements",
        "data_id": pure_id,
        "start_date": start_date
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data.get('msg') == 'success' and data.get('data'):
            return pd.DataFrame(data['data'])
    except: pass
    return pd.DataFrame()

# FinMind 季報還原器 (處理累計值問題)
def get_fm_series(df, keywords, is_pl=True):
    if df.empty: return pd.Series(dtype='float64')
    for kw in keywords:
        mask = df['type'].str.contains(kw, na=False, regex=False)
        if mask.any():
            s = df[mask].drop_duplicates(subset=['date']).set_index('date')['value']
            s.index = pd.to_datetime(s.index)
            s = s.sort_index()
            
            # 若為損益表(P&L)項目，進行反累加運算以取得「單季」數據
            if is_pl:
                s_single = s.copy()
                for i in range(1, len(s)):
                    # 若為同一個年度，單季 = 本季累計 - 上一季累計
                    if s.index[i].year == s.index[i-1].year:
                        s_single.iloc[i] = s.iloc[i] - s.iloc[i-1]
                return s_single
            return s
    return pd.Series(dtype='float64')

# -----------------------------------------------------------------------------
# 4. 輔助工具 (恐慌指數、策略計算)
# -----------------------------------------------------------------------------
def get_series(df, keywords):
    if df is None or df.empty: return pd.Series(dtype='float64')
    for k in keywords:
        if k in df.columns: return df[k]
    for c in df.columns:
        for k in keywords:
            if k.lower() in str(c).lower(): return df[c]
    return pd.Series(dtype='float64', index=df.index)

def calculate_strategy(history_df):
    try:
        if history_df is None or len(history_df) < 200: return None
        try: m = history_df['Close'].resample('ME').last()
        except: m = history_df['Close'].resample('M').last()
        if len(m) < 12: return None
        
        ma10 = m.rolling(10).mean()
        delta = m.diff()
        gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
        loss = -delta.clip(upper=0).ewm(alpha=1/14, adjust=False).mean()
        rsi = 100 - (100 / (1 + (gain/loss)))
        
        c_rsi = rsi.iloc[-1]
        c_ma = ma10.iloc[-1]
        c_p = m.iloc[-1]
        
        sig = {"rsi": c_rsi, "ma10": c_ma, "price": c_p, "title": "🟢 正常情況 (Standard)", "desc": "趨勢偏多，維持標準扣款。", "color": "#2ecc71"}
        if c_rsi < 30:
            sig.update({"title": "🔥 重押訊號 (Aggressive Buy)", "desc": "RSI嚴重超賣(<30)，啟動「機會加碼帳戶」分批大舉投入。", "color": "#ff4d4d"})
        elif c_rsi < 50 or c_p < c_ma:
            sig.update({"title": "🟡 加碼訊號 (Accumulate)", "desc": "RSI弱勢或跌破年線(10MA)，建議投入機會資金，扣款 1.5~2 倍。", "color": "#f1c40f"})
        return sig
    except: return None

def plot_gauge(cur, fair):
    if not fair or fair == 0: fair = cur
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta", value = cur,
        delta = {'reference': fair, 'relative': True, 'valueformat': ".1%", 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [fair*0.5, fair*1.5]}, 'steps': [{'range': [0, fair*0.8], 'color': '#22c55e'}, {'range': [fair*0.8, fair*1.2], 'color': '#eab308'}, {'range': [fair*1.2, fair*2.0], 'color': '#ef4444'}],
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': cur}
        },
        title = {'text': "目前股價 vs 合理價"}
    ))
    fig.update_layout(height=250, margin=dict(l=20,r=20,t=30,b=20), paper_bgcolor='rgba(0,0,0,0)')
    return fig

def plot_multi_bar(data, title, barmode='group'):
    if data is None or ((isinstance(data, pd.DataFrame) or isinstance(data, pd.Series)) and data.empty): return None
    df = data.to_frame(name='Value') if isinstance(data, pd.Series) else data.copy()
    
    if not df.index.empty and isinstance(df.index[0], pd.Timestamp):
        df.index = [f"{d.year}-Q{d.quarter}" for d in df.index]

    df = df.dropna(how='all')
    df_plot = df.reset_index().melt(id_vars='index')
    fig = px.bar(df_plot, x='index', y='value', color='variable', barmode=barmode, text_auto='.2s', color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_layout(title={'text': title, 'font': {'size': 11}, 'x':0}, height=180, margin=dict(l=0,r=0,t=30,b=0), xaxis=dict(title=None), yaxis=dict(title=None, showticklabels=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_traces(textposition='outside')
    return fig

# -----------------------------------------------------------------------------
# 5. 主程式 (啟動)
# -----------------------------------------------------------------------------
def main():
    with st.sidebar:
        st.header("🔍 台股搜尋")
        ticker_input = st.text_input("輸入台股代碼 (例如: 2330)", "2330").strip().upper()
        
        st.markdown("---")
        mode = st.toggle("🌙 夜間模式", value=False)
        theme_mode = 'dark' if mode else 'light'
        inject_custom_css(theme_mode)

    if not ticker_input: return
    
    if not ticker_input.endswith(".TW") and not ticker_input.endswith(".TWO"):
        ticker = f"{ticker_input}.TW"
    else:
        ticker = ticker_input

    # 驅動雙引擎
    data_yf, err = fetch_stock_data_yf(ticker)
    df_fm = fetch_finmind_q_data(ticker_input)

    if err:
        st.error(f"資料獲取失敗: {err}")
        return

    info = data_yf['info']
    fin_df, bal_df, cf_df = data_yf['fin'], data_yf['bal'], data_yf['cf']
    hist_price = data_yf['history']
    strategy_signal = calculate_strategy(hist_price)

    # 取出 YF 年度數據 (給不依賴季報的指標使用)
    op_inc_ann = get_series(fin_df, ['Operating Income', 'EBIT'])
    net_inc_ann = get_series(fin_df, ['Net Income'])
    ocf_ann = get_series(cf_df, ['Operating Cash Flow'])
    icf_ann = get_series(cf_df, ['Investing Cash Flow'])
    financing_cf_ann = get_series(cf_df, ['Financing Cash Flow'])
    fcf_ann = get_series(cf_df, ['Free Cash Flow'])
    if (fcf_ann.sum() == 0) and not ocf_ann.empty:
        capex = get_series(cf_df, ['Capital Expenditure'])
        fcf_ann = ocf_ann + capex
    equity_ann = get_series(bal_df, ['Stockholders Equity', 'Total Stockholder Equity'])
    total_debt_ann = get_series(bal_df, ['Total Debt'])
    total_assets_ann = get_series(bal_df, ['Total Assets'])
    rev_ann = get_series(fin_df, ['Total Revenue', 'Revenue'])

    # 取出 FinMind 季報數據 (專門突破近 4 季瓶頸)
    if not df_fm.empty:
        rev_q = get_fm_series(df_fm, ['營業收入合計', '營業收入', '收益合計', '淨收益']).tail(4)
        gp_q = get_fm_series(df_fm, ['營業毛利（毛損）', '營業毛利（毛損）淨額', '營業毛利']).tail(4)
        op_inc_q = get_fm_series(df_fm, ['營業利益（損失）', '營業利益']).tail(4)
        eps_q = get_fm_series(df_fm, ['基本每股盈餘（元）', '基本每股盈餘']).tail(4)
        ni_q = get_fm_series(df_fm, ['本期淨利（淨損）', '本期淨利']).tail(4)
        eq_q = get_fm_series(df_fm, ['權益總額', '權益總計'], is_pl=False).tail(4)
    else:
        # 極端情況防呆機制 (若 FinMind API 暫時無回應，給予空值避免崩潰)
        st.warning("⚠️ 無法獲取 FinMind 季報資料，部分近 4 季指標將暫時無法顯示。")
        rev_q = gp_q = op_inc_q = eps_q = ni_q = eq_q = pd.Series(dtype='float64')

    cur_price = info.get('currentPrice', 0)
    target_price = info.get('targetMeanPrice', cur_price)
    if not target_price or target_price == 0: target_price = cur_price

    # UI 顯示
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title(f"{info.get('shortName', ticker)}")
        st.markdown(f"### {info.get('currency', 'TWD')} {cur_price}")
        
        st.markdown("#### 📊 估值指標")
        def fmt_val(val, suffix='x'): return f"{val:.2f}{suffix}" if val and val > 0 else "-"
        
        pe_cur = info.get('trailingPE')
        pe_fwd = info.get('forwardPE')
        peg = info.get('pegRatio')
        
        v1, v2, v3, v4, v5, v6 = st.columns(6)
        with v1: st.markdown(f"""<div class="val-card"><div class="val-label">目前 PE</div><div class="val-value">{fmt_val(pe_cur)}</div></div>""", unsafe_allow_html=True)
        with v2: st.markdown(f"""<div class="val-card"><div class="val-label">5年平均 PE</div><div class="val-value">{fmt_val(info.get('hist_pe_avg'))}</div></div>""", unsafe_allow_html=True)
        with v3: st.markdown(f"""<div class="val-card"><div class="val-label">Forward PE</div><div class="val-value">{fmt_val(pe_fwd)}</div></div>""", unsafe_allow_html=True)
        with v4: st.markdown(f"""<div class="val-card"><div class="val-label">歷史最低 PE</div><div class="val-value">{fmt_val(info.get('hist_pe_min'))}</div></div>""", unsafe_allow_html=True)
        with v5: st.markdown(f"""<div class="val-card"><div class="val-label">PEG</div><div class="val-value">{fmt_val(peg, '')}</div></div>""", unsafe_allow_html=True)

    with col2:
        fair_val = st.number_input("合理價 (Fair Value)", value=float(target_price))
        st.plotly_chart(plot_gauge(cur_price, fair_val), use_container_width=True)
        if strategy_signal:
            st.markdown(f"""<div class="strategy-box" style="background-color: {strategy_signal['color']}"><div class="strategy-title">{strategy_signal['title']}</div><div class="strategy-desc">{strategy_signal['desc']}</div><div class="strategy-tech">RSI(14): {strategy_signal['rsi']:.1f} | Price: {strategy_signal['price']:.2f} | 10MA: {strategy_signal['ma10']:.2f}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    results = []
    
    # 趨勢檢驗
    def get_annual_only(series): return series[series.index != "TTM"].dropna()
    def check_trend_annual(series):
        s = get_annual_only(series)
        if len(s) < 2: return False
        return all(v > 0 for v in s.values) and (s.values[-1] >= s.values[0] * 0.95)
    
    def check_trend_q(series):
        if series is None or len(series) < 2: return False
        return all(v > 0 for v in series.values) and (series.values[-1] >= series.values[0] * 0.95)
    
    def check_growth_q(series):
        if series is None or len(series) < 2: return False
        return ((series.values[-1] - series.values[0]) / abs(series.values[0])) > 0

    # 確保預防空值崩潰
    latest_eps_q = eps_q.values[-1] if not eps_q.empty else 0

    # <P營利>
    results.append({'cat': 'P', 'id': 1, 'name': '近4季營收為正、不衰退', 'pass': check_trend_q(rev_q), 'val': '近4季趨勢', 'chart': rev_q})
    results.append({'cat': 'P', 'id': 2, 'name': '近4季毛利率為正、不衰退', 'pass': check_trend_q(gp_q), 'val': '近4季趨勢', 'chart': gp_q})
    results.append({'cat': 'P', 'id': 3, 'name': '近4季營業利益為正、不衰退', 'pass': check_trend_q(op_inc_q), 'val': '近4季趨勢', 'chart': op_inc_q})
    results.append({'cat': 'P', 'id': 4, 'name': '近4季EPS為正、不衰退', 'pass': check_trend_q(eps_q), 'val': f"最新(Q): {latest_eps_q:.2f}", 'chart': eps_q, 'star': True})

    # <E增長>
    results.append({'cat': 'E', 'id': 5, 'name': '近4季總營收正成長', 'pass': check_growth_q(rev_q), 'val': '近4季成長', 'chart': rev_q})
    results.append({'cat': 'E', 'id': 6, 'name': '近4季營業利益正成長', 'pass': check_growth_q(op_inc_q), 'val': '近4季成長', 'chart': op_inc_q})
    results.append({'cat': 'E', 'id': 7, 'name': '近4季EPS正成長', 'pass': check_growth_q(eps_q), 'val': '近4季成長', 'chart': eps_q, 'star': True})

    # <A現金> (使用 YFinance 年度)
    df_8 = pd.DataFrame({'營運(OCF)': ocf_ann, '自由(FCF)': fcf_ann})
    pass_8 = check_trend_annual(ocf_ann) and check_trend_annual(fcf_ann)
    results.append({'cat': 'A', 'id': 8, 'name': '營運現金流、自由現金流持續增加且皆為正', 'pass': pass_8, 'val': '雙現金流對比', 'chart': df_8, 'mode': 'group', 'star': True})
    
    df_9 = pd.DataFrame({'營運(OCF)': ocf_ann, '投資(ICF)': icf_ann, '融資(FinCF)': financing_cf_ann})
    ocf_a = get_annual_only(ocf_ann)
    icf_a = get_annual_only(icf_ann)
    fin_a = get_annual_only(financing_cf_ann)
    common_idx = ocf_a.index.intersection(icf_a.index).intersection(fin_a.index)
    pass_9 = False
    if len(common_idx) > 0: pass_9 = all(ocf_a[common_idx] > (icf_a[common_idx].abs() + fin_a[common_idx].abs()))
    results.append({'cat': 'A', 'id': 9, 'name': '營運現金流 > 融資、投資現金流', 'pass': pass_9, 'val': '三流並列', 'chart': df_9, 'mode': 'group', 'star': True})
    
    ratio_q_ttm = ocf_ann.values[-1] / net_inc_ann.values[-1] if not net_inc_ann.empty and net_inc_ann.values[-1] != 0 else 0
    pass_10 = ratio_q_ttm > 0.8
    cash_quality_series = (ocf_ann / net_inc_ann).replace([np.inf, -np.inf], 0).fillna(0)
    results.append({'cat': 'A', 'id': 10, 'name': '收益質量(營運現金流/淨利) > 0.8', 'pass': pass_10, 'val': f"最新(Y): {ratio_q_ttm:.2f}", 'chart': cash_quality_series, 'star': True})

    # <C保守與安全性>
    de_ratio = info.get('debtToEquity')
    if de_ratio is None: de_ratio = 0
    else: de_ratio = de_ratio / 100 

    curr_ratio = info.get('currentRatio')
    if curr_ratio is None or curr_ratio == 0:
        if not bal_df.empty:
            ca_col = next((c for c in bal_df.columns if 'Total Current Assets' in str(c) or 'Current Assets' in str(c)), None)
            cl_col = next((c for c in bal_df.columns if 'Total Current Liabilities' in str(c) or 'Current Liabilities' in str(c)), None)
            if ca_col and cl_col:
                try:
                    ca_val = bal_df[ca_col].iloc[-1]
                    cl_val = bal_df[cl_col].iloc[-1]
                    if cl_val > 0: curr_ratio = ca_val / cl_val
                except: pass
    if curr_ratio == 0: curr_ratio = None

    results.append({'cat': 'C', 'id': 11, 'name': 'D/E Ratio < 0.5', 'pass': de_ratio < 0.5, 'val': f"D/E: {de_ratio:.2f}", 'chart': None, 'star': True})
    
    pass_12 = curr_ratio > 1 if curr_ratio is not None else False
    val_12 = f"CR: {curr_ratio:.2f}" if curr_ratio is not None else "CR: N/A"
    results.append({'cat': 'C', 'id': 12, 'name': '流動比率 > 100%', 'pass': pass_12, 'val': val_12, 'chart': None})
    
    debt_years = (total_debt_ann.values[-1] / net_inc_ann.values[-1]) if (not total_debt_ann.empty and not net_inc_ann.empty and net_inc_ann.values[-1] > 0) else 99
    results.append({'cat': 'C', 'id': 13, 'name': '長期負債/淨利 < 4', 'pass': debt_years < 4, 'val': f"{debt_years:.1f}", 'chart': None})
    
    # <E效率與經營能力>
    try:
        if not ni_q.empty and not eq_q.empty and eq_q.values[-1] > 0:
            roe_4q = (ni_q.sum() / eq_q.values[-1]) * 100
        else:
            roe_4q = 0
    except: roe_4q = 0
    results.append({'cat': 'E_EFF', 'id': 14, 'name': '近4季 ROE > 15%', 'pass': roe_4q > 15, 'val': f"{roe_4q:.1f}%", 'chart': None, 'star': True})
    
    ato = (rev_ann.values[-1] / total_assets_ann.values[-1]) if not total_assets_ann.empty and total_assets_ann.values[-1] > 0 else 0
    results.append({'cat': 'E_EFF', 'id': 15, 'name': '總資產週轉率 > 0.7', 'pass': ato > 0.7, 'val': f"{ato:.2f}", 'chart': None})
    
    try:
        tax_rate = 0.20
        latest_equity = equity_ann.values[-1] if not equity_ann.empty else 0
        latest_debt = total_debt_ann.values[-1] if not total_debt_ann.empty else 0
        invested_capital = latest_equity + latest_debt
        if invested_capital > 0 and not op_inc_ann.empty:
            roic = (op_inc_ann.values[-1] * (1 - tax_rate)) / invested_capital
        else: roic = 0
    except: roic = 0

    try:
        beta = info.get('beta', 1.2) 
        if beta is None: beta = 1.2
        wacc = 0.045 + beta * 0.05
    except: wacc = 0.08 

    results.append({'cat': 'E_EFF', 'id': 16, 'name': 'ROIC > WACC', 'pass': roic > wacc, 'val': f"ROIC: {roic*100:.1f}% / WACC: {wacc*100:.1f}%", 'chart': None})

    main_score = sum(1 for r in results if r['pass'] and not r.get('extra'))
    
    st.markdown(f'<div style="background:#1e293b; color:white; padding:15px; border-radius:8px; display:flex; justify-content:space-between; margin-bottom:20px;"><h3 style="margin:0">PEACE 總分</h3><h2 style="margin:0; color:{"#4ade80" if main_score>=11 else "#facc15"}">{main_score} / 16</h2></div>', unsafe_allow_html=True)

    cats = [('獲利 (P)', 'P', 'header-P'), ('成長 (E)', 'E', 'header-E1'), ('現金 (A)', 'A', 'header-A'), ('保守 (C)', 'C', 'header-C'), ('效率 (E)', 'E_EFF', 'header-E2')]
    cols = st.columns(3)
    for idx, (title, key, css) in enumerate(cats):
        with cols[idx % 3]:
            st.markdown(f'<div class="metric-card"><div class="{css}">{title}</div>', unsafe_allow_html=True)
            for item in [r for r in results if r['cat'] == key]:
                status = "status-pass" if item['pass'] else "status-fail"
                icon = "✔" if item['pass'] else "✘"
                label_prefix = "⭐ " if item.get("star") else ""
                if item.get('extra'): label_prefix = "➕ "
                st.markdown(f'<div class="check-item"><div><div class="check-label">{label_prefix}{item["id"]}. {item["name"]}</div><div class="check-sub">{item["val"]}</div></div><div class="{status}">{icon}</div></div>', unsafe_allow_html=True)
                if item['chart'] is not None:
                    st.plotly_chart(plot_multi_bar(item['chart'], "", item.get('mode', 'group')), use_container_width=True, key=f"ch_{item['id']}")
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
