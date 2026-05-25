import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Sledování odpadních vod", initial_sidebar_state="expanded")

lang = st.sidebar.radio("Language / Jazyk", ["Čeština", "English"])

texts = {
    "title": "🦠 Monitorování patogenů v odpadních vodách" if lang == "Čeština" else "🦠 Wastewater Pathogen Monitoring",
    "subtitle": "Indikátory sledování a virová nálož v reálném čase" if lang == "Čeština" else "Tracking indicators and real-time viral load",
    "active": "⬤ Aktivní systém" if lang == "Čeština" else "⬤ Active System",
    "proj_info": "Informace o projektu" if lang == "Čeština" else "Project Information",
    "virus_info": "Informace o virech" if lang == "Čeština" else "Virus Information",
    "filters": "🎛️ Filtry dat" if lang == "Čeština" else "🎛️ Data Filters",
    "pathogens": "Cílové patogeny" if lang == "Čeština" else "Target Pathogens",
    "cities": "Místa odběru (ČOV)" if lang == "Čeština" else "Sampling locations (WWTP)",
    "timeline": "Časová osa" if lang == "Čeština" else "Timeline",
    "samples": "Zpracované vzorky" if lang == "Čeština" else "Processed samples",
    "avg_load": "Průměrná nálož (kopie/ml)" if lang == "Čeština" else "Average load (copies/ml)",
    "avg_gu": "Průměrné GU/l" if lang == "Čeština" else "Average GU/l",
    "monitored": "Sledované ČOV" if lang == "Čeština" else "Monitored WWTPs",
    "tab_resp": "Respirační viry" if lang == "Čeština" else "Respiratory viruses",
    "tab_hpv": "HPV data" if lang == "Čeština" else "HPV data",
    "t_overview": "📊 Přehled, mapa a trendy" if lang == "Čeština" else "📊 Overview, map and trends",
    "t_hist": "📈 Analytické histogramy" if lang == "Čeština" else "📈 Analytical histograms",
    "t_data": "📋 Zdrojová data" if lang == "Čeština" else "📋 Source data",
    "map_err": "K vybranému datu nejsou dostupná data pro mapu." if lang == "Čeština" else "No map data available for the selected date.",
    "hpv_placeholder": "Data pro HPV budou zobrazena zde." if lang == "Čeština" else "HPV data will be displayed here."
}

st.markdown(f"""
    <style>
    .block-container {{
        padding-top: 0rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }}
    .top-nav {{
        background-color: #0f172a;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        margin-top: 10px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #1e293b;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}
    .top-nav h1 {{
        margin: 0;
        font-size: 26px;
        color: #38bdf8;
        font-family: 'Arial', sans-serif;
    }}
    .top-nav p {{
        margin: 0;
        color: #94a3b8;
        font-size: 14px;
        margin-top: 4px;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: #1e293b;
        padding: 10px;
        border-radius: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #334155;
        border-radius: 4px;
        padding: 8px 18px;
        color: #f8fafc;
        border: 1px solid #475569;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #0ea5e9 !important;
        color: white !important;
        border-color: #0284c7 !important;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 32px;
        color: #38bdf8;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 14px;
        color: #94a3b8;
    }}
    </style>
    
    <div class="top-nav">
        <div>
            <h1>{texts['title']}</h1>
            <p>{texts['subtitle']}</p>
        </div>
        <div>
            <p style="color: #10b981; font-weight: bold;">{texts['active']}</p>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"### {texts['proj_info']}")
st.markdown("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.")
st.markdown("<br>", unsafe_allow_html=True)

with st.sidebar.expander(texts['virus_info'], expanded=False):
    st.markdown("**SARS-CoV-2:** Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
    st.markdown("**RSV:** Sed do eiusmod tempor incididunt ut labore et dolore.")
    st.markdown("**Chřipka A / Influenza A:** Ut enim ad minim veniam, quis nostrud exercitation.")
    st.markdown("**PMMoV:** Duis aute irure dolor in reprehenderit in voluptate.")
    st.markdown("**HPV:** Excepteur sint occaecat cupidatat non proident.")

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

st.sidebar.markdown(f"### {texts['filters']}")
selected_pathogens = st.sidebar.multiselect(texts['pathogens'], df['Patogen'].unique(), default=df['Patogen'].unique())
selected_cities = st.sidebar.multiselect(texts['cities'], df['Město'].unique(), default=df['Město'].unique())
date_range = st.sidebar.slider(
    texts['timeline'], 
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

main_tab_resp, main_tab_hpv = st.tabs([texts['tab_resp'], texts['tab_hpv']])

with main_tab_hpv:
    st.markdown(f"*{texts['hpv_placeholder']}*")
    st.markdown("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")

with main_tab_resp:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(texts['samples'], len(filtered_df))

    if not filtered_df.empty:
        col2.metric(texts['avg_load'], f"{filtered_df['Virová_nálož_kopie_ml'].mean():.1f}")
        col3.metric(texts['avg_gu'], f"{filtered_df['GU_na_l'].mean():,.0f}".replace(",", " "))
    else:
        col2.metric(texts['avg_load'], "0.0")
        col3.metric(texts['avg_gu'], "0")
        
    col4.metric(texts['monitored'], len(selected_cities))

    st.markdown("<br>", unsafe_allow_html=True)

    tab_overview, tab_histograms, tab_data = st.tabs([texts['t_overview'], texts['t_hist'], texts['t_data']])

    with tab_overview:
        map_col, pie_col = st.columns(2)
        
        with map_col:
            latest_date = filtered_df['Datum'].max()
            map_data = filtered_df[filtered_df['Datum'] == latest_date]
            
            if map_data.empty and not filtered_df.empty:
                latest_date = filtered_df['Datum'].max()
                map_data = filtered_df[filtered_df['Datum'] == latest_date]

            if not map_data.empty:
                fig_map = px.scatter_mapbox(
                    map_data, lat="Zeměpisná_šířka", lon="Zeměpisná_délka", size="GU_na_l",
                    color="Patogen",
                    hover_name="Město", hover_data=["GU_na_l"],
                    zoom=6.0, center={"lat": 49.8, "lon": 15.5},
                    mapbox_style="carto-positron",
                    title=f"Prostorové rozložení k {latest_date.date()}"
                )
                fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=400)
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.info(texts['map_err'])
            
        with pie_col:
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

    with tab_data:
        st.dataframe(filtered_df.sort_values(by="Datum", ascending=False), use_container_width=True, height=400)