import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

st.set_page_config(
    page_title="Dashboard Inventaris Medis",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #cbd5e1;
        font-size: 0.85rem;
        font-weight: 500;
    }
    [data-testid="stMetricValue"] {
       
        font-size: 1.8rem;
        font-weight: 700;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.8rem;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #cbd5e1;
        border-radius: 10px;
    }
    .block-container {
        padding-top: 1.5rem;
    }
    h1 {
        color: #0f172a;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    h2, h3 {
        color: #1e293b;
        font-weight: 600;
    }
    h4 {
        color: #1e293b;
        font-weight: 600;
    }
    p, span, label, .stMarkdown {
        color: #334155;
    }
    .stSidebar h2, .stSidebar h3 {
        color: #1e293b;
    }
</style>
""",
    unsafe_allow_html=True,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COLORS = {
    "primary": "#6366f1",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "muted": "#64748b",
}

COLOR_SEQUENCE = [
    "#6366f1",
    "#22c55e",
    "#f59e0b",
    "#ef4444",
    "#3b82f6",
    "#a855f7",
    "#ec4899",
    "#14b8a6",
    "#f97316",
    "#8b5cf6",
    "#06b6d4",
    "#84cc16",
    "#e11d48",
    "#0ea5e9",
    "#d946ef",
]


@st.cache_data
def load_data():
    data = pd.read_csv(os.path.join(BASE_DIR, "dataset", "data.csv"))
    data["Nama_Alat"] = data["Nama_Alat"].str.strip()
    return data


try:
    df = load_data()
except FileNotFoundError:
    st.error("File data tidak ditemukan di path dataset/data.csv")
    st.stop()


def compute_compliance_score(dataframe):
    if len(dataframe) == 0:
        return 0.0
    total_checks = len(dataframe) * 3
    compliant = (
        (dataframe["Stiker_Label"] == "Ada").sum()
        + (dataframe["Lembar_SOP"] == "Ada").sum()
        + (dataframe["Stiker_Kalibrasi"] == "Ada").sum()
    )
    return round((compliant / total_checks) * 100, 1)


def compute_risk_level(row):
    issues = sum(
        [
            row["Stiker_Label"] == "Tidak",
            row["Lembar_SOP"] == "Tidak",
            row["Stiker_Kalibrasi"] == "Tidak",
            row["Kondisi"] != "Baik",
        ]
    )
    if issues >= 3:
        return "Kritis"
    if issues == 2:
        return "Tinggi"
    if issues == 1:
        return "Sedang"
    return "Rendah"


st.sidebar.markdown("## Filter Dashboard")
st.sidebar.markdown("---")

st.sidebar.markdown("### Departemen / Ruangan")
unique_rooms = sorted(df["Ruangan"].unique())
select_all_rooms = st.sidebar.checkbox("Pilih Semua Ruangan", value=True)
if select_all_rooms:
    selected_rooms = unique_rooms
else:
    selected_rooms = st.sidebar.multiselect(
        "Pilih Ruangan", options=unique_rooms, default=unique_rooms[:3]
    )

st.sidebar.markdown("### Jenis Alat")
unique_equipment = sorted(df["Nama_Alat"].unique())
select_all_equipment = st.sidebar.checkbox("Pilih Semua Jenis Alat", value=True)
if select_all_equipment:
    selected_equipment = unique_equipment
else:
    selected_equipment = st.sidebar.multiselect(
        "Pilih Jenis Alat", options=unique_equipment, default=unique_equipment[:5]
    )

st.sidebar.markdown("### Kondisi Alat")
unique_conditions = sorted(df["Kondisi"].unique())
selected_conditions = st.sidebar.multiselect(
    "Pilih Kondisi", options=unique_conditions, default=unique_conditions
)

st.sidebar.markdown("### Status Kepatuhan")
compliance_filter = st.sidebar.radio(
    "Filter Kepatuhan",
    options=["Semua", "Lengkap (SOP + Label + Kalibrasi)", "Tidak Lengkap"],
    index=0,
)

filtered_df = df[
    (df["Ruangan"].isin(selected_rooms))
    & (df["Nama_Alat"].isin(selected_equipment))
    & (df["Kondisi"].isin(selected_conditions))
].copy()

if compliance_filter == "Lengkap (SOP + Label + Kalibrasi)":
    filtered_df = filtered_df[
        (filtered_df["Stiker_Label"] == "Ada")
        & (filtered_df["Lembar_SOP"] == "Ada")
        & (filtered_df["Stiker_Kalibrasi"] == "Ada")
    ]
elif compliance_filter == "Tidak Lengkap":
    filtered_df = filtered_df[
        (filtered_df["Stiker_Label"] == "Tidak")
        | (filtered_df["Lembar_SOP"] == "Tidak")
        | (filtered_df["Stiker_Kalibrasi"] == "Tidak")
    ]

filtered_df["Tingkat_Risiko"] = filtered_df.apply(compute_risk_level, axis=1)

st.markdown("# Dashboard Inventaris Alat Medis")
st.markdown(
    "Monitoring komprehensif inventaris, kepatuhan, dan kondisi alat medis rumah sakit."
)
st.markdown("---")

total_all = len(df)
total_filtered = len(filtered_df)
good_count = len(filtered_df[filtered_df["Kondisi"] == "Baik"])
damaged_count = len(filtered_df[filtered_df["Kondisi"] != "Baik"])
compliance_score = compute_compliance_score(filtered_df)
missing_sop = (filtered_df["Lembar_SOP"] == "Tidak").sum()
missing_label = (filtered_df["Stiker_Label"] == "Tidak").sum()
missing_calibration = (filtered_df["Stiker_Kalibrasi"] == "Tidak").sum()
risk_critical = (filtered_df["Tingkat_Risiko"] == "Kritis").sum()

good_pct = round((good_count / total_filtered * 100), 1) if total_filtered > 0 else 0
damaged_pct = (
    round((damaged_count / total_filtered * 100), 1) if total_filtered > 0 else 0
)

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Total Alat", f"{total_filtered}", delta=f"dari {total_all} total")
m2.metric("Kondisi Baik", f"{good_count}", delta=f"{good_pct}%")
m3.metric(
    "Rusak / Bermasalah",
    f"{damaged_count}",
    delta=f"{damaged_pct}%",
    delta_color="inverse",
)
m4.metric("Skor Kepatuhan", f"{compliance_score}%", delta="target 100%")
m5.metric(
    "Tanpa Kalibrasi",
    f"{missing_calibration}",
    delta=f"{missing_sop} tanpa SOP",
    delta_color="inverse",
)
m6.metric(
    "Risiko Kritis", f"{risk_critical}", delta="perlu tindakan", delta_color="inverse"
)

st.markdown("---")

if risk_critical > 0:
    st.error(
        f"**PERINGATAN KRITIS:** Terdapat **{risk_critical} alat** dengan tingkat risiko kritis "
        f"(kondisi rusak + tidak lengkap). Segera lakukan tindakan!"
    )

if compliance_score < 50:
    st.warning(
        f"**Kepatuhan Rendah:** Skor kepatuhan saat ini **{compliance_score}%**. "
        f"Target minimum adalah 80%."
    )

if damaged_count > 0:
    top_damaged_rooms = (
        filtered_df[filtered_df["Kondisi"] != "Baik"]["Ruangan"]
        .value_counts()
        .head(3)
        .to_dict()
    )
    room_summary = ", ".join([f"{r} ({c} alat)" for r, c in top_damaged_rooms.items()])
    st.info(f"**Alat Rusak Terbanyak:** {room_summary}")

st.markdown("## Analisis Distribusi Alat")
dist_col1, dist_col2 = st.columns(2)

with dist_col1:
    room_counts = filtered_df["Ruangan"].value_counts().reset_index()
    room_counts.columns = ["Ruangan", "Jumlah"]
    fig_room = px.bar(
        room_counts,
        x="Jumlah",
        y="Ruangan",
        orientation="h",
        title="Distribusi Alat per Ruangan",
        color="Jumlah",
        color_continuous_scale=["#6366f1", "#a855f7", "#ec4899"],
    )
    fig_room.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1e293b"),
        showlegend=False,
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending"),
        margin=dict(l=0, r=20, t=40, b=0),
    )
    st.plotly_chart(fig_room, use_container_width=True)

with dist_col2:
    equip_counts = filtered_df["Nama_Alat"].value_counts().head(15).reset_index()
    equip_counts.columns = ["Nama_Alat", "Jumlah"]
    fig_equip = px.bar(
        equip_counts,
        x="Nama_Alat",
        y="Jumlah",
        title="Top 15 Jenis Alat Terbanyak",
        color="Jumlah",
        color_continuous_scale=["#22c55e", "#3b82f6", "#6366f1"],
    )
    fig_equip.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1e293b"),
        showlegend=False,
        coloraxis_showscale=False,
        xaxis=dict(tickangle=-45),
        margin=dict(l=0, r=20, t=40, b=0),
    )
    st.plotly_chart(fig_equip, use_container_width=True)

st.markdown("## Kondisi dan Kepatuhan per Ruangan")
cond_col1, cond_col2 = st.columns(2)

with cond_col1:
    condition_room = (
        filtered_df.groupby(["Ruangan", "Kondisi"]).size().reset_index(name="Jumlah")
    )
    color_map = {"Baik": "#22c55e", "Rusak": "#ef4444", "Lama Steril": "#f59e0b"}
    fig_cond_room = px.bar(
        condition_room,
        x="Ruangan",
        y="Jumlah",
        color="Kondisi",
        title="Kondisi Alat per Ruangan",
        barmode="stack",
        color_discrete_map=color_map,
    )
    fig_cond_room.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1e293b"),
        xaxis=dict(tickangle=-45),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=20, t=40, b=0),
    )
    st.plotly_chart(fig_cond_room, use_container_width=True)

with cond_col2:
    condition_pie = filtered_df["Kondisi"].value_counts().reset_index()
    condition_pie.columns = ["Kondisi", "Jumlah"]
    fig_pie = px.pie(
        condition_pie,
        names="Kondisi",
        values="Jumlah",
        title="Proporsi Kondisi Alat",
        color="Kondisi",
        color_discrete_map=color_map,
        hole=0.45,
    )
    fig_pie.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1e293b"),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5
        ),
        margin=dict(l=0, r=20, t=40, b=0),
    )
    fig_pie.update_traces(
        textposition="inside",
        textinfo="percent+value",
        textfont_size=13,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("## Analisis Kepatuhan (SOP, Label, Kalibrasi)")
comp_col1, comp_col2 = st.columns(2)

with comp_col1:
    compliance_data = []
    for room in filtered_df["Ruangan"].unique():
        room_df = filtered_df[filtered_df["Ruangan"] == room]
        total = len(room_df)
        if total == 0:
            continue
        sop_rate = round((room_df["Lembar_SOP"] == "Ada").sum() / total * 100, 1)
        label_rate = round((room_df["Stiker_Label"] == "Ada").sum() / total * 100, 1)
        calib_rate = round(
            (room_df["Stiker_Kalibrasi"] == "Ada").sum() / total * 100, 1
        )
        compliance_data.append(
            {
                "Ruangan": room,
                "SOP (%)": sop_rate,
                "Label (%)": label_rate,
                "Kalibrasi (%)": calib_rate,
            }
        )

    compliance_df = pd.DataFrame(compliance_data)

    if not compliance_df.empty:
        comp_melted = compliance_df.melt(
            id_vars="Ruangan", var_name="Jenis Kepatuhan", value_name="Persentase"
        )
        fig_comp = px.bar(
            comp_melted,
            x="Ruangan",
            y="Persentase",
            color="Jenis Kepatuhan",
            title="Tingkat Kepatuhan per Ruangan",
            barmode="group",
            color_discrete_sequence=["#6366f1", "#22c55e", "#f59e0b"],
        )
        fig_comp.add_hline(
            y=80,
            line_dash="dash",
            line_color="#ef4444",
            annotation_text="Target 80%",
            annotation_position="top right",
            annotation_font_color="#ef4444",
        )
        fig_comp.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1e293b"),
            xaxis=dict(tickangle=-45),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            margin=dict(l=0, r=20, t=40, b=0),
        )
        st.plotly_chart(fig_comp, use_container_width=True)

with comp_col2:
    if not compliance_df.empty:
        categories = ["SOP (%)", "Label (%)", "Kalibrasi (%)"]
        fig_radar = go.Figure()

        top_rooms = compliance_df.head(6)
        for i, row in top_rooms.iterrows():
            values = [row["SOP (%)"], row["Label (%)"], row["Kalibrasi (%)"]]
            values.append(values[0])
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=values,
                    theta=categories + [categories[0]],
                    fill="toself",
                    name=row["Ruangan"],
                    opacity=0.6,
                )
            )

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#64748b"),
                bgcolor="rgba(0,0,0,0)",
                angularaxis=dict(color="#475569"),
            ),
            title="Radar Kepatuhan per Ruangan",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1e293b", size=11),
            legend=dict(font=dict(size=10)),
            margin=dict(l=40, r=40, t=50, b=40),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("## Peta Inventaris (Treemap)")

treemap_data = (
    filtered_df.groupby(["Ruangan", "Nama_Alat", "Kondisi"])
    .size()
    .reset_index(name="Jumlah")
)
treemap_data["Label"] = (
    treemap_data["Nama_Alat"] + " (" + treemap_data["Jumlah"].astype(str) + ")"
)

fig_tree = px.treemap(
    treemap_data,
    path=["Ruangan", "Nama_Alat"],
    values="Jumlah",
    color="Jumlah",
    title="Peta Distribusi Alat per Ruangan dan Jenis",
    color_continuous_scale=["#1e293b", "#6366f1", "#a855f7"],
)
fig_tree.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#1e293b"),
    coloraxis_showscale=False,
    margin=dict(l=0, r=0, t=40, b=0),
    height=500,
)
st.plotly_chart(fig_tree, use_container_width=True)

st.markdown("## Heatmap Kepatuhan per Ruangan")

heatmap_data = []
for room in sorted(filtered_df["Ruangan"].unique()):
    room_df = filtered_df[filtered_df["Ruangan"] == room]
    total = len(room_df)
    if total == 0:
        continue
    heatmap_data.append(
        {
            "Ruangan": room,
            "SOP": round((room_df["Lembar_SOP"] == "Ada").sum() / total * 100, 1),
            "Label": round((room_df["Stiker_Label"] == "Ada").sum() / total * 100, 1),
            "Kalibrasi": round(
                (room_df["Stiker_Kalibrasi"] == "Ada").sum() / total * 100, 1
            ),
            "Kondisi Baik": round(
                (room_df["Kondisi"] == "Baik").sum() / total * 100, 1
            ),
        }
    )

heatmap_df = pd.DataFrame(heatmap_data).set_index("Ruangan")

fig_heatmap = go.Figure(
    data=go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns.tolist(),
        y=heatmap_df.index.tolist(),
        colorscale=[
            [0, "#ef4444"],
            [0.4, "#f59e0b"],
            [0.7, "#22c55e"],
            [1, "#16a34a"],
        ],
        text=heatmap_df.values,
        texttemplate="%{text:.1f}%",
        textfont=dict(size=12, color="white"),
        hovertemplate="%{y}<br>%{x}: %{z:.1f}%<extra></extra>",
        showscale=True,
        colorbar=dict(
            title=dict(text="%", font=dict(color="#334155")),
            tickfont=dict(color="#334155"),
        ),
    )
)

fig_heatmap.update_layout(
    title="Persentase Kepatuhan & Kondisi per Ruangan",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#1e293b"),
    xaxis=dict(side="bottom"),
    margin=dict(l=0, r=20, t=40, b=0),
    height=450,
)
st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("## Perbandingan Antar Ruangan")
compare_col1, compare_col2 = st.columns(2)

with compare_col1:
    room_summary = []
    for room in filtered_df["Ruangan"].unique():
        room_df = filtered_df[filtered_df["Ruangan"] == room]
        total = len(room_df)
        if total == 0:
            continue
        room_summary.append(
            {
                "Ruangan": room,
                "Total Alat": total,
                "Baik": (room_df["Kondisi"] == "Baik").sum(),
                "Rusak": (room_df["Kondisi"] != "Baik").sum(),
                "% Baik": round((room_df["Kondisi"] == "Baik").sum() / total * 100, 1),
                "Skor Kepatuhan": compute_compliance_score(room_df),
            }
        )

    summary_df = pd.DataFrame(room_summary).sort_values(
        "Skor Kepatuhan", ascending=False
    )
    st.markdown("#### Ranking Ruangan")
    st.dataframe(
        summary_df.style.background_gradient(
            subset=["Skor Kepatuhan", "% Baik"], cmap="RdYlGn"
        ),
        use_container_width=True,
    )

with compare_col2:
    if not summary_df.empty:
        fig_scatter = px.scatter(
            summary_df,
            x="Skor Kepatuhan",
            y="% Baik",
            size="Total Alat",
            color="Ruangan",
            title="Kepatuhan vs Kondisi per Ruangan",
            color_discrete_sequence=COLOR_SEQUENCE,
            size_max=40,
        )
        fig_scatter.add_hline(y=80, line_dash="dash", line_color="#f59e0b", opacity=0.5)
        fig_scatter.add_vline(x=80, line_dash="dash", line_color="#f59e0b", opacity=0.5)
        fig_scatter.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1e293b"),
            legend=dict(font=dict(size=9)),
            margin=dict(l=0, r=20, t=40, b=0),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("## Sistem Peringatan dan Risiko")

alert_tab1, alert_tab2, alert_tab3 = st.tabs(
    ["Risiko Kritis", "Alat Tanpa Kelengkapan", "Detail Risiko per Alat"]
)

with alert_tab1:
    critical_df = filtered_df[filtered_df["Tingkat_Risiko"] == "Kritis"]
    if len(critical_df) > 0:
        st.error(f"Ditemukan **{len(critical_df)} alat** dengan tingkat risiko kritis.")
        st.dataframe(
            critical_df[
                [
                    "ID_Alat",
                    "Nama_Alat",
                    "SN",
                    "Ruangan",
                    "Kondisi",
                    "Stiker_Label",
                    "Lembar_SOP",
                    "Stiker_Kalibrasi",
                    "Tingkat_Risiko",
                ]
            ],
            use_container_width=True,
        )
    else:
        st.success("Tidak ada alat dengan risiko kritis.")

with alert_tab2:
    incomplete_df = filtered_df[
        (filtered_df["Stiker_Label"] == "Tidak")
        | (filtered_df["Lembar_SOP"] == "Tidak")
        | (filtered_df["Stiker_Kalibrasi"] == "Tidak")
    ]
    if len(incomplete_df) > 0:
        st.warning(
            f"Ditemukan **{len(incomplete_df)} alat** yang tidak memiliki kelengkapan penuh."
        )

        gap_summary = pd.DataFrame(
            {
                "Kategori": ["Tanpa SOP", "Tanpa Label", "Tanpa Kalibrasi"],
                "Jumlah": [missing_sop, missing_label, missing_calibration],
            }
        )
        fig_gap = px.bar(
            gap_summary,
            x="Kategori",
            y="Jumlah",
            title="Ringkasan Ketidaklengkapan",
            color="Kategori",
            color_discrete_sequence=["#ef4444", "#f59e0b", "#6366f1"],
        )
        fig_gap.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1e293b"),
            showlegend=False,
            margin=dict(l=0, r=20, t=40, b=0),
        )
        st.plotly_chart(fig_gap, use_container_width=True)

        st.dataframe(
            incomplete_df[
                [
                    "ID_Alat",
                    "Nama_Alat",
                    "Ruangan",
                    "Stiker_Label",
                    "Lembar_SOP",
                    "Stiker_Kalibrasi",
                ]
            ],
            use_container_width=True,
        )
    else:
        st.success("Semua alat memiliki kelengkapan penuh.")

with alert_tab3:
    risk_counts = filtered_df["Tingkat_Risiko"].value_counts().reset_index()
    risk_counts.columns = ["Tingkat Risiko", "Jumlah"]
    risk_color_map = {
        "Kritis": "#ef4444",
        "Tinggi": "#f59e0b",
        "Sedang": "#3b82f6",
        "Rendah": "#22c55e",
    }
    fig_risk = px.pie(
        risk_counts,
        names="Tingkat Risiko",
        values="Jumlah",
        title="Distribusi Tingkat Risiko Alat",
        color="Tingkat Risiko",
        color_discrete_map=risk_color_map,
        hole=0.4,
    )
    fig_risk.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1e293b"),
        margin=dict(l=0, r=20, t=40, b=0),
    )
    fig_risk.update_traces(textposition="inside", textinfo="percent+value")
    st.plotly_chart(fig_risk, use_container_width=True)

    risk_room = (
        filtered_df.groupby(["Ruangan", "Tingkat_Risiko"])
        .size()
        .reset_index(name="Jumlah")
    )
    fig_risk_room = px.bar(
        risk_room,
        x="Ruangan",
        y="Jumlah",
        color="Tingkat_Risiko",
        title="Tingkat Risiko per Ruangan",
        barmode="stack",
        color_discrete_map=risk_color_map,
    )
    fig_risk_room.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1e293b"),
        xaxis=dict(tickangle=-45),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=20, t=40, b=0),
    )
    st.plotly_chart(fig_risk_room, use_container_width=True)

st.markdown("## Tabel Data Lengkap")

search_query = st.text_input("Cari alat (nama, ruangan, SN)...", "")

display_df = filtered_df.copy()
if search_query:
    mask = (
        display_df["Nama_Alat"].str.contains(search_query, case=False, na=False)
        | display_df["Ruangan"].str.contains(search_query, case=False, na=False)
        | display_df["SN"].astype(str).str.contains(search_query, case=False, na=False)
    )
    display_df = display_df[mask]

st.markdown(
    f"Menampilkan **{len(display_df)}** dari **{len(filtered_df)}** data yang difilter."
)
st.dataframe(display_df, use_container_width=True)

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#64748b; font-size:0.85rem;'>"
    "Dashboard Inventaris Alat Medis &bull; Data diperbarui secara berkala"
    "</div>",
    unsafe_allow_html=True,
)
