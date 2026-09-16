import streamlit as st
import numpy as np

# 1. Configuração da Página e Cores
st.set_page_config(page_title="Lidia's Calculator", page_icon="💠", layout="centered")

# Estilo CSS personalizado em tons de azul pastel
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f8fb;
    }
    div.stButton > button:first-child {
        background-color: #90caf9;
        color: #0d47a1;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
    div.stButton > button:first-child:hover {
        background-color: #64b5f6;
        color: white;
    }
    .destaque {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #42a5f5;
        color: #0d47a1;
    }
    h1, h2, h3, p {
        color: #2c3e50;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💠 Lidia's Calculator")
st.markdown("### Fator de Estrutura: BiFeO₃ (Co-K$\\alpha$)")

# Aqui entra a imagem da estrutura cristalina!
# Quando subir o código, suba também uma imagem chamada "estrutura.png" na mesma pasta.
try:
    st.image("estrutura.png", caption="Estrutura Cristalina R3c do BiFeO3", use_column_width=True)
except:
    st.info("Faça o upload de uma imagem chamada 'estrutura.png' no seu repositório para ela aparecer aqui.")

# 2. Dados Físicos (Co-Ka)
lam = 1.79026
a = 5.58267
c = 13.8816

atomos = [
    {'nome': 'Bi', 'x': 0.0, 'y': 0.0, 'z': -0.00104, 'B': 0.1026, 'fp': -3.611, 'fpp': 9.666, 
     'cm': [21.5724, 1.8315, 19.6800, 6.3275, 14.0722, 0.2374, 10.3705, 19.6053, 17.2640]},
    {'nome': 'Fe', 'x': 0.0, 'y': 0.0, 'z': 0.22165, 'B': 0.0711, 'fp': -2.464, 'fpp': 3.608, 
     'cm': [11.0425, 4.5735, 7.3740, 0.2972, 4.1346, 11.7957, 1.5299, 36.1584, 1.9104]},
    {'nome': 'O',  'x': 0.4314, 'y': 0.0139, 'z': 0.95210, 'B': 1.3739, 'fp': 0.048, 'fpp': 0.038, 
     'cm': [3.0485, 13.2771, 2.2868, 5.7011, 1.5463, 0.3239, 0.8670, 32.9089, 0.2508]}
]

def get_posicoes_equivalentes(x, y, z):
    pos_base = [(x, y, z), (-y, x-y, z), (y-x, -x, z), (-y, -x, z+0.5), (x, x-y, z+0.5), (y-x, y, z+0.5)]
    centros = [(0,0,0), (1/3, 2/3, 2/3), (2/3, 1/3, 1/3)]
    pos_unicas = []
    for cx, cy, cz in centros:
        for px, py, pz in pos_base:
            p_calc = ((px+cx)%1, (py+cy)%1, (pz+cz)%1)
            p_round = (round(p_calc[0], 4), round(p_calc[1], 4), round(p_calc[2], 4))
            if p_round not in [(round(u[0],4), round(u[1],4), round(u[2],4)) for u in pos_unicas]:
                pos_unicas.append(p_calc)
    return pos_unicas

# 3. Interface Limpa para o Celular
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1: h = st.number_input("h", value=1, step=1)
with col2: k = st.number_input("k", value=0, step=1)
with col3: l = st.number_input("l", value=-2, step=1)
mult = st.number_input("Multiplicidade do Plano", value=6, step=2)

if st.button("Calcular Intensidade", use_container_width=True):
    inv_d2 = (4.0/3.0) * (h**2 + h*k + k**2) / (a**2) + (l**2) / (c**2)
    
    if inv_d2 == 0:
        st.error("Planos (0 0 0) não geram difração.")
    else:
        d = np.sqrt(1.0 / inv_d2)
        s = 1.0 / (2.0 * d)
        theta = np.arcsin(lam * s)
        dois_theta = 2 * np.degrees(theta)
        LP = (1 + np.cos(2*theta)**2) / (np.sin(theta)**2 * np.cos(theta))
        
        F_real_total, F_imag_total = 0, 0
        resultados_at = []
        
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
            resultados_at.append({'nome': at['nome'], 'real': F_real_at, 'imag': F_imag_at, 'mod': mod_at})
            F_real_total += F_real_at
            F_imag_total += F_imag_at

        F_modulo_total = np.sqrt(F_real_total**2 + F_imag_total**2)
        I_bruta = mult * (F_modulo_total**2) * LP
        
        st.markdown(f"""
        <div class="destaque">
            <h4 style="margin-top: 0; color: #0d47a1;">Plano ({h} {k} {l})</h4>
            <b>2θ Calc:</b> {dois_theta:.2f}° <br>
            <b>Intensidade Bruta:</b> {I_bruta:,.0f}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Fator de Estrutura Total")
        cA, cB, cC = st.columns(3)
        cA.metric("A", f"{F_real_total:.1f}")
        cB.metric("B", f"{F_imag_total:.1f}")
        cC.metric("|F|", f"{F_modulo_total:.1f}")
        
        st.markdown("### Influência por Elemento")
        for res in resultados_at:
            with st.expander(f"Átomo {res['nome']} (Contribuição: {res['mod']:.1f})"):
                st.write(f"Parte Real: {res['real']:.1f} | Parte Imaginária: {res['imag']:.1f}")
