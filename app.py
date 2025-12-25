import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency, ttest_ind

# Set page config
st.set_page_config(page_title="Marketing Campaign Performance", layout="wide")

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .metric-card {
        background-color: var(--secondary-background-color);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Define Theme CSS
themes = {
    "light": """
        <style>
        :root {
            --primary-color: #4e8cff;
            --background-color: #ffffff;
            --secondary-background-color: #f0f2f6;
            --text-color: #262730;
            --widget-background-color: #ffffff;
            --widget-border-color: #d3d3d3;
        }
        /* Force background on main app and SIDEBAR */
        .stApp, section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
            color: #262730 !important;
        }
        .stApp header, .stApp footer {
            background-color: #ffffff !important;
        }
        /* Metric cards specific styling */
        .metric-card {
            background-color: #f0f2f6 !important;
            border: 1px solid #d3d3d3 !important;
            color: #262730 !important;
        }
        /* Force text color on all headers and text elements, including sidebar */
        h1, h2, h3, h4, h5, h6, p, li, span, div, label, .stMarkdown {
            color: #262730 !important;
        }
        /* Fix input fields in sidebar to look correct in light mode */
        .stTextInput input, .stSelectbox div, .stFileUploader div {
            color: #262730 !important;
            background-color: #ffffff !important;
        }
        /* Specific Fix for File Uploader in Light Mode */
        [data-testid="stFileUploader"] section {
            background-color: #f0f2f6 !important;
            color: #262730 !important;
        }
        [data-testid="stFileUploader"] button {
             background-color: #4e8cff !important; /* Primary color for button */
             color: #ffffff !important;
             border: none !important;
        }
        </style>
    """,
    "dark": """
        <style>
        :root {
            --primary-color: #4e8cff;
            --background-color: #0e1117;
            --secondary-background-color: #262730;
            --text-color: #fafafa;
            --widget-background-color: #262730;
            --widget-border-color: #464b5c;
        }
        /* Force background on main app and SIDEBAR */
        .stApp, section[data-testid="stSidebar"] {
            background-color: #0e1117 !important;
            color: #fafafa !important;
        }
        .stApp header, .stApp footer {
            background-color: #0e1117 !important;
        }
        .metric-card {
            background-color: #262730 !important;
            border: 1px solid #464b5c !important;
            color: #fafafa !important;
        }
         h1, h2, h3, h4, h5, h6, p, li, span, div, label, .stMarkdown {
            color: #fafafa !important;
        }
        /* Fix input fields in sidebar to look correct in dark mode */
        .stTextInput input, .stSelectbox div, .stFileUploader div {
            color: #fafafa !important;
            background-color: #262730 !important;
        }
        /* Specific Fix for File Uploader in Dark Mode */
        [data-testid="stFileUploader"] section {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        [data-testid="stFileUploader"] button {
             background-color: #4e8cff !important; /* Primary color for button */
             color: #ffffff !important;
             border: none !important;
        }
        </style>
    """
}

# Apply selected theme
st.markdown(themes[st.session_state.theme], unsafe_allow_html=True)

# Title and Layout with Toggle
col_title, col_toggle = st.columns([8, 1])
with col_title:
    st.title("Marketing Campaign Performance Analytics")
with col_toggle:
    # Button to toggle theme
    current_theme = st.session_state.theme
    btn_label = "🌞 Light" if current_theme == 'dark' else "🌑 Dark"
    if st.button(btn_label):
        new_theme = 'light' if current_theme == 'dark' else 'dark'
        st.session_state.theme = new_theme
        st.rerun()

st.markdown("### Analyzing the impact of email marketing strategies on conversion and spend.")
st.markdown("---")

# 1. Data Loading (Cached)
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    return df

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    uploaded_file = st.file_uploader("Upload Dataset (CSV)", type="csv")
    st.markdown("---")
    st.markdown("**About this Dashboard**")
    st.info("""
    This dashboard analyzes a digital marketing campaign's performance.
    
    **Key Metrics:**
    - Visit Rate
    - Conversion Rate
    - Average Spend
    
    **Segments Analyzed:**
    - Apparel Email
    - Footwear Email
    - Control Group (No Email)
    """)

# Load Data
default_file = "digital_marketing_dataset.csv"
if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.sidebar.success("Custom dataset loaded")
else:
    try:
        df = load_data(default_file)
        st.sidebar.success("Default dataset loaded")
    except FileNotFoundError:
        st.error(f"Default file '{default_file}' not found. Please upload a CSV file.")
        st.stop()

# --- PRE-CALCULATIONS ---
metrics = df.groupby("campaign_segment").agg(
    user_count=("campaign_segment", "count"),
    visit_rate=("visit", "mean"),
    conversion_count=("conversion", "sum"),
    conversion_rate=("conversion", "mean"),
    avg_spend=("spend", "mean")
).reset_index()

# Find winning campaign based on conversion
winner = metrics.loc[metrics['conversion_rate'].idxmax()]

# --- TABS LAYOUT ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Executive Summary", 
    "Data Overview", 
    "Campaign Performance", 
    "Statistical Tests", 
    "Segmentation Deep Dive",
    "Spend Profile"
])

