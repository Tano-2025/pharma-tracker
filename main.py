import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="PharmaTrack - Acceso", layout="centered")

# Simulación de base de datos de usuarios (Esto podría venir de un CSV)
USUARIOS_DB = {
    "101": {"nombre": "Juan Pérez", "clave": "1234"},
    "102": {"nombre": "Ana García", "clave": "abcd"}
}

# --- INICIALIZACIÓN DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'usuario_nombre' not in st.session_state:
    st.session_state.usuario_nombre = ""

# --- FUNCIÓN DE LOGIN ---
def login():
    st.title("🔐 Control de Acceso Pharma")
    st.markdown("---")
    
    # Usamos un formulario para agrupar los inputs
    with st.form("formulario_login"):
        user_code = st.text_input("Código de Operador", placeholder="Ej: 101")
        password = st.text_input("Contraseña", type="password")
        boton_entrar = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
        
        if boton_entrar:
            if user_code in USUARIOS_DB and USUARIOS_DB[user_code]["clave"] == password:
                st.session_state.autenticado = True
                st.session_state.usuario_nombre = USUARIOS_DB[user_code]["nombre"]
                st.success(f"Bienvenido, {st.session_state.usuario_nombre}")
                st.rerun() # Recarga la página para mostrar el contenido
            else:
                st.error("⚠️ Código o contraseña incorrectos. Intente de nuevo.")

# --- PANEL PRINCIPAL (Solo se ve si está autenticado) ---
def panel_principal():
    # Barra lateral con info de usuario
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3022/3022215.png", width=100)
    st.sidebar.write(f"🟢 **Operador:** {st.session_state.usuario_nombre}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # Contenido de tu aplicación original
    st.title("🚀 Control de Fabricación")
    st.info(f"Sesión iniciada a las: {datetime.now().strftime('%H:%M')}")
    
    # Aquí continuaría el resto de tu código (Lotes, Etapas, etc.)
    lote = st.text_input("Ingrese número de lote para comenzar:")
    if lote:
        st.write(f"Trabajando en el lote: **{lote}**")

# --- FLUJO DEL PROGRAMA ---
if not st.session_state.autenticado:
    login()
else:
    panel_principal()
