import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Great Hele Flow & Pressure - Wales & West Utilities",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------
# BRAND COLOURS (HYDROSTAR + DARK THEME)
# ------------------------------------------------------
PRIMARY_COLOUR = "#a7d730"  # HydroStar primary green
SECONDARY_COLOUR = "#499823"  # HydroStar secondary green
DARK_GREY = "#30343c"
LIGHT_GREY = "#8c919a"
BACKGROUND = "#0e1117"
PANEL_BG = "#1b222b"
TEXT_COL = "#f2f4f7"
SUBTEXT_COL = LIGHT_GREY
ACCENT_COLOUR = "#86d5f8"


COLOUR_MAP = {
    "Flow (Scmh)": PRIMARY_COLOUR,
    "Pressure (Bar)": ACCENT_COLOUR,
}


# ------------------------------------------------------
# GLOBAL CSS TO FORCE DARK UI
# ------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind:wght@300;400;500;600;700&display=swap');

    :root {{
        --hs-primary: {PRIMARY_COLOUR};
        --hs-secondary: {SECONDARY_COLOUR};
        --hs-bg: {BACKGROUND};
        --hs-card: {PANEL_BG};
        --hs-text: {TEXT_COL};
        --hs-subtext: {SUBTEXT_COL};
        --hs-sidebar: {DARK_GREY};
    }}

    html, body, [class*="css"] {{
        font-family: 'Hind', sans-serif;
    }}

    .stApp {{
        background:
            radial-gradient(circle at top right, rgba(167, 215, 48, 0.11) 0%, rgba(14, 17, 23, 0) 35%),
            radial-gradient(circle at bottom left, rgba(134, 213, 248, 0.08) 0%, rgba(14, 17, 23, 0) 40%),
            var(--hs-bg);
        color: var(--hs-text);
    }}
    .block-container {{
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        color: var(--hs-text);
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: var(--hs-text) !important;
        font-weight: 700;
        letter-spacing: 0.1px;
    }}
    p, span, label {{
        color: var(--hs-text) !important;
    }}
    .stCaption, .stMarkdown small {{
        color: var(--hs-subtext) !important;
    }}
    section[data-testid="stSidebar"] > div {{
        background-color: var(--hs-sidebar);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] label {{
        color: #ffffff !important;
    }}
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {{
        background-color: rgba(255, 255, 255, 0.06);
        border-color: rgba(255, 255, 255, 0.16);
    }}
    .stDateInput > div > div,
    .stMultiSelect > div > div,
    .stSelectbox > div > div {{
        background-color: rgba(255, 255, 255, 0.06);
    }}
    .stSlider > div > div > div {{
        background-color: rgba(167, 215, 48, 0.18);
    }}
    .stSlider [data-testid="stTickBar"] > div {{
        background-color: rgba(167, 215, 48, 0.40);
    }}
    .st-bx, .stTextInput, .stNumberInput, .stDateInput, .stSelectbox, .stMultiSelect {{
        color: var(--hs-text) !important;
    }}
    .stButton > button {{
        background-color: var(--hs-primary);
        color: #1d2430;
        font-weight: 700;
        border: none;
        border-radius: 8px;
    }}
    .stButton > button:hover {{
        background-color: var(--hs-secondary);
        color: #ffffff;
    }}
    div[data-testid="metric-container"] {{
        background: linear-gradient(180deg, rgba(27, 34, 43, 0.96) 0%, rgba(22, 29, 37, 0.96) 100%);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-left: 5px solid var(--hs-primary);
        border-radius: 12px;
        padding: 0.85rem 1rem;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.24);
    }}
    div[data-testid="metric-container"] label {{
        color: var(--hs-subtext) !important;
        font-size: 0.86rem !important;
        letter-spacing: 0.35px;
        text-transform: uppercase;
    }}
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
        color: var(--hs-text) !important;
        font-weight: 700;
        line-height: 1.1;
    }}
    div[data-testid="stDataFrame"] {{
        background-color: rgba(27, 34, 43, 0.96);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 0.2rem;
    }}
    .stPlotlyChart {{
        background-color: rgba(27, 34, 43, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 0.55rem 1.45rem 0.25rem 0.55rem;
        margin-bottom: 1.1rem;
        box-sizing: border-box;
    }}
    .hero-banner {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1.2rem;
        padding: 1.1rem 1.25rem;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        background: linear-gradient(
            90deg,
            rgba(12, 16, 24, 0.90) 0%,
            rgba(18, 30, 22, 0.88) 72%,
            rgba(29, 52, 33, 0.78) 100%
        );
        margin-bottom: 1.4rem;
    }}
    .hero-copy {{
        max-width: 68%;
    }}
    .hero-title {{
        margin: 0;
        color: var(--hs-text);
        font-size: clamp(2.0rem, 2.8vw, 2.8rem);
        line-height: 1.1;
        font-weight: 700;
    }}
    .hero-subtitle {{
        margin: 0.45rem 0 0 0;
        color: var(--hs-subtext);
        font-size: 1rem;
    }}
    .hero-logos {{
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 1rem;
        flex-wrap: nowrap;
    }}
    .hero-logos img {{
        height: 112px;
        width: auto;
        object-fit: contain;
        filter: drop-shadow(0 6px 14px rgba(0, 0, 0, 0.35));
    }}
    @media (max-width: 1080px) {{
        .hero-banner {{
            flex-direction: column;
            align-items: flex-start;
        }}
        .hero-copy {{
            max-width: 100%;
        }}
        .hero-logos {{
            justify-content: flex-start;
        }}
        .hero-logos img {{
            height: 88px;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ======================================================
# DATA LOADING
# ======================================================
@st.cache_data
def load_data():
    df_local = pd.read_parquet("great_hele_combined.parquet")
    if not isinstance(df_local.index, pd.DatetimeIndex):
        for col in ["Time", "Datetime", "timestamp"]:
            if col in df_local.columns:
                df_local[col] = pd.to_datetime(df_local[col], utc=True)
                df_local = df_local.set_index(col)
                break
        else:
            df_local.index = pd.to_datetime(df_local.index, utc=True)
    df_local = df_local.sort_index()
    return df_local


df = load_data()


def encode_logo_to_base64(path: Path):
    if not path.exists():
        return ""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


# ======================================================
# SIDEBAR FILTERS
# ======================================================
min_date = df.index.min().date()
max_date = df.index.max().date()

st.sidebar.caption("Drag both handles to set the date window")
start_date, end_date = st.sidebar.slider(
    "Date range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD",
)

mask = (df.index.date >= start_date) & (df.index.date <= end_date)
df = df.loc[mask]

all_cols = list(df.columns)
selected_cols = st.sidebar.multiselect(
    "Select series",
    options=all_cols,
    default=all_cols,
)

if not selected_cols:
    st.sidebar.error("Please select at least one series.")
    st.stop()

df = df[selected_cols]

st.sidebar.markdown(
    f"<p style='color:{SUBTEXT_COL}; font-size:0.9rem;'>Records (filtered): "
    f"<span style='color:{TEXT_COL}; font-weight:600;'>{len(df):,}</span><br>"
    f"{df.index.min().date()} -> {df.index.max().date()}</p>",
    unsafe_allow_html=True,
)


# ======================================================
# HEADER
# ======================================================
hs_logo_b64 = encode_logo_to_base64(Path("logo.png"))
wwu_logo_b64 = encode_logo_to_base64(Path("wwu.png"))

logo_html_parts = []
if hs_logo_b64:
    logo_html_parts.append(f'<img src="data:image/png;base64,{hs_logo_b64}" alt="HydroStar logo">')
if wwu_logo_b64:
    logo_html_parts.append(
        f'<img src="data:image/png;base64,{wwu_logo_b64}" alt="Wales and West Utilities logo">'
    )

st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-copy">
            <h1 class="hero-title">Great Hele Flow &amp; Pressure Explorer</h1>
            <p class="hero-subtitle">HydroStar x Wales &amp; West Utilities</p>
        </div>
        <div class="hero-logos">
            {''.join(logo_html_parts)}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ======================================================
# SUMMARY STATISTICS
# ======================================================
st.markdown("## Summary statistics")

start_ts = df.index.min().strftime("%Y-%m-%d %H:%M")
end_ts = df.index.max().strftime("%Y-%m-%d %H:%M")

st.caption("Current filter KPIs")
metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.metric("Start date", start_ts)
with metric_col2:
    st.metric("End date", end_ts)
with metric_col3:
    st.metric("Total records (filtered)", f"{len(df):,}")

st.markdown("#### Descriptive statistics")
desc = df.describe().T
st.dataframe(
    desc.style.format(
        {
            "count": "{:,.0f}",
            "mean": "{:,.4f}",
            "std": "{:,.4f}",
            "min": "{:,.4f}",
            "25%": "{:,.4f}",
            "50%": "{:,.4f}",
            "75%": "{:,.4f}",
            "max": "{:,.4f}",
        }
    ),
    use_container_width=True,
    height=min(350, 80 + 28 * len(desc)),
)


# ======================================================
# HELPER FUNCTIONS
# ======================================================
def apply_dark_layout(fig, title):
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, color=TEXT_COL, family="Hind, sans-serif")),
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COL, family="Hind, sans-serif"),
        colorway=[PRIMARY_COLOUR, SECONDARY_COLOUR, ACCENT_COLOUR, "#f59e0b", "#e11d48"],
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=66, r=72, t=78, b=62),
        hovermode="x unified",
    )
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        linecolor="rgba(255,255,255,0.18)",
        automargin=True,
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        linecolor="rgba(255,255,255,0.18)",
        automargin=True,
    )
    return fig


