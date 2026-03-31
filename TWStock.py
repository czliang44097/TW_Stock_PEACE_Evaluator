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
    page_title="PEACE 台股品質分析",
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
# 3. 輔助函數
# -----------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def fetch_sp500_pe():
    try: return yf.Ticker("SPY").info.get('trailingPE')
    except: return None

@st.cache_data(ttl=3600)
def fetch_fear_greed():
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile"}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            d = r.json().get('fear_and_greed', {})
            return {"score": float(d.get('score', 0)), "rating": d.get('rating', 'Neutral')}
    except: pass
    return None

def _fetch_realized_vol(ticker, window=21):
    try:
        hist = yf.Ticker(ticker).history(period="3mo")
        if hist.empty: return None
        hist['Log_Ret'] = np.log(hist['Close'] / hist['Close'].shift(1))
        hist['Volatility'] = hist['Log_Ret'].rolling(window=window).std() * np.sqrt(252) * 100
        return hist['Volatility'].dropna().iloc[-1]
    except: return None

@st.cache_data(ttl=3600)
def fetch_vix_data():
    vix_config = {
        "S&P 500 VIX": {"ticker": "^VIX", "proxy": "SPY"},
        "Nasdaq VIX": {"ticker": "^VXN", "proxy": "QQQ"},
        "Semi VIX": {"ticker": "^VXSOX", "proxy": "SMH"}
    }
    results = {}
    for name, cfg in vix_config.items():
        try:
            t_obj = yf.Ticker(cfg["ticker"])
            val = None
            try: val = t_obj.fast_info.last_price
            except: pass
            hist = t_obj.history(period="5y")
            if val is None and not hist.empty: val = hist['Close'].iloc[-1]
            
            if name == "Semi VIX" and (val is None or val <= 0 or hist.empty):
                calc_vol = _fetch_realized_vol(cfg["proxy"])
                if calc_vol:
                    results[name] = {"val": calc_vol, "pr": 50, "is_proxy": True}
                    continue
            
            if val is not None and not hist.empty:
                pr = (hist['Close'] < val).mean() * 100
                results[name] = {"val": val, "pr": pr, "is_proxy": False}
            else: results[name] = None
        except: results[name] = None
    return results

def get_vix_status_color(pr, is_proxy=False):
    if is_proxy: return "#888", "ETF波動率 (估算)"
    if pr is None: return "#888", "N/A"
    if pr > 90: return "#ff4d4d", "極度恐慌 (重押)"
    if pr > 80: return "#f1c40f", "恐慌 (加碼)"
    if pr < 20: return "#3498db", "貪婪 (減碼)"
    return "#2ecc71", "正常波動"

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

@st.cache_data(ttl=3600)
def scrape_yahoo_valuation(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}/key-statistics"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    result = {'trailingPE': None, 'forwardPE': None, 'pegRatio': None, 'hist_pe_avg': None, 'hist_pe_min': None}
    
    def extract_float(s):
        try:
            s = str(s).replace(',', '').strip()
            if s in ['N/A', '-', 'nan']: return None
            mult = 1
            if s.upper().endswith('T'): mult = 1e12; s=s[:-1]
            elif s.upper().endswith('B'): mult = 1e9; s=s[:-1]
            elif s.upper().endswith('M'): mult = 1e6; s=s[:-1]
            return float(s) * mult
        except: return None

    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code != 200: return result

        dfs = pd.read_html(r.text)
        target_df = None
        for df in dfs:
            if df.shape[1] > 1 and df.iloc[:, 0].astype(str).str.lower().str.contains("trailing p/e").any():
                target_df = df
                break
        
        if target_df is not None:
            for idx, row in target_df.iterrows():
                label = str(row.iloc[0]).lower()
                if "trailing p/e" in label:
                    result['trailingPE'] = extract_float(row.iloc[1])
                    hist_vals = []
                    for c in range(2, 7):
                        if c < len(row):
                            v = extract_float(row.iloc[c])
                            if v and v > 0: hist_vals.append(v)
                    if hist_vals:
                        result['hist_pe_avg'] = np.mean(hist_vals)
                        result['hist_pe_min'] = np.min(hist_vals)
                elif "forward p/e" in label:
                    result['forwardPE'] = extract_float(row.iloc[1])
                elif "peg ratio" in label:
                    result['pegRatio'] = extract_float(row.iloc[1])
        return result
    except:
        return result

