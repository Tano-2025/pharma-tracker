import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Configuración de la página para Tablet
st.set_page_config(page_title="PharmaTrack Web", layout="wide")

# --- SIMULACIÓN DE BASE DE DATOS (En memoria para el ejemplo) ---
# En una versión real, esto leería los CSV que subas
if 'bitacora' not in st.session_state:
    st.session_state.bitacora = pd.DataFrame(columns=["Lote", "Producto", "Operador", "Etapa", "Evento", "Hora"])

if 'usuario_autenticado' not in st.session_state:
    st.session_state.usuario_autenticado = None

# --- LÓGICA DE LOGIN ---
if not st.session_state.usuario_autenticado:
    st.title("🔐 Ingreso al Sistema Pharma")
    
    col_user, col_pass = st.columns(2)
    with col_user:
        codigo = st.text_input("Código de Usuario")
        # Simulación de búsqueda en listas.csv
        nombres_mock = {"101": "Juan Pérez", "102": "Ana García"}
        if codigo in nombres_mock:
            st.info(f"Usuario: {nombres_mock[codigo]}")
            
    with col_pass:
        clave = st.text_input("Contraseña", type="password")

    if st.button("Ingresar", use_container_width=True):
        if codigo in nombres_mock and clave == "1234": # Validación simple
            st.session_state.usuario_autenticado = nombres_mock[codigo]
            st.rerun()
        else:
            st.error("Credenciales inválidas")

# --- PANEL PRINCIPAL DE PRODUCCIÓN ---
else:
    st.sidebar.write(f"👤 Operador: {st.session_state.usuario_autenticado}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_autenticado = None
        st.rerun()

    st.title("🚀 Control de Fabricación")
    
    lote_input = st.text_input("Escriba el Lote y presione ENTER")

    if lote_input:
        # Datos de prueba (Simulando datos_produccion.csv)
        datos_lotes = {
            "L001": {"Producto": "Ibuprofeno 400mg", "Tren_ID": 3},
            "L002": {"Producto": "Paracetamol 500mg", "Tren_ID": 10}
        }

        if lote_input in datos_lotes:
            lote_info = datos_lotes[lote_input]
            st.success(f"📦 Producto: {lote_info['Producto']} | Tren ID: {lote_info['Tren_ID']}")
            
            es_secuencial = lote_info['Tren_ID'] > 5
            etapas = ["Pesaje", "Mezclado", "Granulado", "Envasado"]
            
            st.divider()
            
            # --- INTERFAZ DE TIEMPOS ---
            cols = st.columns(len(etapas))
            
            for i, etapa in enumerate(etapas):
                with cols[i]:
                    st.subheader(etapa)
                    if st.button(f"▶️ Iniciar {etapa}", key=f"ini_{etapa}"):
                        nuevo_reg = {"Lote": lote_input, "Producto": lote_info['Producto'], 
                                     "Operador": st.session_state.usuario_autenticado,
                                     "Etapa": etapa, "Evento": "INICIO", "Hora": datetime.now()}
                        st.session_state.bitacora = pd.concat([st.session_state.bitacora, pd.DataFrame([nuevo_reg])])
                        st.toast(f"{etapa} Iniciada")

                    if st.button(f"⏹️ Fin {etapa}", key=f"fin_{etapa}"):
                        nuevo_reg = {"Lote": lote_input, "Producto": lote_info['Producto'], 
                                     "Operador": st.session_state.usuario_autenticado,
                                     "Etapa": etapa, "Evento": "FIN", "Hora": datetime.now()}
                        st.session_state.bitacora = pd.concat([st.session_state.bitacora, pd.DataFrame([nuevo_reg])])
                        st.toast(f"{etapa} Finalizada")

            # --- REPORTE EN TIEMPO REAL ---
            if not st.session_state.bitacora.empty:
                st.divider()
                st.subheader("📊 Historial del Lote")
                st.dataframe(st.session_state.bitacora[st.session_state.bitacora['Lote'] == lote_input])

        else:
            st.warning("Lote no encontrado.")