def split_series_columns(columns):
    flow_cols = [col for col in columns if "flow" in col.lower()]
    pressure_cols = [col for col in columns if "pressure" in col.lower()]
    other_cols = [col for col in columns if col not in flow_cols + pressure_cols]
    return flow_cols, pressure_cols, other_cols


def build_stacked_line_chart(
    plot_df,
    title,
    xaxis_title,
    flow_unit="Scmh",
    mode="lines",
    marker_size=7,
):
    flow_cols, pressure_cols, other_cols = split_series_columns(plot_df.columns)
    has_two_rows = bool(flow_cols and pressure_cols)
    nrows = 2 if has_two_rows else 1
    flow_scale = 1000.0 if flow_unit == "kScmh" else 1.0

    fig = make_subplots(rows=nrows, cols=1, shared_xaxes=True, vertical_spacing=0.08)

    for col in plot_df.columns:
        base_col = COLOUR_MAP.get(col, "#6366f1")
        line_style = dict(color=base_col, width=2.4)
        if col in other_cols:
            line_style["dash"] = "dot"

        target_row = 1
        if has_two_rows and col in pressure_cols:
            target_row = 2

        y_vals = plot_df[col]
        trace_name = col
        if col in flow_cols:
            y_vals = y_vals / flow_scale
            trace_name = col.replace("(Scmh)", f"({flow_unit})")

        trace_kwargs = dict(
            x=plot_df.index,
            y=y_vals,
            mode=mode,
            name=trace_name,
            line=line_style,
        )
        if "markers" in mode:
            trace_kwargs["marker"] = dict(size=marker_size)

        fig.add_trace(go.Scatter(**trace_kwargs), row=target_row, col=1)

    fig.update_layout(xaxis_title=xaxis_title)
    if has_two_rows:
        fig.update_yaxes(title_text=f"Flow ({flow_unit})", row=1, col=1)
        fig.update_yaxes(title_text="Pressure (Bar)", row=2, col=1)
    else:
        single_axis_label = "Value"
        if flow_cols:
            single_axis_label = f"Flow ({flow_unit})"
        elif pressure_cols:
            single_axis_label = "Pressure (Bar)"
        fig.update_yaxes(title_text=single_axis_label, row=1, col=1)

    return apply_dark_layout(fig, title)


