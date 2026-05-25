import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Sledování odpadních vod", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .block-container {
        padding-top: 0rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #1e293b;
        padding: 10px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #334155;
        border-radius: 4px;
        padding: 8px 18px;
        color: #f8fafc;
        border: 1px solid #475569;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0ea5e9 !important;
        color: white !important;
        border-color: #0284c7 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 32px;
        color: #38bdf8;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #94a3b8;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    np.random.seed(42)
    dates = [datetime.today() - timedelta(days=i) for i in range(180)]
    cities = {
        'Praha': (50.0755, 14.4378),
        'Brno': (49.1951, 16.6068),
        'Ostrava': (49.8209, 18.2625),
        'Plzeň': (49.7384, 13.3736),
        'Liberec': (50.7671, 15.0562)
    }
    pathogens = ['SARS-CoV-2', 'RSV', 'Chřipka A', 'PMMoV']
    
    data = []
    for date in dates:
        for city, coords in cities.items():
            for pathogen in pathogens:
                if pathogen == 'SARS-CoV-2':
                    base_val = np.random.normal(120, 25)
                elif pathogen == 'PMMoV':
                    base_val = np.random.normal(5000, 800)
                else:
                    base_val = np.random.normal(60, 25)
                    
                vl = max(0, base_val + np.random.normal(0, 15))
                fecal_load = np.random.uniform(500, 2500)
                
                data.append({
                    'ID_vzorku': f"VZR-{np.random.randint(10000, 99999)}",
                    'Datum': date,
                    'Týden': date - timedelta(days=date.weekday()),
                    'Město': city,
                    'Zeměpisná_šířka': coords[0],
                    'Zeměpisná_délka': coords[1],
                    'Patogen': pathogen,
                    'Virová_nálož_kopie_ml': vl,
                    'GU_na_l': vl * 1000 * np.random.uniform(0.9, 1.1),
                    'Fekální_zátěž': fecal_load,
                    'Poměr_Patogen_Fekální': (vl * 1000) / fecal_load
                })
                
    df = pd.DataFrame(data)
    
    unique_weeks = df['Týden'].unique()
    no_sample_weeks = np.random.choice(unique_weeks, size=int(len(unique_weeks) * 0.15), replace=False)
    
    df = df[~df['Týden'].isin(no_sample_weeks)]
    
    df['Výsledek_Vzorku'] = np.random.choice(['Pozitivní', 'Negativní'], p=[0.40, 0.60], size=len(df))
    
    return df

df = load_data()

st.sidebar.markdown("### 🎛️ Filtry dat")
selected_pathogens = st.sidebar.multiselect("Cílové patogeny", df['Patogen'].unique(), default=df['Patogen'].unique())
selected_cities = st.sidebar.multiselect("Místa odběru (ČOV)", df['Město'].unique(), default=df['Město'].unique())
date_range = st.sidebar.slider(
    "Časová osa", 
    min_value=df['Datum'].min().date(), 
    max_value=df['Datum'].max().date(),
    value=(df['Datum'].min().date() + timedelta(days=30), df['Datum'].max().date())
)

filtered_df = df[
    (df['Patogen'].isin(selected_pathogens)) & 
    (df['Město'].isin(selected_cities)) &
    (df['Datum'].dt.date >= date_range[0]) &
    (df['Datum'].dt.date <= date_range[1])
]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Zpracované vzorky", len(filtered_df))

if not filtered_df.empty:
    col2.metric("Průměrná nálož (kopie/ml)", f"{filtered_df['Virová_nálož_kopie_ml'].mean():.1f}")
    col3.metric("Průměrné GU/l", f"{filtered_df['GU_na_l'].mean():,.0f}".replace(",", " "))
else:
    col2.metric("Průměrná nálož (kopie/ml)", "0.0")
    col3.metric("Průměrné GU/l", "0")
    
col4.metric("Sledované ČOV", len(selected_cities))

st.markdown("<br>", unsafe_allow_html=True)