# --- TAB 1: EXECUTIVE SUMMARY ---
with tab1:
    st.header("Executive Summary")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric(label="Total Users Targeted", value=f"{df.shape[0]:,}")
    with col_b:
        st.metric(label="Overall Conversion Rate", value=f"{df['conversion'].mean():.2%}")
    with col_c:
        st.metric(label="Avg Overall Spend", value=f"${df['spend'].mean():.2f}")

    st.markdown("Winning Strategy")
    st.success(f"**{winner['campaign_segment']}** is the top performing campaign with a conversion rate of **{winner['conversion_rate']:.2%}**.")
    
    st.markdown("""
    #### Key Insights:
    - **Apparel Email** drove the highest website visits and actual purchases.
    - **Significance**: The performance gap between Apparel Email and the Control Group is statistically significant (confirmed by Chi-Square tests).
    - **Recommendation**: Prioritize the Apparel Email strategy while investigating why Footwear underperformed relative to Apparel but still beat the baseline.
    """)

# --- TAB 2: DATA OVERVIEW ---
with tab2:
    st.header("Dataset Overview")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Dataset Statistics")
        st.write(df.describe())
        st.markdown("#### Missing Values")
        st.write(df.isnull().sum())
    
    with col2:
        st.markdown("#### Sample Data")
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")

# --- TAB 3: CAMPAIGN PERFORMANCE ---
with tab3:
    st.header("Campaign Performance Metrics")
    st.markdown("Comparative analysis of Visit Rates, Conversion Rates, and Average Spend across groups.")

    # Main Metrics Table
    st.subheader("Summary Table")
    st.dataframe(metrics.style.format({
        "visit_rate": "{:.2%}",
        "conversion_rate": "{:.2%}",
        "avg_spend": "${:.2f}"
    }), use_container_width=True)

    # Visualizations
    st.subheader("Visual Comparisons")
    
    # Theme-aware styling
    text_color = "#fafafa" if st.session_state.theme == "dark" else "#262730"
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor('none')

    sns.barplot(data=metrics, x="campaign_segment", y="visit_rate", ax=axes[0], palette="viridis")
    axes[0].set_title("Visit Rate", fontsize=14, color=text_color)
    axes[0].set_ylabel("Rate", color=text_color)
    axes[0].set_xlabel("Campaign Segment", color=text_color)
    axes[0].tick_params(colors=text_color)
    axes[0].grid(axis='y', linestyle='--', alpha=0.5)
    axes[0].set_facecolor('none')
    for spine in axes[0].spines.values():
        spine.set_edgecolor(text_color)

    sns.barplot(data=metrics, x="campaign_segment", y="conversion_rate", ax=axes[1], palette="coolwarm")
    axes[1].set_title("Conversion Rate", fontsize=14, color=text_color)
    axes[1].set_ylabel("Rate", color=text_color)
    axes[1].set_xlabel("Campaign Segment", color=text_color)
    axes[1].tick_params(colors=text_color)
    axes[1].grid(axis='y', linestyle='--', alpha=0.5)
    axes[1].set_facecolor('none')
    for spine in axes[1].spines.values():
        spine.set_edgecolor(text_color)

    sns.barplot(data=metrics, x="campaign_segment", y="avg_spend", ax=axes[2], palette="magma")
    axes[2].set_title("Average Spend ($)", fontsize=14, color=text_color)
    axes[2].set_ylabel("Dollars", color=text_color)
    axes[2].set_xlabel("Campaign Segment", color=text_color)
    axes[2].tick_params(colors=text_color)
    axes[2].grid(axis='y', linestyle='--', alpha=0.5)
    axes[2].set_facecolor('none')
    for spine in axes[2].spines.values():
        spine.set_edgecolor(text_color)

    st.pyplot(fig)
    st.caption("Bar charts showing key performance indicators by campaign segment.")

