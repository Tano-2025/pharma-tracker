import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="PharmaTrack Web", layout="wide")

# --- ESTADO DE LA SESIÓN ---
if 'bitacora' not in st.session_state:
    st.session_state.bitacora = pd.DataFrame(columns=["Lote", "Producto", "Operador", "Etapa", "Evento", "Hora"])

if 'usuario_autenticado' not in st.session_state:
    st.session_state.usuario_autenticado = None

# --- LÓGICA DE LOGIN (FORMULARIO) ---
def login():
    st.title("🔐 Ingreso al Sistema Pharma")
    
    # Usamos un formulario para evitar que la página se recargue en cada tecla
    with st.form("login_form"):
        codigo = st.text_input("Código de Usuario")
        clave = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar", use_container_width=True)

        if submit:
            # Simulación de base de datos de usuarios
            nombres_mock = {"101": "Juan Pérez", "102": "Ana García"}
            
            if codigo in nombres_mock and clave == "1234":
                st.session_state.usuario_autenticado = nombres_mock[codigo]
                st.success(f"Bienvenido {nombres_mock[codigo]}")
                st.rerun() # Recarga para mostrar el panel principal
            else:
                st.error("Código o contraseña incorrectos")

# --- PANEL PRINCIPAL ---
def main_panel():
    st.sidebar.write(f"👤 **Operador:** {st.session_state.usuario_autenticado}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_autenticado = None
        st.rerun()

    st.title("🚀 Control de Fabricación")
    
    lote_input = st.text_input("Escriba el Lote y presione ENTER")

    if lote_input:
        datos_lotes = {
            "L001": {"Producto": "Ibuprofeno 400mg", "Tren_ID": 3},
            "L002": {"Producto": "Paracetamol 500mg", "Tren_ID": 10}
        }

        if lote_input in datos_lotes:
            lote_info = datos_lotes[lote_input]
            st.info(f"📦 **Producto:** {lote_info['Producto']} | **Tren ID:** {lote_info['Tren_ID']}")
            
            etapas = ["Pesaje", "Mezclado", "Granulado", "Envasado"]
            st.divider()
            
            # --- INTERFAZ DE TIEMPOS ---
            cols = st.columns(len(etapas))
            for i, etapa in enumerate(etapas):
                with cols[i]:
                    st.subheader(etapa)
                    if st.button(f"▶️ Iniciar", key=f"ini_{etapa}"):
                        nuevo_reg = {
                            "Lote": lote_input, "Producto": lote_info['Producto'], 
                            "Operador": st.session_state.usuario_autenticado,
                            "Etapa": etapa, "Evento": "INICIO", "Hora": datetime.now().strftime("%H:%M:%S")
                        }
                        st.session_state.bitacora = pd.concat([st.session_state.bitacora, pd.DataFrame([nuevo_reg])], ignore_index=True)
                        st.toast(f"{etapa} Iniciada")

                    if st.button(f"⏹️ Fin", key=f"fin_{etapa}"):
                        nuevo_reg = {
                            "Lote": lote_input, "Producto": lote_info['Producto'], 
                            "Operador": st.session_state.usuario_autenticado,
                            "Etapa": etapa, "Evento": "FIN", "Hora": datetime.now().strftime("%H:%M:%S")
                        }
                        st.session_state.bitacora = pd.concat([st.session_state.bitacora, pd.DataFrame([nuevo_reg])], ignore_index=True)
                        st.toast(f"{etapa} Finalizada")

            # --- REPORTE ---
            if not st.session_state.bitacora.empty:
                st.divider()
                st.subheader("📊 Historial del Lote")
                df_filtrado = st.session_state.bitacora[st.session_state.bitacora['Lote'] == lote_input]
                st.table(df_filtrado) # Table es más amigable en Tablet que dataframe
        else:
            st.warning("El lote no existe en la base de datos.")

# --- CONTROL DE FLUJO ---
if st.session_state.usuario_autenticado is None:
    login()
else:
    main_panel()
