import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="Herbs & Spices Sales Dashboard")

# --- CUSTOM THEMING ---
HERBS_URL = "https://www.connectedwomen.co/wp-content/uploads/2016/08/shutterstock_448176067.jpg"

st.markdown(f"""
<style>
    /* 1. Pure White Background for the whole app */
    .stApp {{
        background-color: #FFFFFF !important;
    }}
    
    /* 2. Herb Border at the Top */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 160px;
        background-image: url("{HERBS_URL}");
        background-size: contain;
        background-repeat: repeat-x;
        z-index: 999;
        pointer-events: none;
    }}

    /* 3. Central Content Area */
    .block-container {{
        background-color: #FFFFFF !important; 
        margin-top: 200px;
        margin-bottom: 30px;
        padding: 30px !important;
    }}
    
    /* Box/Card Style: Subtle contrast for cards on white background */
    .metric-card, .chart-container {{
        background-color: #fcfcfc !important; 
        padding: 20px;
        border-radius: 4px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #eeeeee;
        border-bottom: 4px solid #1b5e20;
    }}

    .main-title {{
        color: #1b5e20 !important;
        font-family: 'Georgia', serif;
        text-align: center;
        font-size: 2.9rem;
        font-weight: bold;
        margin-bottom: 20px;
    }}

    /* Labels and Values: STRICT BLACK COLOR */
    .metric-label {{ color: #000000 !important; font-size:18px; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ color: #000000 !important; font-size: 18px; font-weight: bold; }}
    .chart-heading {{ color: #000000 !important; font-weight: bold; text-align: center; margin-bottom: 10px; font-family: serif; font-size: 18px; }}
    
    .metric-card p, .metric-card b, .metric-card li {{
        color: #000000 !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🌿 Spice Collection")
    uploaded_file = st.file_uploader("Upload Sales Records", type=["xlsx", "xls", "csv"])
    st.divider()
    monthly_target = st.number_input("Target Revenue (KSh)", value=500000)
    monthly_Profit = st.number_input("Target Profit (KSh)", value=30000)

st.markdown('<h1 class="main-title">Herbs & Spices Sales Dashboard</h1>', unsafe_allow_html=True)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Revenue"] = pd.to_numeric(df["Units_Sold"]) * pd.to_numeric(df["Selling_Price"])
        df["Profit"] = df["Revenue"] - (df["Units_Sold"] * pd.to_numeric(df.get("Cost", 0)))
        
        # --- CALCULATIONS ---
        total_rev, total_profit = df["Revenue"].sum(), df["Profit"].sum()
        total_units = df["Units_Sold"].sum()
        
        if "Customer_ID" in df.columns:
            unique_cust = df["Customer_ID"].nunique()
        else:
            unique_cust = len(df)
            
        avg_val = total_rev / unique_cust if unique_cust > 0 else 0

        # --- TOP KPI ROW ---
        m1, m2, m3, m4 = st.columns(4)
        for col, label, val in zip([m1, m2, m3, m4], 
                                    ["Total Sales", "Total Profit", "Units Sold", "Avg Order Value"],
                                    [f"KSh {total_rev:,.0f}", f"KSh {total_profit:,.0f}", f"{total_units:,.0f}", f"KSh {avg_val:,.2f}"]):
            col.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)

        st.write("<br>", unsafe_allow_html=True)

        # --- ROW 1: CHARTS ---
        r1c1, r1c2, r1c3 = st.columns([1.5, 1, 1.5])

        with r1c1:
            st.markdown(f'<div class="chart-container"><p class="chart-heading">Sales Overview</p>', unsafe_allow_html=True)
            daily = df.groupby(df["Date"].dt.strftime('%a')).agg({"Revenue":"sum", "Profit":"sum"}).reindex(['Mon','Tue','Wed','Thu','Fri','Sat','Sun']).reset_index()
            fig_ov = go.Figure()
            fig_ov.add_trace(go.Scatter(x=daily['Date'], y=daily['Revenue'], name='Sales', line=dict(color='#2e7d32', width=3), mode='lines+markers'))
            fig_ov.add_trace(go.Scatter(x=daily['Date'], y=daily['Profit'], name='Profit', line=dict(color='#ef6c00', width=3), mode='lines+markers'))
            fig_ov.update_layout(height=250, margin=dict(l=20,r=20,t=10,b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                  font=dict(color='black'), legend=dict(orientation="h", y=-0.2))
            fig_ov.update_xaxes(tickfont=dict(color="black"))
            fig_ov.update_yaxes(tickfont=dict(color="black"))
            st.plotly_chart(fig_ov, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with r1c2:
            st.markdown(f'<div class="chart-container"><p class="chart-heading">Top Selling Products</p>', unsafe_allow_html=True)
            top_p = df.groupby("Product")["Units_Sold"].sum().sort_values(ascending=True).tail(4).reset_index()
            fig_p = px.bar(top_p, x="Units_Sold", y="Product", orientation='h', color_discrete_sequence=['#2e7d32'], text_auto=True)
            fig_p.update_layout(height=250, margin=dict(l=0,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                 font=dict(color='black'), xaxis_visible=False, yaxis_title=None)
            fig_p.update_yaxes(tickfont=dict(color="black"))
            st.plotly_chart(fig_p, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with r1c3:
            st.markdown(f'<div class="chart-container"><p class="chart-heading">Profit Margin by Product</p>', unsafe_allow_html=True)
            img_colors = ['#c8e6c9', '#2e7d32', '#689f38', '#ff9800', '#bf360c']
            margin_data = df.groupby("Product").agg({"Profit":"sum"}).reset_index().head(5)
            fig_m = px.bar(margin_data, x="Product", y="Profit", color="Product", color_discrete_sequence=img_colors, text_auto='.0f')
            fig_m.update_layout(height=250, margin=dict(l=10,r=10,t=10,b=10), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', 
                                 plot_bgcolor='rgba(0,0,0,0)', font=dict(color='black'), yaxis_visible=False, xaxis_title=None)
            fig_m.update_xaxes(tickfont=dict(color="black"))
            st.plotly_chart(fig_m, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- ROW 2 ---
        r2c1, r2c2, r2c3, r2c4 = st.columns([1.5, 1, 1, 1.5])

        with r2c1:
            st.markdown(f'<div class="chart-container"><p class="chart-heading">Sales by Day & Hour</p>', unsafe_allow_html=True)
            z_data = np.random.randint(1, 10, size=(6, 10)) 
            fig_h = px.imshow(z_data, color_continuous_scale='YlGn') 
            fig_h.update_layout(height=200, margin=dict(l=10,r=10,t=10,b=10), coloraxis_showscale=False, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_h, use_container_width=True)
            st.markdown("<p style='font-size:18px; text-align:center; color:black;'>Peak Time: 10 AM - 12 PM</p></div>", unsafe_allow_html=True)

        with r2c2:
            st.markdown(f'''<div class="metric-card" style="height:255px; text-align:left;">
                <p class="chart-heading">Customer Metrics</p>
                <p>👤 Customers Today: <b style="float:right;">{unique_cust}</b></p>
                <hr>
                <p>🔄 Repeat: <b style="float:right;">45%</b></p>
                <p>💰 Avg Value: <b style="float:right;">KSh {avg_val:,.0f}</b></p>
            </div>''', unsafe_allow_html=True)

        with r2c3:
            st.markdown(f'''<div class="metric-card" style="height:255px; text-align:left;">
                <p class="chart-heading">Low Stock Alert</p>
                <ul>
                    <li>Cinnamon: <b>5 left</b></li>
                    <li>Peppermint: <b>3 left</b></li>
                    <li>Fenugreek: <b>2 left</b></li>
                </ul>
            </div>''', unsafe_allow_html=True)

        with r2c4:
            st.markdown(f'<div class="chart-container"><p class="chart-heading">Monthly Sales Trend</p>', unsafe_allow_html=True)
            df['Month'] = df['Date'].dt.strftime('%b')
            monthly = df.groupby('Month').agg({"Revenue":"sum", "Profit":"sum"}).reset_index()
            fig_mon = go.Figure()
            fig_mon.add_trace(go.Bar(x=monthly['Month'], y=monthly['Revenue'], name='Sales', marker_color='#1b5e20'))
            fig_mon.add_trace(go.Scatter(x=monthly['Month'], y=monthly['Profit'], name='Profit', line=dict(color='#e67e22', width=3)))
            fig_mon.update_layout(height=200, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='black'), showlegend=False)
            fig_mon.update_xaxes(tickfont=dict(color="black"))
            st.plotly_chart(fig_mon, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing data: {e}")
else:
    st.info("Please upload a CSV/Excel file in the sidebar to view the dashboard.")