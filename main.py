import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="PharmaTrack Web", layout="wide", initial_sidebar_state="collapsed")

# 2. FUNCIONES DE CARGA DE DATOS (LECTURA DINÁMICA)
def cargar_lotes():
    """Lee el CSV detectando automáticamente si usa comas o puntos y comas"""
    archivo = 'datos_produccion.csv'
    if os.path.exists(archivo):
        try:
            # engine='python' y sep=None permiten detectar el separador automáticamente
            # on_bad_lines='skip' evita el error "Expected X fields, saw Y"
            df = pd.read_csv(archivo, sep=None, engine='python', on_bad_lines='skip')
            
            # Limpiar espacios en los nombres de columnas
            df.columns = df.columns.str.strip()
            
            # Validar columnas necesarias
            if 'Lote' in df.columns:
                return df.set_index('Lote').to_dict('index')
            else:
                st.error("El CSV debe tener una columna llamada 'Lote'")
                return {}
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            return {}
    else:
        st.warning(f"No se encontró el archivo {archivo}")
        return {}

# 3. INICIALIZACIÓN DE ESTADOS (MEMORIA DE SESIÓN)
if 'bitacora' not in st.session_state:
    st.session_state.bitacora = pd.DataFrame(columns=["Lote", "Producto", "Operador", "Etapa", "Evento", "Hora"])

if 'usuario_autenticado' not in st.session_state:
    st.session_state.usuario_autenticado = None

# --- LISTA DE OPERADORES (Puedes mover esto a otro CSV si deseas) ---
USUARIOS = {
    "101": "Juan Pérez",
    "102": "Ana García",
    "103": "Carlos Ruiz",
    "104": "Elena Marín"
}

# 4. LÓGICA DE ACCESO (SIN CONTRASEÑA)
if not st.session_state.usuario_autenticado:
    st.title("🔐 Acceso al Sistema Pharma")
    st.write("Ingrese su código de operador para comenzar.")
    
    codigo = st.text_input("Código de Operador", key="login_id")
    
    if codigo in USUARIOS:
        nombre = USUARIOS[codigo]
        st.success(f"Operador detectado: **{nombre}**")
        if st.button("CONFIRMAR INGRESO", use_container_width=True):
            st.session_state.usuario_autenticado = nombre
            st.rerun()
    elif codigo != "":
        st.error("Código no registrado.")

# 5. PANEL DE CONTROL PRINCIPAL
else:
    # Barra lateral
    st.sidebar.title(f"👤 {st.session_state.usuario_autenticado}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_autenticado = None
        st.rerun()

    st.title("🚀 Control de Fabricación")
    
    # Carga dinámica del CSV
    lotes_db = cargar_lotes()
    
    # Input del Lote
    lote_input = st.text_input("📦 Ingrese o escanee el LOTE", placeholder="Ej: L001").strip()

    if lote_input:
        if lote_input in lotes_db:
            # Extraer datos del CSV
            info = lotes_db[lote_input]
            # Usamos .get() para evitar errores si la columna no existe exactamente igual
            producto = info.get('Producto', 'Nombre no encontrado')
            tren_id = info.get('Tren_ID', 'N/A')
            
            # Mostrar información del producto
            c1, c2 = st.columns(2)
            with c1:
                st.metric("PRODUCTO", producto)
            with c2:
                st.metric("TREN ID", tren_id)

            st.divider()
            
            # --- INTERFAZ DE TIEMPOS (ETAPAS) ---
            etapas = ["Pesaje", "Mezclado", "Granulado", "Envasado"]
            cols = st.columns(len(etapas))
            
            for i, etapa in enumerate(etapas):
                with cols[i]:
                    st.subheader(etapa)
                    
                    # Botón de Inicio
                    if st.button(f"▶️ INICIAR", key=f"ini_{etapa}", use_container_width=True):
                        nuevo_reg = {
                            "Lote": lote_input, "Producto": producto, 
                            "Operador": st.session_state.usuario_autenticado,
                            "Etapa": etapa, "Evento": "INICIO", 
                            "Hora": datetime.now().strftime("%H:%M:%S")
                        }
                        st.session_state.bitacora = pd.concat([st.session_state.bitacora, pd.DataFrame([nuevo_reg])], ignore_index=True)
                        st.toast(f"{etapa} iniciada")

                    # Botón de Fin
                    if st.button(f"⏹️ FINALIZAR", key=f"fin_{etapa}", use_container_width=True):
                        nuevo_reg = {
                            "Lote": lote_input, "Producto": producto, 
                            "Operador": st.session_state.usuario_autenticado,
                            "Etapa": etapa, "Evento": "FIN", 
                            "Hora": datetime.now().strftime("%H:%M:%S")
                        }
                        st.session_state.bitacora = pd.concat([st.session_state.bitacora, pd.DataFrame([nuevo_reg])], ignore_index=True)
                        st.toast(f"{etapa} finalizada")

            # --- VISUALIZACIÓN DE RESULTADOS ---
            if not st.session_state.bitacora.empty:
                st.divider()
                st.subheader(f"📊 Historial del Lote: {lote_input}")
                # Mostrar solo registros del lote actual
                df_filtrado = st.session_state.bitacora[st.session_state.bitacora['Lote'] == lote_input]
                st.table(df_filtrado[["Etapa", "Evento", "Hora", "Operador"]])
                
        else:
            st.warning(f"El lote **{lote_input}** no se encuentra en el archivo de producción.")

    # Botón para refrescar la base de datos manualmente
    if st.sidebar.button("🔄 Recargar base de datos"):
        st.rerun()