# --- TAB 4: STATISTICAL SIGNIFICANCE ---
with tab4:
    st.header("Statistical Significance Testing")
    st.markdown("""
    We use **Chi-Square Tests** to determine if the differences in visit and conversion rates are statistically significant, 
    and **T-Tests** for spending differences.
    
    - **Null Hypothesis (H0)**: There is no difference between the groups.
    - **P-Value < 0.05**: We reject H0 → The difference is **Significant**.
    """)

    # --- Calculations ---
    footwear = df[df["campaign_segment"] == "Footwear E-Mail"]
    apparel = df[df["campaign_segment"] == "Apparel E-Mail"]
    no_email = df[df["campaign_segment"] == "No E-Mail"]

    def run_chi2(group1, group2, metric="visit"):
        contingency = [
            [group1[metric].sum(), group1.shape[0] - group1[metric].sum()],
            [group2[metric].sum(), group2.shape[0] - group2[metric].sum()]
        ]
        stat, p, _, _ = chi2_contingency(contingency)
        return p

    comparisons = [
        ("Apparel", "Footwear", apparel, footwear),
        ("Apparel", "No Email", apparel, no_email),
        ("Footwear", "No Email", footwear, no_email)
    ]
    
    results = []
    for label1, label2, g1, g2 in comparisons:
        p_visit = run_chi2(g1, g2, "visit")
        p_conv = run_chi2(g1, g2, "conversion")
        t_stat, p_spend = ttest_ind(g1["spend"], g2["spend"], nan_policy='omit')
        
        results.append({
            "Comparison": f"{label1} vs {label2}",
            "Visit Rate P-Value": p_visit,
            "Conversion Rate P-Value": p_conv,
            "Spend P-Value": p_spend
        })
    
    results_df = pd.DataFrame(results)

    def highlight_significant(val):
        theme = st.session_state.get('theme', 'light')
        if isinstance(val, float):
            if theme == 'dark':
                # Dark Mode: Dark Green/Red background, White text
                color = '#1b4d3e' if val < 0.05 else '#4d1b1b' 
                return f'background-color: {color}; color: #ffffff'
            else:
                # Light Mode: Light Green/Red background, Dark text
                color = '#d4edda' if val < 0.05 else '#f8d7da'
                return f'background-color: {color}; color: #000000'
        return ''

    st.subheader("Test Results")
    st.dataframe(
        results_df.style
        .applymap(highlight_significant, subset=["Visit Rate P-Value", "Conversion Rate P-Value", "Spend P-Value"])
        .format("{:.4f}", subset=["Visit Rate P-Value", "Conversion Rate P-Value", "Spend P-Value"]),
        use_container_width=True
    )
    
    st.info("**Interpretation**: Green cells (p < 0.05) indicate that the marketing campaign had a real, non-random impact compared to the other group.")

