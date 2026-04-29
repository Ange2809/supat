import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(
    page_title="SUPAT - Suivi Patient",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PALETTE DE COULEURS (centralisée pour cohérence)
# ============================================================
COLORS = {
    "primary":    "#2DD4BF",   # Teal médical
    "secondary":  "#38BDF8",   # Sky blue
    "accent":     "#818CF8",   # Indigo doux
    "success":    "#4ADE80",   # Vert succès
    "warning":    "#FB923C",   # Orange alerte
    "danger":     "#F87171",   # Rouge danger
    "pink":       "#F472B6",   # Rose
    "bg_dark":    "rgba(8, 15, 30, 0.92)",
    "glass":      "rgba(255, 255, 255, 0.05)",
    "text_main":  "#F1F5F9",
    "text_muted": "#94A3B8",
    "border":     "rgba(45, 212, 191, 0.25)",
}

CHART_COLORS = [
    COLORS["primary"], COLORS["secondary"], COLORS["accent"],
    COLORS["warning"], COLORS["pink"], COLORS["success"]
]

# ============================================================
# STYLE GLOBAL — Optimisé & Structuré
# ============================================================
st.markdown(f"""
<style>
/* ─── Google Fonts ────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* ─── Fond global avec overlay ───────────────────────────── */
.stApp {{
    background-image:
        linear-gradient(135deg, rgba(8,15,30,0.72) 0%, rgba(12,28,54,0.68) 100%),
        url("https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=1920&q=80");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    font-family: 'Poppins', sans-serif;
}}

/* ─── Conteneur principal — Glassmorphism raffiné ────────── */
.main .block-container {{
    background: {COLORS['bg_dark']};
    border-radius: 20px;
    padding: 2.5rem 3rem;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.6),
        0 0 0 1px {COLORS['border']};
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
    max-width: 1400px;
}}

/* ─── Sidebar — Style premium ─────────────────────────────── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(8,15,30,0.97) 0%, rgba(15,28,55,0.97) 100%) !important;
    border-right: 1px solid {COLORS['border']} !important;
    backdrop-filter: blur(20px);
}}

[data-testid="stSidebar"] .block-container {{
    padding: 1.5rem 1rem;
}}

/* Titre sidebar */
[data-testid="stSidebar"] h1 {{
    font-family: 'Poppins', sans-serif !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: {COLORS['primary']} !important;
    letter-spacing: 0.5px;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid {COLORS['border']};
    margin-bottom: 1rem !important;
    text-shadow: 0 0 20px rgba(45,212,191,0.4);
}}

/* Radio sidebar */
[data-testid="stSidebar"] .stRadio label {{
    color: {COLORS['text_muted']} !important;
    font-size: 0.9rem;
    font-weight: 500;
    padding: 0.4rem 0.5rem;
    border-radius: 8px;
    transition: color 0.2s ease;
}}
[data-testid="stSidebar"] .stRadio label:hover {{
    color: {COLORS['primary']} !important;
}}

/* ─── Typographie principale ──────────────────────────────── */
h1 {{
    font-family: 'Poppins', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: {COLORS['text_main']} !important;
    letter-spacing: -0.5px;
    text-shadow: 0 2px 12px rgba(0,0,0,0.5);
    margin-bottom: 0.25rem !important;
}}

h2, h3 {{
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    color: {COLORS['primary']} !important;
    letter-spacing: 0.2px;
}}

h4, h5, h6 {{
    font-family: 'Poppins', sans-serif !important;
    font-weight: 500 !important;
    color: {COLORS['text_muted']} !important;
}}

p, li {{
    color: {COLORS['text_main']} !important;
    font-size: 0.95rem;
    line-height: 1.7;
}}

/* ─── Labels des inputs ───────────────────────────────────── */
.stTextInput label,
.stSelectbox label,
.stDateInput label {{
    color: {COLORS['text_muted']} !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-family: 'Poppins', sans-serif;
}}

/* ─── Champs de saisie ────────────────────────────────────── */
.stTextInput > div > div > input,
.stDateInput > div > div > input {{
    background: rgba(255,255,255,0.08) !important;
    color: {COLORS['text_main']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 10px !important;
    padding: 0.55rem 1rem !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}}
.stTextInput > div > div > input:focus,
.stDateInput > div > div > input:focus {{
    border-color: {COLORS['primary']} !important;
    box-shadow: 0 0 0 3px rgba(45,212,191,0.15) !important;
    outline: none !important;
}}
.stTextInput > div > div > input::placeholder {{
    color: rgba(148,163,184,0.5) !important;
}}

/* ─── Selectbox ───────────────────────────────────────────── */
.stSelectbox > div > div {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 10px !important;
    color: {COLORS['text_main']} !important;
    font-family: 'Poppins', sans-serif !important;
}}
.stSelectbox > div > div:focus-within {{
    border-color: {COLORS['primary']} !important;
    box-shadow: 0 0 0 3px rgba(45,212,191,0.15) !important;
}}

/* ─── Bouton principal ────────────────────────────────────── */
.stButton > button,
.stFormSubmitButton > button {{
    background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%) !important;
    color: #0a0f1e !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.65rem 2rem !important;
    font-weight: 700 !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.5px;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(45,212,191,0.3) !important;
}}
.stButton > button:hover,
.stFormSubmitButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 25px rgba(45,212,191,0.5) !important;
    filter: brightness(1.08);
}}
.stButton > button:active,
.stFormSubmitButton > button:active {{
    transform: translateY(0px) !important;
}}

/* ─── Bouton téléchargement ───────────────────────────────── */
.stDownloadButton > button {{
    background: rgba(45,212,191,0.12) !important;
    color: {COLORS['primary']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 10px !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
}}
.stDownloadButton > button:hover {{
    background: rgba(45,212,191,0.22) !important;
    border-color: {COLORS['primary']} !important;
    transform: translateY(-1px) !important;
}}

/* ─── Métriques / KPI Cards ───────────────────────────────── */
[data-testid="stMetric"] {{
    background: {COLORS['glass']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.5rem !important;
    backdrop-filter: blur(8px);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}}
[data-testid="stMetric"]:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(45,212,191,0.2);
}}
[data-testid="stMetricLabel"] {{
    color: {COLORS['text_muted']} !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'Poppins', sans-serif !important;
}}
[data-testid="stMetricValue"] {{
    color: {COLORS['primary']} !important;
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    font-family: 'Poppins', sans-serif !important;
    line-height: 1.2;
}}

/* ─── Dataframe / Table ───────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid {COLORS['border']} !important;
}}

/* ─── Messages système ────────────────────────────────────── */
.stSuccess, .stInfo, .stWarning, .stError {{
    border-radius: 12px !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 500;
}}

/* ─── Divider horizontal ──────────────────────────────────── */
hr {{
    border-color: {COLORS['border']} !important;
    margin: 1.5rem 0 !important;
}}

/* ─── Scrollbar personnalisée ─────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.03); }}
::-webkit-scrollbar-thumb {{
    background: {COLORS['border']};
    border-radius: 10px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: {COLORS['primary']};
}}

/* ─── Spinner / Progress ──────────────────────────────────── */
.stSpinner > div {{
    border-top-color: {COLORS['primary']} !important;
}}

/* ─── Form container ──────────────────────────────────────── */
[data-testid="stForm"] {{
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
}}
</style>
""", unsafe_allow_html=True)


# ============================================================
# BASE DE DONNÉES (SQLite — inchangée fonctionnellement)
# ============================================================
def init_db():
    conn = sqlite3.connect('supat_medical.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            sexe TEXT,
            ville TEXT,
            maladie TEXT,
            date_consultation TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def load_patients():
    conn = sqlite3.connect('supat_medical.db')
    df = pd.read_sql_query("SELECT * FROM patients", conn)
    conn.close()
    return df

def insert_patient(nom, sexe, ville, maladie, date_consultation, email):
    conn = sqlite3.connect('supat_medical.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO patients (nom, sexe, ville, maladie, date_consultation, email)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nom, sexe, ville, maladie, str(date_consultation), email))
    conn.commit()
    conn.close()


# ============================================================
# CONSTANTES (inchangées)
# ============================================================
MALADIES = ["Diabète", "Hypertension", "Paludisme", "Asthme", "Cardiopathie", "Autre"]
SEXES    = ["Masculin", "Féminin"]
VILLES   = ["Yaoundé", "Douala", "Bafoussam", "Garoua", "Maroua", "Bamenda", "Autre"]


# ============================================================
# HELPER — Layout graphique unifié Plotly
# ============================================================
def plotly_layout(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(family="Poppins", size=15, color=COLORS["text_main"]), x=0.02),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.03)",
        font=dict(family="Poppins", color=COLORS["text_main"], size=12),
        margin=dict(l=16, r=16, t=40, b=16),
        legend=dict(
            bgcolor="rgba(255,255,255,0.05)",
            bordercolor=COLORS["border"],
            borderwidth=1,
            font=dict(color=COLORS["text_main"])
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.08)",
            tickfont=dict(color=COLORS["text_muted"])
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.08)",
            tickfont=dict(color=COLORS["text_muted"])
        ),
        hoverlabel=dict(
            bgcolor="rgba(8,15,30,0.95)",
            bordercolor=COLORS["primary"],
            font=dict(family="Poppins", color=COLORS["text_main"])
        )
    )
    return fig


