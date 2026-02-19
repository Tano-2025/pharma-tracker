import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="PharmaTrack Web", layout="wide")

# --- BASE DE DATOS DE OPERADORES ---
# Puedes cambiar esto por un st.selectbox si prefieres que elijan de una lista
USUARIOS = {
    "101": "Juan Pérez",
    "102": "Ana García",
    "103": "Carlos Ruiz",
    "104": "Elena Marín"
}

# --- ESTADO DE LA SESIÓN ---
if 'bitacora' not in st.session_state:
    st.session_state.bitacora = pd.DataFrame(columns=["Lote", "Producto", "Operador", "Etapa", "Evento", "Hora"])

if 'usuario_autenticado' not in st.session_state:
    st.session_state.usuario_autenticado = None

# --- PANTALLA DE ACCESO RÁPIDO ---
if not st.session_state.usuario_autenticado:
    st.title("🏥 Acceso Rápido Pharma")
    st.write("Ingrese su código de operador para comenzar")

    # Opción A: Entrada por teclado numérica (Ideal para Tablets)
    codigo = st.text_input("Código de Operador", placeholder="Ej: 101", help="Ingrese su ID")
    
    # Opción B: También puedes usar un menú desplegable si es más cómodo
    # codigo = st.selectbox("Seleccione su nombre", options=[""] + list(USUARIOS.keys()), format_func=lambda x: USUARIOS.get(x, "Seleccione..."))

    if codigo in USUARIOS:
        nombre = USUARIOS[codigo]
        st.success(f"Identificado como: **{nombre}**")
        if st.button(f"Confirmar ingreso como {nombre}", use_container_width=True):
            st.session_state.usuario_autenticado = nombre
            st.rerun()
    elif codigo != "":
        st.error("Código no reconocido")

# --- PANEL DE PRODUCCIÓN ---
else:
    # Barra lateral simplificada
    st.sidebar.title("👤 Sesión Activa")
    st.sidebar.subheader(st.session_state.usuario_autenticado)
    if st.sidebar.button("❌ Salir / Cambiar Usuario"):
        st.session_state.usuario_autenticado = None
        st.rerun()

    st.title("🚀 Control de Fabricación")
    
    # Campo de Lote
    lote_input = st.text_input("📦 Escanee o escriba el Lote y presione ENTER")

    if lote_input:
        # Datos de prueba
        datos_lotes = {
            "L001": {"Producto": "Ibuprofeno 400mg", "Tren": 3},
            "L002": {"Producto": "Paracetamol 500mg", "Tren": 10}
        }

        if lote_input in datos_lotes:
            info = datos_lotes[lote_input]
            st.success(f"**Producto:** {info['Producto']} | **Tren:** {info['Tren']}")
            
            etapas = ["Pesaje", "Mezclado", "Granulado", "Envasado"]
            st.divider()
            
            # Botonera de etapas
            cols = st.columns(len(etapas))
            for i, etapa in enumerate(etapas):
                with cols[i]:
                    st.markdown(f"### {etapa}")
                    if st.button(f"▶️ INICIAR", key=f"ini_{etapa}", use_container_width=True):
                        nuevo = {
                            "Lote": lote_input, "Producto": info['Producto'], 
                            "Operador": st.session_state.usuario_autenticado,
                            "Etapa": etapa, "Evento": "INICIO", "Hora": datetime.now().strftime("%H:%M:%S")
                        }
                        st.session_state.bitacora = pd.concat([st.session_state.bitacora, pd.DataFrame([nuevo])], ignore_index=True)
                        st.toast(f"{etapa} Iniciada")

                    if st.button(f"⏹️ FIN", key=f"fin_{etapa}", use_container_width=True):
                        nuevo = {
                            "Lote": lote_input, "Producto": info['Producto'], 
                            "Operador": st.session_state.usuario_autenticado,
                            "Etapa": etapa, "Evento": "FIN", "Hora": datetime.now().strftime("%H:%M:%S")
                        }
                        st.session_state.bitacora = pd.concat([st.session_state.bitacora, pd.DataFrame([nuevo])], ignore_index=True)
                        st.toast(f"{etapa} Finalizada")

            # Tabla de registros
            if not st.session_state.bitacora.empty:
                st.divider()
                st.subheader("📊 Historial de hoy")
                st.table(st.session_state.bitacora[st.session_state.bitacora['Lote'] == lote_input])
        else:
            st.warning("Lote no encontrado.")