def format_large_num(num):
    if num is None or np.isnan(num): return "0"
    if abs(num) >= 1e9: return f"{num/1e9:.2f}B"
    elif abs(num) >= 1e6: return f"{num/1e6:.2f}M"
    return f"{num:,.0f}"

# -----------------------------------------------------------------------------
# 4. 數據獲取 (核心 - 含備援機制)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        
        info = {
            'symbol': ticker, 'shortName': ticker, 'currency': 'TWD',
            'currentPrice': 0, 'targetMeanPrice': 0,
            'longBusinessSummary': '無法獲取詳細簡介',
            'debtToEquity': None, 'currentRatio': None,
            'trailingPE': None, 'forwardPE': None, 'pegRatio': None, 
            'earningsGrowth': None,
            'hist_pe_avg': None, 'hist_pe_min': None, 'beta': None,
            'pe_source': None, 'peg_source': None, 'hist_source': None
        }
        
        try:
            full = stock.info
            if full and 'symbol' in full:
                for k in info.keys():
                    if k in full: info[k] = full[k]
                for k in ['trailingPegRatio', 'targetMeanPrice']:
                    if k in full: info[k] = full[k]
        except: pass

        if info['currentPrice'] == 0:
            try:
                f = stock.fast_info
                if f: info['currentPrice'], info['currency'] = f.last_price, f.currency
            except: pass

        scraped = scrape_yahoo_valuation(ticker)
        if scraped['trailingPE']: 
            info['trailingPE'] = scraped['trailingPE']
            info['pe_source'] = 'Scraped'
        if scraped['forwardPE']:
            info['forwardPE'] = scraped['forwardPE']
        if scraped['pegRatio']:
            info['pegRatio'] = scraped['pegRatio']
            info['peg_source'] = 'Scraped'
        elif info.get('trailingPegRatio'):
            info['pegRatio'] = info.get('trailingPegRatio')
        if scraped['hist_pe_avg']:
            info['hist_pe_avg'] = scraped['hist_pe_avg']
            info['hist_source'] = 'Scraped (Table)'
        if scraped['hist_pe_min']:
            info['hist_pe_min'] = scraped['hist_pe_min']

        def get_combined(annual, quarterly, mode='sum'):
            try:
                ann = annual.T.sort_index()
                ann = ann[ann.index <= pd.Timestamp.now()].dropna(how='all')
            except: ann = pd.DataFrame()
            try:
                qrt = quarterly
                if qrt is not None and not qrt.empty:
                    q_sort = qrt.T.sort_index()
                    rec = q_sort.tail(4)
                    if not rec.empty:
                        val = rec.sum(axis=0, min_count=1) if mode == 'sum' else rec.iloc[-1]
                        df_ttm = pd.DataFrame(val).T
                        df_ttm.index = ["TTM"]
                        ann_str = ann.copy()
                        ann_str.index = ann_str.index.astype(str).str[:4]
                        return pd.concat([ann_str, df_ttm])
            except: pass
            if not ann.empty:
                ann.index = ann.index.astype(str).str[:4]
                return ann
            return pd.DataFrame()

        try:
            # 獲取年度資料 + TTM
            fin = get_combined(stock.financials, stock.quarterly_financials, 'sum')
            bal = get_combined(stock.balance_sheet, stock.quarterly_balance_sheet, 'latest')
            cf = get_combined(stock.cashflow, stock.quarterly_cashflow, 'sum')
            
            # 獲取純季報資料 (供近4季運算使用)
            fin_q = stock.quarterly_financials
            bal_q = stock.quarterly_balance_sheet
            cf_q = stock.quarterly_cashflow
            
            hist_price = pd.DataFrame()
            try: hist_price = stock.history(period="10y")
            except: pass

            if info['trailingPE'] is None:
                eps_col = next((c for c in fin.columns if 'Diluted EPS' in str(c) or 'Basic EPS' in str(c)), None)
                if eps_col:
                    try:
                        e_ttm = fin.loc["TTM", eps_col]
                        if e_ttm > 0: info['trailingPE'] = info['currentPrice'] / e_ttm
                    except: pass

            return {
                'info': info, 'fin': fin, 'bal': bal, 'cf': cf, 'history': hist_price,
                'fin_q': fin_q, 'bal_q': bal_q, 'cf_q': cf_q
            }, None

        except Exception as e: return None, f"數據處理錯誤: {e}"
    except Exception as e: return None, f"API 連線錯誤: {e}"