tab_overview, tab_histograms = st.tabs(["📊 Přehled a trendy", "📈 Analytické histogramy"])

with tab_overview:
    if not filtered_df.empty:
        fig_pie = px.sunburst(
            filtered_df, path=['Město', 'Patogen'], values='GU_na_l',
            title="Podíl celkových GU/l podle ČOV a patogenu",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_pie.update_layout(margin=dict(t=40, b=20, l=20, r=20), height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if not filtered_df.empty:
        fig_trend = px.line(
            filtered_df, x='Datum', y='GU_na_l', color='Patogen', line_group='Město', hover_name='Město',
            markers=True,
            title="Časové trendy GU/l"
        )
        fig_trend.update_layout(
            margin=dict(t=40, b=10, l=10, r=10), height=400
        )
        st.plotly_chart(fig_trend, use_container_width=True)

with tab_histograms:
    hist_col1, hist_col2 = st.columns(2)
    
    with hist_col1:
        if not filtered_df.empty:
            fig_hist1 = px.histogram(
                filtered_df, x="GU_na_l", color="Patogen", nbins=80, barmode="overlay",
                title="Koncentrace patogenu (GU/l)"
            )
            fig_hist1.update_layout(bargap=0.2, margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig_hist1, use_container_width=True)
        
    with hist_col2:
        if not filtered_df.empty:
            fig_hist2 = px.histogram(
                filtered_df, x="Poměr_Patogen_Fekální", color="Patogen", nbins=80, barmode="overlay",
                title="Poměr patogenu vůči fekální zátěži"
            )
            fig_hist2.update_layout(bargap=0.2, margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig_hist2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if not filtered_df.empty:
        weekly_counts = filtered_df.groupby(['Týden', 'Výsledek_Vzorku', 'Patogen']).size().reset_index(name='Počet')
        weekly_counts['Týden_Str'] = weekly_counts['Týden'].dt.strftime('%V<br>%Y')
        
        weekly_counts['Textový_Štítek'] = weekly_counts.apply(
            lambda x: str(x['Počet']) if x['Počet'] > 0 else "", axis=1
        )
        
        start_date_obj = pd.to_datetime(date_range[0])
        end_date_obj = pd.to_datetime(date_range[1])
        start_week = start_date_obj - pd.Timedelta(days=start_date_obj.weekday())
        
        all_weeks_str = []
        curr = start_week
        while curr <= end_date_obj:
            all_weeks_str.append(curr.strftime('%V<br>%Y'))
            curr += pd.Timedelta(days=7)
        
        fig_bar = px.bar(
            weekly_counts, 
            x="Týden_Str", 
            y="Počet", 
            color="Výsledek_Vzorku",
            facet_row="Patogen",
            text="Textový_Štítek",
            color_discrete_map={'Pozitivní': '#E69F00', 'Negativní': '#999999'},
            category_orders={"Výsledek_Vzorku": ["Negativní", "Pozitivní"], "Týden_Str": all_weeks_str}
        )
        
        dynamic_height = 250 * len(selected_pathogens) + 150 if len(selected_pathogens) > 0 else 600
        
        fig_bar.update_layout(
            barmode='relative',
            barnorm='percent',
            yaxis_title="Vzorky odpadních vod %",
            xaxis_title="Kalendářní týden",
            margin=dict(t=40, b=60, l=60, r=20),
            height=dynamic_height,
            legend_title_text="Výsledek vzorku",
            plot_bgcolor='white',
            xaxis=dict(showgrid=False, tickangle=0)
        )
        
        fig_bar.update_yaxes(showgrid=True, gridcolor='#eeeeee', tickvals=[0, 25, 50, 75, 100], ticktext=['0%', '25%', '50%', '75%', '100%'])
        
        fig_bar.update_traces(
            textposition='inside', 
            textfont=dict(color='black', size=11),
            insidetextanchor='middle',
            marker_line_color='white',
            marker_line_width=0.5
        )
        st.plotly_chart(fig_bar, use_container_width=True)