# ============================================================
# COMPOSANT — Titre de page avec badge décoratif
# ============================================================
def page_header(icon: str, title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid {COLORS['border']};
    ">
        <div style="font-size: 2.5rem; margin-bottom: 0.3rem;">{icon}</div>
        <h1 style="
            color: {COLORS['text_main']} !important;
            font-size: 1.85rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
            margin: 0 !important;
            text-shadow: 0 0 30px rgba(45,212,191,0.25);
        ">{title}</h1>
        {"<p style='color:" + COLORS['text_muted'] + " !important; font-size:0.9rem; margin-top:0.4rem;'>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# COMPOSANT — Section card wrapper
# ============================================================
def section_card(label: str, icon: str = ""):
    st.markdown(f"""
    <div style="
        display: flex; align-items: center; gap: 0.5rem;
        margin: 1.5rem 0 0.75rem 0;
    ">
        <span style="font-size:1.1rem;">{icon}</span>
        <span style="
            color: {COLORS['text_muted']};
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        ">{label}</span>
        <div style="flex:1; height:1px; background:{COLORS['border']}; margin-left:0.5rem;"></div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# NAVIGATION SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 0.5rem 0 1.5rem 0;">
        <div style="font-size:2rem;">🏥</div>
        <div style="
            color: {COLORS['primary']};
            font-size: 1.3rem;
            font-weight: 700;
            letter-spacing: 2px;
            text-shadow: 0 0 20px rgba(45,212,191,0.5);
        ">SUPAT</div>
        <div style="color:{COLORS['text_muted']}; font-size:0.72rem; letter-spacing:1px;">
            SUIVI PATIENT CAMEROUN
        </div>
    </div>
    <hr style="border-color:{COLORS['border']}; margin-bottom:1rem;">
    """, unsafe_allow_html=True)

    menu = st.radio(
        "Navigation",
        ["📝 Accueil (Formulaire)", "📊 Dashboard Admin", "📈 Analyse Descriptive"],
        label_visibility="collapsed"
    )

    st.markdown(f"""
    <hr style="border-color:{COLORS['border']}; margin-top:2rem;">
    <div style="
        text-align:center;
        color:{COLORS['text_muted']};
        font-size:0.7rem;
        padding-top:0.5rem;
    ">
        v1.0 · © 2025 SUPAT<br>
        <span style="color:{COLORS['primary']};">●</span> Système actif
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE 1 — FORMULAIRE PATIENT
# ============================================================
if menu == "📝 Accueil (Formulaire)":
    page_header("📝", "Enregistrement Patient", "Remplissez les informations du patient ci-dessous")

    with st.form("patient_form", clear_on_submit=True):
        section_card("Informations personnelles", "👤")
        col1, col2 = st.columns(2, gap="large")

        with col1:
            nom   = st.text_input("Nom complet", placeholder="Ex : Jean Dupont")
            sexe  = st.selectbox("Sexe", SEXES)
            email = st.text_input("Adresse Email", placeholder="Ex : jean.dupont@mail.com")

        with col2:
            ville             = st.selectbox("Ville de résidence", VILLES)
            maladie           = st.selectbox("Maladie diagnostiquée", MALADIES)
            date_consultation = st.date_input("Date de consultation", date.today())

        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.form_submit_button("💾 Enregistrer le patient", use_container_width=True)

    if submit_button:
        if nom and email:
            insert_patient(nom, sexe, ville, maladie, date_consultation, email)
            st.success(f"✅ Le patient **{nom}** a été enregistré avec succès !")
            st.balloons()
        else:
            st.error("⚠️ Veuillez remplir au minimum le **nom** et l'**email**.")


# ============================================================
# PAGE 2 — DASHBOARD ADMIN
# ============================================================
elif menu == "📊 Dashboard Admin":
    page_header("📊", "Dashboard Administrateur", "Vue globale et base de données des patients enregistrés")

    df = load_patients()

    if df.empty:
        st.info("ℹ️ Aucun patient enregistré pour le moment. Commencez par le formulaire d'accueil.")
    else:
        # ── KPI Cards ──────────────────────────────────────────
        section_card("Indicateurs Clés", "📌")
        col1, col2, col3, col4 = st.columns(4, gap="medium")

        total    = len(df)
        hommes   = len(df[df['sexe'] == 'Masculin'])
        femmes   = len(df[df['sexe'] == 'Féminin'])
        maladies = df['maladie'].nunique()

        col1.metric("👥 Total Patients", total)
        col2.metric("👨 Hommes",          hommes,  delta=f"{round(hommes/total*100)}%")
        col3.metric("👩 Femmes",          femmes,  delta=f"{round(femmes/total*100)}%")
        col4.metric("🦠 Maladies dist.",  maladies)

        # ── Graphique rapide (mini bar) ────────────────────────
        section_card("Aperçu rapide par maladie", "📉")
        snap_counts = df['maladie'].value_counts().reset_index()
        snap_counts.columns = ['Maladie', 'Nombre']
        fig_snap = px.bar(
            snap_counts, x='Maladie', y='Nombre',
            color='Maladie',
            color_discrete_sequence=CHART_COLORS,
            text_auto=True,
            height=260
        )
        fig_snap = plotly_layout(fig_snap)
        fig_snap.update_traces(marker_line_width=0, textfont=dict(color=COLORS["text_main"]))
        st.plotly_chart(fig_snap, use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Base de données ────────────────────────────────────
        section_card("Base de données patients", "🗄️")

        search = st.text_input("🔍 Rechercher un patient", placeholder="Nom, ville, maladie...")
        display_df = df.drop(columns=['id'])
        if search:
            mask = display_df.apply(
                lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1
            )
            display_df = display_df[mask]

        st.dataframe(
            display_df,
            use_container_width=True,
            height=380
        )

        st.markdown("<br>", unsafe_allow_html=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger les données (CSV)",
            data=csv,
            file_name='supat_patients.csv',
            mime='text/csv',
        )


# ============================================================
# PAGE 3 — ANALYSE DESCRIPTIVE
# ============================================================
elif menu == "📈 Analyse Descriptive":
    page_header("📈", "Analyse Descriptive", "Exploration visuelle des données collectées par SUPAT")

    df = load_patients()

    if df.empty:
        st.warning("⚠️ Pas assez de données pour générer des graphiques. Enregistrez d'abord des patients.")
    else:
        # ── Graphiques Ligne 1 ─────────────────────────────────
        section_card("Répartitions démographiques", "📊")
        col1, col2 = st.columns(2, gap="large")

        with col1:
            # Bar — Répartition par Maladie
            disease_counts = df['maladie'].value_counts().reset_index()
            disease_counts.columns = ['Maladie', 'Nombre']

            fig_maladie = px.bar(
                disease_counts, x='Maladie', y='Nombre',
                color='Maladie',
                color_discrete_sequence=CHART_COLORS,
                text_auto=True,
                height=340
            )
            fig_maladie = plotly_layout(fig_maladie, "Répartition par Maladie")
            fig_maladie.update_traces(
                marker_line_width=0,
                textfont=dict(color=COLORS["text_main"], size=11),
                hovertemplate="<b>%{x}</b><br>Patients : %{y}<extra></extra>"
            )
            st.plotly_chart(fig_maladie, use_container_width=True)

        with col2:
            # Donut — Répartition par Sexe
            gender_counts = df['sexe'].value_counts().reset_index()
            gender_counts.columns = ['Sexe', 'Nombre']

            fig_sexe = px.pie(
                gender_counts, values='Nombre', names='Sexe',
                hole=0.52,
                color_discrete_sequence=[COLORS["secondary"], COLORS["pink"]],
                height=340
            )
            fig_sexe = plotly_layout(fig_sexe, "Répartition par Sexe")
            fig_sexe.update_traces(
                textfont=dict(color=COLORS["text_main"], size=12),
                hovertemplate="<b>%{label}</b><br>%{value} patients (%{percent})<extra></extra>",
                marker=dict(line=dict(color="rgba(0,0,0,0.3)", width=2))
            )
            st.plotly_chart(fig_sexe, use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Graphiques Ligne 2 ─────────────────────────────────
        section_card("Répartition géographique & temporelle", "🗺️")
        col3, col4 = st.columns([1.4, 1], gap="large")

        with col3:
            # Bar horizontal — Répartition par Ville
            ville_counts = df['ville'].value_counts().reset_index()
            ville_counts.columns = ['Ville', 'Nombre']

            fig_ville = px.bar(
                ville_counts, x='Nombre', y='Ville',
                orientation='h',
                color='Nombre',
                color_continuous_scale=[[0, COLORS["accent"]], [1, COLORS["primary"]]],
                text_auto=True,
                height=340
            )
            fig_ville = plotly_layout(fig_ville, "Répartition géographique (Villes)")
            fig_ville.update_traces(
                textfont=dict(color=COLORS["text_main"], size=11),
                hovertemplate="<b>%{y}</b><br>Patients : %{x}<extra></extra>"
            )
            fig_ville.update_layout(coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig_ville, use_container_width=True)

        with col4:
            # Donut — Répartition par Maladie (anneau)
            fig_mal_pie = px.pie(
                disease_counts, values='Nombre', names='Maladie',
                hole=0.45,
                color_discrete_sequence=CHART_COLORS,
                height=340
            )
            fig_mal_pie = plotly_layout(fig_mal_pie, "Part de chaque maladie")
            fig_mal_pie.update_traces(
                textfont=dict(color=COLORS["text_main"], size=11),
                hovertemplate="<b>%{label}</b><br>%{value} cas (%{percent})<extra></extra>",
                marker=dict(line=dict(color="rgba(0,0,0,0.3)", width=2))
            )
            st.plotly_chart(fig_mal_pie, use_container_width=True)

        # ── Tableau récapitulatif ──────────────────────────────
        section_card("Résumé statistique", "🔢")
        stat_df = df.groupby('maladie').agg(
            Total=('nom', 'count'),
            Hommes=('sexe', lambda x: (x == 'Masculin').sum()),
            Femmes=('sexe', lambda x: (x == 'Féminin').sum()),
        ).reset_index().rename(columns={'maladie': 'Maladie'})
        stat_df['Ratio H/F'] = (stat_df['Hommes'] / stat_df['Femmes'].replace(0, 1)).round(2)
        st.dataframe(stat_df, use_container_width=True)

# ─── Footer global ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    text-align: center;
    padding: 2rem 0 0.5rem 0;
    margin-top: 2rem;
    border-top: 1px solid {COLORS['border']};
">
    <span style="color:{COLORS['text_muted']}; font-size:0.75rem; letter-spacing:0.5px;">
        🏥 <b style='color:{COLORS['primary']};'>SUPAT</b> · Système de Suivi Patient · Cameroun · 2025
    </span>
</div>
""", unsafe_allow_html=True)
