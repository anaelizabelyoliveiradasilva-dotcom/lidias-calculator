import streamlit as st
import numpy as np
import pandas as pd

# 1. Configuração da Página (Layout Largo para o Dashboard)
st.set_page_config(page_title="Lidia's Calculator", page_icon="💠", layout="wide")

# Estilo CSS para replicar o seu design limpo em tons frios
st.markdown("""
    <style>
    .stApp { background-color: #f0f4f8; }
    div.stButton > button:first-child {
        background-color: #1e88e5; color: white; border-radius: 8px; font-weight: bold;
    }
    div.stButton > button:first-child:hover { background-color: #1565c0; color: white; }
    .card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("<h1>💠 Lidia's Calculator</h1>", unsafe_allow_html=True)
st.markdown("### BiFeO₃ Crystallographic Plane Calculator", unsafe_allow_html=True)
st.markdown("---")

# Dados Físicos (Co-Ka)
lam, a, c = 1.79026, 5.58267, 13.8816
atomos = [
    {'nome': 'Bi', 'x': 0.0, 'y': 0.0, 'z': -0.00104, 'B': 0.1026, 'fp': -3.611, 'fpp': 9.666, 'cm': [21.5724, 1.8315, 19.6800, 6.3275, 14.0722, 0.2374, 10.3705, 19.6053, 17.2640]},
    {'nome': 'Fe', 'x': 0.0, 'y': 0.0, 'z': 0.22165, 'B': 0.0711, 'fp': -2.464, 'fpp': 3.608, 'cm': [11.0425, 4.5735, 7.3740, 0.2972, 4.1346, 11.7957, 1.5299, 36.1584, 1.9104]},
    {'nome': 'O',  'x': 0.4314, 'y': 0.0139, 'z': 0.95210, 'B': 1.3739, 'fp': 0.048, 'fpp': 0.038, 'cm': [3.0485, 13.2771, 2.2868, 5.7011, 1.5463, 0.3239, 0.8670, 32.9089, 0.2508]}
]

def get_posicoes_equivalentes(x, y, z):
    pos_base = [(x, y, z), (-y, x-y, z), (y-x, -x, z), (-y, -x, z+0.5), (x, x-y, z+0.5), (y-x, y, z+0.5)]
    centros = [(0,0,0), (1/3, 2/3, 2/3), (2/3, 1/3, 1/3)]
    return [((px+cx)%1, (py+cy)%1, (pz+cz)%1) for cx, cy, cz in centros for px, py, pz in pos_base]

# Layout em duas colunas principais (igual ao seu design)
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🧮 Calculate a Plane")
    st.write("Enter Miller indices (h k l)")
    
    h_col, k_col, l_col = st.columns(3)
    with h_col: h = st.number_input("h", value=1, step=1)
    with k_col: k = st.number_input("k", value=1, step=1)
    with l_col: l = st.number_input("l", value=0, step=1)
    
    calcular = st.button("Calculate", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Exibe a imagem gerada abaixo dos inputs
    try:
        st.image("estrutura.png", use_column_width=True)
    except:
        pass

with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"### 📊 Results for plane ({h} {k} {l})")
    
    # CORREÇÃO DO PLANO CRISTALOGRÁFICO: Regra de Seleção para R3c (-h + k + l = 3n)
    if (-h + k + l) % 3 != 0:
        st.error(f"⚠️ Ausência Sistemática: O plano ({h} {k} {l}) é proibido pela regra de reflexão do grupo espacial R3c ($-h+k+l = 3n$). A intensidade é zero.")
    elif h == 0 and k == 0 and l == 0:
        st.error("⚠️ Planos (0 0 0) não geram difração.")
    else:
        # Cálculos Físicos
        inv_d2 = (4.0/3.0) * (h**2 + h*k + k**2) / (a**2) + (l**2) / (c**2)
        d = np.sqrt(1.0 / inv_d2)
        s = 1.0 / (2.0 * d)
        
        resultados_at = {}
        F_real_total, F_imag_total = 0, 0
        
        for at in atomos:
            F_real_at, F_imag_at = 0, 0
            cm = at['cm']
            f0 = cm[0]*np.exp(-cm[1]*s**2) + cm[2]*np.exp(-cm[3]*s**2) + cm[4]*np.exp(-cm[5]*s**2) + cm[6]*np.exp(-cm[7]*s**2) + cm[8]
            f_real_term = (f0 + at['fp']) * np.exp(-at['B'] * s**2)
            f_imag_term = at['fpp'] * np.exp(-at['B'] * s**2)
            
            for px, py, pz in get_posicoes_equivalentes(at['x'], at['y'], at['z']):
                fase = 2 * np.pi * (h*px + k*py + l*pz)
                F_real_at += f_real_term * np.cos(fase) - f_imag_term * np.sin(fase)
                F_imag_at += f_real_term * np.sin(fase) + f_imag_term * np.cos(fase)
            
            mod_at = np.sqrt(F_real_at**2 + F_imag_at**2)
            resultados_at[at['nome']] = mod_at
            F_real_total += F_real_at
            F_imag_total += F_imag_at

        F_modulo_total = np.sqrt(F_real_total**2 + F_imag_total**2)

        # Módulos de Cartões (Cards) para os elementos
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🟣 Bi contribution", f"{resultados_at['Bi']:.3f}")
        m2.metric("🟠 Fe contribution", f"{resultados_at['Fe']:.3f}")
        m3.metric("🔴 O contribution", f"{resultados_at['O']:.3f}")
        m4.metric("📈 Intensity |F|", f"{F_modulo_total:.3f}")
        
        st.markdown("---")
        
        # Gráfico de Barras igual ao design
        st.markdown("##### Element Contributions")
        df_chart = pd.DataFrame({
            "Element": ["Bi", "Fe", "O"],
            "Contribution": [resultados_at['Bi'], resultados_at['Fe'], resultados_at['O']]
        })
        st.bar_chart(df_chart.set_index("Element"), height=250, use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
