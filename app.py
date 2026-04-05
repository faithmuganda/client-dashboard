import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from streamlit_gsheets import GSheetsConnection
hide_attribution = """
    <style>
    /* Hides the "Created by" and other info in the sidebar footer */
    div[data-testid="stSidebarNav"] + div {
        display: none;
    }

    /* Specifically targets the 'Made with Streamlit' and user info in the menu */
    footer {
        visibility: hidden;
    }
    
    /* Optional: Hide the header bar at the top for a cleaner look */
    header {
        visibility: hidden;
    }
    </style>
    """
st.markdown(hide_attribution, unsafe_allow_html=True)
# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="Herbs & Spices Sales Dashboard")

# --- CUSTOM THEMING ---
HERBS_URL = "https://www.connectedwomen.co/wp-content/uploads/2016/08/shutterstock_448176067.jpg"

st.markdown(f"""
<style>
    .stApp {{ background-color: #FFFFFF !important; }}
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 160px;
        background-image: url("{HERBS_URL}"); background-size: contain;
        background-repeat: repeat-x; z-index: 999; pointer-events: none;
    }}
    .block-container {{
        background-color: #FFFFFF !important; 
        margin-top: 200px; margin-bottom: 30px; padding: 30px !important;
    }}
    .metric-card, .chart-container {{
        background-color: #fcfcfc !important; 
        padding: 20px; border-radius: 4px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #eeeeee; border-bottom: 4px solid #1b5e20;
    }}
    .main-title {{
        color: #1b5e20 !important; font-family: 'Georgia', serif;
        text-align: center; font-size: 2.9rem; font-weight: bold; margin-bottom: 10px;
    }}
    .metric-label {{ color: #000000 !important; font-size:18px; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ color: #000000 !important; font-size: 18px; font-weight: bold; }}
    .chart-heading {{ color: #000000 !important; font-weight: bold; text-align: center; margin-bottom: 5px; font-family: serif; font-size: 18px; }}
    
    .stDownloadButton button {{
        padding: 0.2rem 0.5rem !important;
        font-size: 12px !important;
        height: auto !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- GOOGLE SHEETS CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Use ttl=0 to always fetch fresh data on refresh
    df = conn.read(ttl=0) 
    
    # --- DATA PROCESSING ---
    df["Date"] = pd.to_datetime(df["Date"])
    df["Revenue"] = pd.to_numeric(df["Units_Sold"]) * pd.to_numeric(df["Selling_Price"])
    df["Profit"] = df["Revenue"] - (df["Units_Sold"] * pd.to_numeric(df.get("Cost", 0)))
    
    # --- HEADER SECTION ---
    st.markdown('<h1 class="main-title">Herbs & Spices Sales Dashboard</h1>', unsafe_allow_html=True)
    
    col_space, col_refresh = st.columns([6, 1])
    with col_refresh:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    # --- CALCULATIONS ---
    total_rev, total_profit = df["Revenue"].sum(), df["Profit"].sum()
    total_units = df["Units_Sold"].sum()
    
    if "Customer_ID" in df.columns:
        unique_cust = df["Customer_ID"].nunique()
        cust_counts = df["Customer_ID"].value_counts()
        repeat_cust = (cust_counts > 1).sum()
        repeat_rate = (repeat_cust / unique_cust * 100) if unique_cust > 0 else 0
    else:
        unique_cust = len(df)
        repeat_rate = 0
    avg_val = total_rev / unique_cust if unique_cust > 0 else 0

    # --- TOP KPI ROW ---
    m1, m2, m3, m4 = st.columns(4)
    metrics_data = [
        ("Total Sales", f"KSh {total_rev:,.0f}"),
        ("Total Profit", f"KSh {total_profit:,.0f}"),
        ("Units Sold", f"{total_units:,.0f}"),
        ("Avg Order Value", f"KSh {avg_val:,.2f}")
    ]
    for col, (label, val) in zip([m1, m2, m3, m4], metrics_data):
        col.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # FIXED: Axis Style with correct Plotly property nesting
    axis_style = dict(
        showgrid=True, 
        gridcolor='#eeeeee', 
        tickfont=dict(color='black'),
        title=dict(font=dict(color='black')) # Nested font inside title
    )

    # --- ROW 1: CHARTS ---
    r1c1, r1c2, r1c3 = st.columns([1.5, 1, 1.5])

    with r1c1:
        st.markdown(f'<div class="chart-container"><p class="chart-heading">Sales Overview</p>', unsafe_allow_html=True)
        daily = df.groupby(df["Date"].dt.strftime('%a')).agg({"Revenue":"sum", "Profit":"sum"}).reindex(['Mon','Tue','Wed','Thu','Fri','Sat','Sun']).reset_index()
        fig_ov = go.Figure()
        fig_ov.add_trace(go.Scatter(x=daily['Date'], y=daily['Revenue'], name='Sales', line=dict(color='#2e7d32', width=3), mode='lines+markers'))
        fig_ov.add_trace(go.Scatter(x=daily['Date'], y=daily['Profit'], name='Profit', line=dict(color='#ef6c00', width=3), mode='lines+markers'))
        fig_ov.update_layout(height=230, margin=dict(l=20,r=20,t=10,b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                             xaxis=axis_style, yaxis=axis_style, legend=dict(font=dict(color="black"), orientation="h", y=-0.2))
        st.plotly_chart(fig_ov, use_container_width=True)
        st.download_button("📥 Sales Data", daily.to_csv(index=False), "daily_sales.csv", key="dl_daily")
        st.markdown('</div>', unsafe_allow_html=True)

    with r1c2:
        st.markdown(f'<div class="chart-container"><p class="chart-heading">Top Selling Products</p>', unsafe_allow_html=True)
        top_p = df.groupby("Product")["Units_Sold"].sum().sort_values(ascending=False).reset_index()
        fig_p = px.bar(top_p.head(4), x="Units_Sold", y="Product", orientation='h', color_discrete_sequence=['#2e7d32'], text_auto=True)
        fig_p.update_layout(height=230, margin=dict(l=0,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                            xaxis=dict(visible=False), yaxis=axis_style)
        st.plotly_chart(fig_p, use_container_width=True)
        st.download_button("📥 Product Data", top_p.to_csv(index=False), "top_products.csv", key="dl_prod")
        st.markdown('</div>', unsafe_allow_html=True)

    with r1c3:
        st.markdown(f'<div class="chart-container"><p class="chart-heading">Profit Margin by Product</p>', unsafe_allow_html=True)
        margin_data = df.groupby("Product").agg({"Profit":"sum"}).reset_index().sort_values("Profit", ascending=False)
        fig_m = px.bar(margin_data.head(5), x="Product", y="Profit", color="Product", color_discrete_sequence=['#2e7d32', '#ff9800'], text_auto='.0f')
        fig_m.update_layout(height=230, margin=dict(l=10,r=10,t=10,b=10), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                            xaxis=axis_style, yaxis=dict(visible=False))
        st.plotly_chart(fig_m, use_container_width=True)
        st.download_button("📥 Margin Data", margin_data.to_csv(index=False), "profit_margins.csv", key="dl_margin")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ROW 2 ---
    r2c1, r2c2, r2c3, r2c4 = st.columns([1.5, 1, 1, 1.5])

    with r2c1:
        st.markdown(f'<div class="chart-container"><p class="chart-heading">Activity Heatmap</p>', unsafe_allow_html=True)
        # Note: Using random data here as per your original logic
        z_data = np.random.randint(1, 10, size=(6, 10)) 
        fig_h = px.imshow(z_data, color_continuous_scale='YlGn') 
        fig_h.update_layout(height=200, margin=dict(l=10,r=10,t=10,b=10), coloraxis_showscale=False, paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=axis_style, yaxis=axis_style)
        st.plotly_chart(fig_h, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r2c2:
        st.markdown(f'''<div class="metric-card" style="height:310px; text-align:left;">
            <p class="chart-heading">Customer Metrics</p>
            <p>👤 Total Customers: <b style="float:right;">{unique_cust}</b></p>
            <hr>
            <p>🔄 Repeat Rate: <b style="float:right;">{repeat_rate:.1f}%</b></p>
            <p>💰 Avg Value: <b style="float:right;">KSh {avg_val:,.0f}</b></p>
        </div>''', unsafe_allow_html=True)

    with r2c3:
        if "Stock" in df.columns:
            low_stock_df = df.groupby("Product")["Stock"].last().sort_values().head(3)
        else:
            low_stock_df = df.groupby("Product")["Units_Sold"].sum().sort_values().head(3)
        stock_items_html = "".join([f"<li>{prod}: <b>{int(val)} left</b></li>" for prod, val in low_stock_df.items()])
        st.markdown(f'''<div class="metric-card" style="height:310px; text-align:left;">
            <p class="chart-heading">Low Stock Alert</p>
            <ul>{stock_items_html}</ul>
        </div>''', unsafe_allow_html=True)

    with r2c4:
        st.markdown(f'<div class="chart-container"><p class="chart-heading">Monthly Trend</p>', unsafe_allow_html=True)
        df['Month'] = df['Date'].dt.strftime('%b')
        monthly = df.groupby('Month').agg({"Revenue":"sum", "Profit":"sum"}).reset_index()
        fig_mon = go.Figure()
        fig_mon.add_trace(go.Bar(x=monthly['Month'], y=monthly['Revenue'], marker_color='#1b5e20'))
        fig_mon.update_layout(height=200, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                             xaxis=axis_style, yaxis=axis_style, showlegend=False)
        st.plotly_chart(fig_mon, use_container_width=True)
        st.download_button("📥 Monthly Data", monthly.to_csv(index=False), "monthly_trend.csv", key="dl_monthly")
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Something went wrong: {e}")