# ======================================================
# 1. Trend over time
# ======================================================
st.markdown("## Trend over time")

control_col1, control_col2, control_col3 = st.columns(3)
with control_col1:
    agg_choice = st.selectbox(
        "Time resolution",
        options=["30 minutes", "Hourly", "Daily", "Weekly"],
        index=2,
    )
with control_col2:
    trend_view = st.selectbox(
        "Comparison view",
        options=["Separated (actual units)", "Normalized (0-1)"],
        index=0,
    )
with control_col3:
    smooth_trend = st.checkbox("Smooth trend", value=True)

flow_unit = st.radio(
    "Flow display unit",
    options=["Scmh", "kScmh"],
    horizontal=True,
    index=1,
)

freq_map = {
    "30 minutes": "30min",
    "Hourly": "H",
    "Daily": "D",
    "Weekly": "W",
}
freq = freq_map[agg_choice]

resampled = df.resample(freq).mean()
rolling_window_map = {
    "30 minutes": 48,
    "Hourly": 24,
    "Daily": 7,
    "Weekly": 4,
}
plot_data = resampled.copy()
if smooth_trend:
    plot_data = plot_data.rolling(window=rolling_window_map[agg_choice], min_periods=1).median()

flow_cols, pressure_cols, other_cols = split_series_columns(plot_data.columns)