# --- TAB 5: SEGMENTATION ---
with tab5:
    st.header("Segmentation Analysis")
    st.markdown("Analyze how different customer groups reacted to the campaigns.")

    col1, col2 = st.columns([1, 3])
    with col1:
        segment_col = st.selectbox("Select Segment Attribute", 
                                   ["acquired_in_last_year", "address_category", "history_footwear", "history_apparel"],
                                   format_func=lambda x: x.replace("_", " ").title())
        
        st.markdown("**Attribute Description:**")
        if segment_col == "acquired_in_last_year":
            st.write("0: Existing Customer\n1: New Customer")
        elif segment_col == "history_footwear":
            st.write("0: Never bought footwear\n1: Bought footwear before")

    with col2:
        segment_metrics = df.groupby(["campaign_segment", segment_col]).agg(
            conversion_rate=("conversion", "mean"),
            avg_spend=("spend", "mean")
        ).reset_index()

        # Theme-aware styling
        text_color = "#fafafa" if st.session_state.theme == "dark" else "#262730"

        fig2, ax2 = plt.subplots(1, 2, figsize=(14, 5))
        fig2.patch.set_facecolor('none')
        
        sns.barplot(data=segment_metrics, x=segment_col, y="conversion_rate", hue="campaign_segment", ax=ax2[0], palette="cividis")
        ax2[0].set_title(f"Conversion Rate by {segment_col.replace('_', ' ').title()}", color=text_color)
        ax2[0].set_xlabel(segment_col.replace('_', ' ').title(), color=text_color)
        ax2[0].set_ylabel("Conversion Rate", color=text_color)
        ax2[0].tick_params(colors=text_color)
        ax2[0].set_facecolor('none')
        for spine in ax2[0].spines.values():
            spine.set_edgecolor(text_color)
        # Update legend text color
        if ax2[0].legend_:
            plt.setp(ax2[0].legend_.get_texts(), color=text_color)
        
        sns.barplot(data=segment_metrics, x=segment_col, y="avg_spend", hue="campaign_segment", ax=ax2[1], palette="magma")
        ax2[1].set_title(f"Avg Spend by {segment_col.replace('_', ' ').title()}", color=text_color)
        ax2[1].set_xlabel(segment_col.replace('_', ' ').title(), color=text_color)
        ax2[1].set_ylabel("Average Spend", color=text_color)
        ax2[1].tick_params(colors=text_color)
        ax2[1].set_facecolor('none')
        for spine in ax2[1].spines.values():
            spine.set_edgecolor(text_color)
        if ax2[1].legend_:
            plt.setp(ax2[1].legend_.get_texts(), color=text_color)
        
        st.pyplot(fig2)

# --- TAB 6: CUSTOMER PROFILING ---
with tab6:
    st.header("Customer Spend Profiling")
    st.markdown("Breakdown of performance based on historical customer value (High/Medium/Low spenders).")

    try:
        # Dynamic binning based on quartiles/distribution
        df['spend_group'] = pd.qcut(df['history_spend'], q=3, labels=['Low Value', 'Medium Value', 'High Value'])
        
        spend_metrics = df.groupby(['campaign_segment', 'spend_group']).agg(
            conversion_rate=('conversion', 'mean')
        ).reset_index()

        # Theme-aware styling
        text_color = "#fafafa" if st.session_state.theme == "dark" else "#262730"

        fig3, ax3 = plt.subplots(figsize=(12, 6))
        fig3.patch.set_facecolor('none')
        sns.barplot(data=spend_metrics, x='spend_group', y='conversion_rate', hue='campaign_segment', palette='coolwarm', ax=ax3)
        ax3.set_title("Conversion Rate by Historical Spend Level", fontsize=15, color=text_color)
        ax3.set_ylabel("Conversion Rate", color=text_color)
        ax3.set_xlabel("Customer Value Tier", color=text_color)
        ax3.tick_params(colors=text_color)
        ax3.set_facecolor('none')
        for spine in ax3.spines.values():
            spine.set_edgecolor(text_color)
        if ax3.legend_:
            plt.setp(ax3.legend_.get_texts(), color=text_color)
        
        st.pyplot(fig3)
        
        st.markdown("""
        **Insight**: This chart reveals if we are effectively upselling high-value customers or activating low-value ones.
        """)

    except Exception as e:
        st.error(f"Error in profiling analysis: {e}")
