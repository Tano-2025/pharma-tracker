import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuración para Tablet
st.set_page_config(page_title="PharmaTrack Dinámico", layout="wide")

# --- FUNCIONES DE CARGA DE DATOS ---
def cargar_datos_produccion():
    """Lee el CSV de lotes y lo convierte en un diccionario para búsqueda rápida"""
    if os.path.exists('datos_produccion.csv'):
        try:
            df = pd.read_csv('datos_produccion.csv')
            # Limpieza básica: quitar espacios en blanco
            df.columns = df.columns.str.strip()
            # Convertir a diccionario: { 'L001': {'Producto': '...', 'Tren_ID': 3}, ... }
            return df.set_index('Lote').to_dict('index')
        except Exception as e:
            st.error(f"Error al leer datos_produccion.csv: {e}")
            return {}
    else:
        st.warning("⚠️ Archivo 'datos_produccion.csv' no encontrado.")
        return {}

# --- INICIALIZACIÓN DE ESTADOS ---
if 'bitacora' not in st.session_state:
    st.session_state.bitacora = pd.DataFrame(columns=["Lote", "Producto", "Operador", "Etapa", "Evento", "Hora"])

if 'usuario_autenticado' not in st.session_state:
    st.session_state.usuario_autenticado = None

# --- ACCESO POR CÓDIGO (SIN CONTRASEÑA) ---
USUARIOS = {"101": "Juan Pérez", "102": "Ana García", "103": "Carlos Ruiz"}

if not st.session_state.usuario_autenticado:
    st.title("🏥 Acceso de Operador")
    codigo = st.text_input("Ingrese su Código de Operador", key="login_code")
    
    if codigo in USUARIOS:
        nombre = USUARIOS[codigo]
        if st.button(f"Entrar como {nombre}", use_container_width=True):
            st.session_state.usuario_autenticado = nombre
            st.rerun()
    elif codigo:
        st.error("Código no válido")

# --- PANEL DE CONTROL ---
else:
    st.sidebar.title(f"👤 {st.session_state.usuario_autenticado}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_autenticado = None
        st.rerun()

    st.title("🚀 Control de Fabricación")

    # CARGA DINÁMICA: Se vuelve a leer si el usuario interactúa
    lotes_db = cargar_datos_produccion()
    
    # Input de Lote
    lote_input = st.text_input("📦 Escanee o escriba el Lote y presione ENTER").strip()

    if lote_input:
        if lote_input in lotes_db:
            info = lotes_db[lote_input]
            producto = info.get('Producto', 'Desconocido')
            tren = info.get('Tren_ID', 'N/A')
            
            # Encabezado dinámico
            st.success(f"✅ **Lote Identificado:** {lote_input}")
            
            # Uso de métricas para mejor visualización en Tablet
            m1, m2 = st.columns(2)
            m1.metric("Producto", producto)
            m2.metric("Tren de Producción", f"ID: {tren}")

            st.divider()
            
            # --- BOTONERA DE ETAPAS ---
            etapas = ["Pesaje", "Mezclado", "Granulado", "Envasado"]
            cols = st.columns(len(etapas))
            
            for i, etapa in enumerate(etapas):
                with cols[i]:
                    st.subheader(etapa)
                    if st.button(f"▶️ INICIAR", key=f"ini_{etapa}", use_container_width=True):
                        nuevo = {
                            "Lote": lote_input, "Producto": producto, 
                            "Operador": st.session_state.usuario_autenticado,
                            "Etapa": etapa, "Evento": "INICIO", 
                            "Hora": datetime.now().strftime("%H:%M:%S")
                        }
                        st.session_state.bitacora = pd.concat([st.session_state.bitacora, pd.DataFrame([nuevo])], ignore_index=True)
                        st.toast(f"Inicio: {etapa}")

                    if st.button(f"⏹️ FIN", key=f"fin_{etapa}", use_container_width=True):
                        nuevo = {
                            "Lote": lote_input, "Producto": producto, 
                            "Operador": st.session_state.usuario_autenticado,
                            "Etapa": etapa, "Evento": "FIN", 
                            "Hora": datetime.now().strftime("%H:%M:%S")
                        }
                        st.session_state.bitacora = pd.concat([st.session_state.bitacora, pd.DataFrame([nuevo])], ignore_index=True)
                        st.toast(f"Fin: {etapa}")

            # --- REGISTRO VISUAL ---
            if not st.session_state.bitacora.empty:
                st.divider()
                st.subheader("📊 Historial del Lote")
                # Filtramos la bitácora para mostrar solo lo relacionado al lote actual
                df_lote = st.session_state.bitacora[st.session_state.bitacora['Lote'] == lote_input]
                st.table(df_lote[["Etapa", "Evento", "Hora", "Operador"]])
        else:
            st.warning(f"El lote **{lote_input}** no existe en el archivo datos_produccion.csv")

    # Botón de refresco manual de base de datos (Opcional)
    if st.sidebar.button("🔄 Actualizar Lotes (CSV)"):
        st.rerun()