# -----------------------------------------------------------------------------
# 5. 繪圖與 HTML
# -----------------------------------------------------------------------------
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
    
    # 若為季報資料，將 index 轉成字串顯示比較好看
    if not df.index.empty and isinstance(df.index[0], pd.Timestamp):
        df.index = [f"{d.year}-Q{d.quarter}" for d in df.index]

    df = df.dropna(how='all')
    df_plot = df.reset_index().melt(id_vars='index')
    fig = px.bar(df_plot, x='index', y='value', color='variable', barmode=barmode, text_auto='.2s', color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_layout(title={'text': title, 'font': {'size': 11}, 'x':0}, height=180, margin=dict(l=0,r=0,t=30,b=0), xaxis=dict(title=None), yaxis=dict(title=None, showticklabels=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_traces(textposition='outside')
    return fig

def get_series(df, keywords):
    if df is None or df.empty: return pd.Series(dtype='float64')
    for k in keywords:
        if k in df.columns: return df[k]
    for c in df.columns:
        for k in keywords:
            if k.lower() in str(c).lower(): return df[c]
    return pd.Series(dtype='float64', index=df.index)

# -----------------------------------------------------------------------------
# 6. 主程式 (啟動)
# -----------------------------------------------------------------------------
def main():
    with st.sidebar:
        st.header("🔍 台股搜尋")
        # 前台只需要輸入數字代碼
        ticker_input = st.text_input("輸入台股代碼 (例如: 2330)", "2330").strip().upper()
        
        # 新增日夜模式切換
        st.markdown("---")
        mode = st.toggle("🌙 夜間模式", value=False) # False=Light, True=Dark
        theme_mode = 'dark' if mode else 'light'
        inject_custom_css(theme_mode)

    if not ticker_input: return
    
    # 後台自動補上 .TW (若使用者已打 .TW 或 .TWO 則不補)
    if not ticker_input.endswith(".TW") and not ticker_input.endswith(".TWO"):
        ticker = f"{ticker_input}.TW"
    else:
        ticker = ticker_input

    data, err = fetch_stock_data(ticker)
    fg_data = fetch_fear_greed()
    vix_data = fetch_vix_data()
    sp500_pe = fetch_sp500_pe()

    if err:
        st.error(f"資料獲取失敗: {err}")
        return

    info = data['info']
    fin_df, bal_df, cf_df = data['fin'], data['bal'], data['cf']
    hist_price = data['history']
    
    # 季報轉置並排序
    fin_q = data['fin_q'].T.sort_index() if data['fin_q'] is not None and not data['fin_q'].empty else pd.DataFrame()
    bal_q = data['bal_q'].T.sort_index() if data['bal_q'] is not None and not data['bal_q'].empty else pd.DataFrame()
    cf_q = data['cf_q'].T.sort_index() if data['cf_q'] is not None and not data['cf_q'].empty else pd.DataFrame()

    strategy_signal = calculate_strategy(hist_price)

    # 提取年度與 TTM 數據 (給部分原有邏輯使用)
    rev = get_series(fin_df, ['Total Revenue', 'Revenue'])
    op_inc = get_series(fin_df, ['Operating Income', 'EBIT'])
    net_inc = get_series(fin_df, ['Net Income'])
    ocf = get_series(cf_df, ['Operating Cash Flow'])
    icf = get_series(cf_df, ['Investing Cash Flow'])
    financing_cf = get_series(cf_df, ['Financing Cash Flow'])
    fcf = get_series(cf_df, ['Free Cash Flow'])
    if (fcf.sum() == 0) and not ocf.empty:
        capex = get_series(cf_df, ['Capital Expenditure'])
        fcf = ocf + capex
    equity = get_series(bal_df, ['Stockholders Equity', 'Total Stockholder Equity'])
    total_debt = get_series(bal_df, ['Total Debt'])
    total_assets = get_series(bal_df, ['Total Assets'])

    # 提取近 4 季數據
    rev_q = get_series(fin_q, ['Total Revenue', 'Revenue']).tail(4)
    gp_q = get_series(fin_q, ['Gross Profit']).tail(4)
    op_inc_q = get_series(fin_q, ['Operating Income', 'EBIT']).tail(4)
    eps_q = get_series(fin_q, ['Diluted EPS', 'Basic EPS']).tail(4)
    ni_q = get_series(fin_q, ['Net Income']).tail(4)
    eq_q = get_series(bal_q, ['Stockholders Equity', 'Total Stockholder Equity']).tail(4)

    cur_price = info.get('currentPrice', 0)
    target_price = info.get('targetMeanPrice', cur_price)
    if not target_price or target_price == 0: target_price = cur_price

    # UI 顯示
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title(f"{info.get('shortName', ticker)}")
        st.markdown(f"### {info.get('currency', 'TWD')} {cur_price}")
        st.caption(info.get('longBusinessSummary', '')[:150] + '...')
        
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
    
    # 趨勢檢驗：年度
    def get_annual_only(series): return series[series.index != "TTM"].dropna()
    def check_trend(series):
        s = get_annual_only(series)
        if len(s) < 2: return False
        return all(v > 0 for v in s.values) and (s.values[-1] >= s.values[0] * 0.95)
    
    # 趨勢檢驗：季報
    def check_trend_q(series):
        if series is None or len(series) < 2: return False
        return all(v > 0 for v in series.values) and (series.values[-1] >= series.values[0] * 0.95)
    
    # 成長檢驗：季報
    def check_growth_q(series):
        if series is None or len(series) < 2: return False
        return ((series.values[-1] - series.values[0]) / abs(series.values[0])) > 0

    # <P營利>
    results.append({'cat': 'P', 'id': 1, 'name': '近4季營收為正、不衰退', 'pass': check_trend_q(rev_q), 'val': '近4季趨勢', 'chart': rev_q})
    results.append({'cat': 'P', 'id': 2, 'name': '近4季毛利率為正、不衰退', 'pass': check_trend_q(gp_q), 'val': '近4季趨勢', 'chart': gp_q})
    results.append({'cat': 'P', 'id': 3, 'name': '近4季營業利益為正、不衰退', 'pass': check_trend_q(op_inc_q), 'val': '近4季趨勢', 'chart': op_inc_q})
    results.append({'cat': 'P', 'id': 4, 'name': '近4季(可用資料)EPS為正且不衰退', 'pass': check_trend_q(eps_q), 'val': f"最新(Q): {eps_q.values[-1] if not eps_q.empty else 0:.2f}", 'chart': eps_q, 'star': True})

    # <E增長>
    results.append({'cat': 'E', 'id': 5, 'name': '近4季總營收正成長', 'pass': check_growth_q(rev_q), 'val': '近4季成長', 'chart': rev_q})
    results.append({'cat': 'E', 'id': 6, 'name': '近4季營業利益正成長', 'pass': check_growth_q(op_inc_q), 'val': '近4季成長', 'chart': op_inc_q})
    results.append({'cat': 'E', 'id': 7, 'name': '近4季(可用資料)EPS正成長', 'pass': check_growth_q(eps_q), 'val': '近4季成長', 'chart': eps_q, 'star': True})

    # <A現金>
    df_8 = pd.DataFrame({'營運(OCF)': ocf, '自由(FCF)': fcf})
    pass_8 = check_trend(ocf) and check_trend(fcf)
    results.append({'cat': 'A', 'id': 8, 'name': '營運現金流、自由現金流持續增加且皆為正', 'pass': pass_8, 'val': '雙現金流對比', 'chart': df_8, 'mode': 'group', 'star': True})
    
    df_9 = pd.DataFrame({'營運(OCF)': ocf, '投資(ICF)': icf, '融資(FinCF)': financing_cf})
    ocf_ann = get_annual_only(ocf)
    icf_ann = get_annual_only(icf)
    fin_ann = get_annual_only(financing_cf)
    common_idx = ocf_ann.index.intersection(icf_ann.index).intersection(fin_ann.index)
    pass_9 = False
    if len(common_idx) > 0: pass_9 = all(ocf_ann[common_idx] > (icf_ann[common_idx].abs() + fin_ann[common_idx].abs()))
    results.append({'cat': 'A', 'id': 9, 'name': '營運現金流 > 融資、投資現金流', 'pass': pass_9, 'val': '三流並列', 'chart': df_9, 'mode': 'group', 'star': True})
    
    ratio_q_ttm = ocf.values[-1] / net_inc.values[-1] if not net_inc.empty and net_inc.values[-1] != 0 else 0
    pass_10 = ratio_q_ttm > 0.8
    cash_quality_series = (ocf / net_inc).replace([np.inf, -np.inf], 0).fillna(0)
    results.append({'cat': 'A', 'id': 10, 'name': '收益質量(營運現金流/淨利) > 0.8', 'pass': pass_10, 'val': f"最新(TTM): {ratio_q_ttm:.2f}", 'chart': cash_quality_series, 'star': True})

    # <C保守與安全性>
    de_ratio = 0
    de_source = "manual"
    if not total_debt.empty and not equity.empty:
        try: de_ratio = total_debt.values[-1] / equity.values[-1]
        except: de_source = "api"
    else: de_source = "api"
    if de_source == "api":
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
    
    debt_years = (total_debt.values[-1] / net_inc.values[-1]) if (not total_debt.empty and not net_inc.empty and net_inc.values[-1] > 0) else 99
    results.append({'cat': 'C', 'id': 13, 'name': '長期負債/淨利 < 4', 'pass': debt_years < 4, 'val': f"{debt_years:.1f}", 'chart': None})
    
    # <E效率與經營能力>
    try:
        if not ni_q.empty and not eq_q.empty and eq_q.values[-1] > 0:
            # 近4季淨利總和 / 最新一季股東權益
            roe_4q = (ni_q.sum() / eq_q.values[-1]) * 100
        else:
            roe_4q = 0
    except: roe_4q = 0
    results.append({'cat': 'E_EFF', 'id': 14, 'name': '近4季 ROE > 15%', 'pass': roe_4q > 15, 'val': f"{roe_4q:.1f}%", 'chart': None, 'star': True})
    
    ato = (rev.values[-1] / total_assets.values[-1]) if not total_assets.empty and total_assets.values[-1] > 0 else 0
    results.append({'cat': 'E_EFF', 'id': 15, 'name': '總資產週轉率 > 0.7', 'pass': ato > 0.7, 'val': f"{ato:.2f}", 'chart': None})
    
    try:
        tax_rate = 0.20 # 台股預設營所稅率20%
        latest_equity = equity.values[-1] if not equity.empty else 0
        latest_debt = total_debt.values[-1] if not total_debt.empty else 0
        invested_capital = latest_equity + latest_debt
        if invested_capital > 0 and not op_inc.empty:
            roic = (op_inc.values[-1] * (1 - tax_rate)) / invested_capital
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