if trend_view == "Separated (actual units)":
    flow_scale = 1000.0 if flow_unit == "kScmh" else 1.0
    has_two_rows = bool(flow_cols and pressure_cols)
    nrows = 2 if has_two_rows else 1
    fig_trend = make_subplots(rows=nrows, cols=1, shared_xaxes=True, vertical_spacing=0.06)

    for col in plot_data.columns:
        base_col = COLOUR_MAP.get(col, "#6366f1")
        line_style = dict(color=base_col, width=2.2)
        if col in other_cols:
            line_style["dash"] = "dot"

        target_row = 1
        if has_two_rows and col in pressure_cols:
            target_row = 2

        y_vals = plot_data[col]
        trace_name = f"{col} ({agg_choice} average)"
        if col in flow_cols:
            y_vals = y_vals / flow_scale
            trace_name = f"{col.replace('(Scmh)', f'({flow_unit})')} ({agg_choice} average)"

        fig_trend.add_trace(
            go.Scatter(
                x=plot_data.index,
                y=y_vals,
                mode="lines",
                name=trace_name,
                line=line_style,
            ),
            row=target_row,
            col=1,
        )

    fig_trend.update_layout(xaxis_title="Time")
    if has_two_rows:
        top_axis_label = f"Flow ({flow_unit})" if flow_cols else "Value"
        fig_trend.update_yaxes(title_text=top_axis_label, row=1, col=1)
        fig_trend.update_yaxes(title_text="Pressure (Bar)", row=2, col=1)
    else:
        single_axis_label = f"Flow ({flow_unit})" if flow_cols else "Value"
        if pressure_cols and not flow_cols:
            single_axis_label = "Pressure (Bar)"
        fig_trend.update_yaxes(title_text=single_axis_label, row=1, col=1)

    fig_trend = apply_dark_layout(fig_trend, f"Great Hele - {agg_choice.lower()} averages")
else:
    # Normalize each selected series independently to [0, 1] for shape comparison.
    span = (plot_data.max() - plot_data.min()).replace(0, pd.NA)
    normalized = ((plot_data - plot_data.min()) / span).fillna(0.0)
    fig_trend = go.Figure()

    for col in normalized.columns:
        base_col = COLOUR_MAP.get(col, "#6366f1")
        fig_trend.add_trace(
            go.Scatter(
                x=normalized.index,
                y=normalized[col],
                mode="lines",
                name=f"{col} ({agg_choice} average)",
                line=dict(color=base_col, width=2.2),
            )
        )

    fig_trend.update_layout(
        xaxis_title="Time",
        yaxis_title="Normalized value (0-1)",
    )
    fig_trend = apply_dark_layout(
        fig_trend,
        f"Great Hele - {agg_choice.lower()} averages (normalized)",
    )
    st.caption("Each selected series is scaled independently to 0-1 for shape comparison.")

if smooth_trend:
    st.caption(f"Smoothed with rolling median ({rolling_window_map[agg_choice]} points).")

st.plotly_chart(fig_trend, use_container_width=True)


# ======================================================
# 2. DAILY AVERAGES
# ======================================================
st.markdown("## Daily averages")

daily = df.resample("D").mean()
fig_daily = build_stacked_line_chart(
    daily,
    "Great Hele - Daily Averages",
    "Year",
    flow_unit=flow_unit,
    mode="lines",
)
st.plotly_chart(fig_daily, use_container_width=True)


# ======================================================
# 3. MONTHLY SEASONALITY
# ======================================================
st.markdown("## Monthly averages (multi-year seasonality)")

monthly = df.resample("M").mean()
fig_monthly = build_stacked_line_chart(
    monthly,
    "Monthly Averages (Seasonality)",
    "Year",
    flow_unit=flow_unit,
    mode="lines",
)
st.plotly_chart(fig_monthly, use_container_width=True)


# ======================================================
# 4. AVERAGE BY CALENDAR MONTH
# ======================================================
st.markdown("## Average by calendar month (2019-2025)")

monthly_pattern = df.groupby(df.index.month).mean()
monthly_pattern.index = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
fig_mpat = build_stacked_line_chart(
    monthly_pattern,
    "Average by Month (2019-2025)",
    "Month",
    flow_unit=flow_unit,
    mode="lines+markers",
    marker_size=8,
)
st.plotly_chart(fig_mpat, use_container_width=True)


# ======================================================
# 5. AVERAGE BY HOUR OF DAY
# ======================================================
st.markdown("## Average by hour of day")

hourly_pattern = df.groupby(df.index.hour).mean()
fig_hpat = build_stacked_line_chart(
    hourly_pattern,
    "Average by Hour of Day",
    "Hour",
    flow_unit=flow_unit,
    mode="lines+markers",
    marker_size=7,
)
st.plotly_chart(fig_hpat, use_container_width=True)


# ======================================================
# 6. YEARLY DISTRIBUTION (BOXPLOTS)
# ======================================================
st.markdown("## Distribution of daily values by year")

df_year = df.resample("D").mean()
df_year["Year"] = df_year.index.year
year_value_cols = [col for col in df_year.columns if col != "Year"]
flow_year_cols, pressure_year_cols, other_year_cols = split_series_columns(year_value_cols)

first_group_cols = flow_year_cols + other_year_cols
if first_group_cols:
    fig_box_flow = go.Figure()
    flow_scale = 1000.0 if flow_unit == "kScmh" else 1.0
    for col in first_group_cols:
        plot_name = col.replace("(Scmh)", f"({flow_unit})") if col in flow_year_cols else col
        y_vals = df_year[col] / flow_scale if col in flow_year_cols else df_year[col]
        fig_box_flow.add_trace(
            go.Box(
                x=df_year["Year"],
                y=y_vals,
                name=plot_name,
                marker_color=COLOUR_MAP.get(col, "#6366f1"),
                boxmean=True,
                boxpoints=False,
            )
        )
    yaxis_title = f"Flow ({flow_unit})" if flow_year_cols else "Value"
    fig_box_flow.update_layout(xaxis_title="Year", yaxis_title=yaxis_title)
    box_title = "Flow Distribution by Year" if flow_year_cols else "Distribution by Year"
    fig_box_flow = apply_dark_layout(fig_box_flow, box_title)
    st.plotly_chart(fig_box_flow, use_container_width=True)

if pressure_year_cols:
    fig_box_pressure = go.Figure()
    for col in pressure_year_cols:
        fig_box_pressure.add_trace(
            go.Box(
                x=df_year["Year"],
                y=df_year[col],
                name=col,
                marker_color=COLOUR_MAP.get(col, "#6366f1"),
                boxmean=True,
                boxpoints=False,
            )
        )
    fig_box_pressure.update_layout(xaxis_title="Year", yaxis_title="Pressure (Bar)")
    fig_box_pressure = apply_dark_layout(fig_box_pressure, "Pressure Distribution by Year")
    st.plotly_chart(fig_box_pressure, use_container_width=True)

if not first_group_cols and not pressure_year_cols:
    fig_box = go.Figure()
    for col in year_value_cols:
        fig_box.add_trace(
            go.Box(
                x=df_year["Year"],
                y=df_year[col],
                name=col,
                marker_color=COLOUR_MAP.get(col, "#6366f1"),
                boxmean=True,
                boxpoints=False,
            )
        )
    fig_box.update_layout(xaxis_title="Year", yaxis_title="Value")
    fig_box = apply_dark_layout(fig_box, "Distribution of Daily Values by Year")
    st.plotly_chart(fig_box, use_container_width=True)


# ======================================================
# 7. CORRELATION HEATMAP
# ======================================================
st.markdown("## Correlation between series")

corr = df.corr()
fig_corr = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale=[
        [0.0, ACCENT_COLOUR],
        [0.5, PANEL_BG],
        [1.0, PRIMARY_COLOUR],
    ],
    aspect="auto",
)
fig_corr.update_layout(xaxis_title="", yaxis_title="")
fig_corr = apply_dark_layout(fig_corr, "Correlation Between Flow and Pressure")
st.plotly_chart(fig_corr, use_container_width=True)


# ======================================================
# RAW DATA
# ======================================================
with st.expander("Show raw data (first 500 rows)"):
    st.dataframe(df.head(500), use_container_width=True)

