import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración inicial de la página
st.set_page_config(page_title="¡Que tacos!", page_icon="🌮", layout="centered")

# --- ESTILOS CSS MODERNOS (MODO UI CLEAN) ---
st.markdown("""
    <style>
    /* Estilo general y fuente más limpia */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Tarjetas contenedoras elegantes */
    div.stForm, div[data-testid="stVerticalBlock"] > div.element-container {
        border-radius: 12px;
    }
    
    /* Botones principales modernos */
    .stButton button[kind="primary"], div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.2s ease-in-out;
    }
    
    /* Métricas con diseño limpio tipo tarjeta */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    /* Encabezados más estilizados */
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIMULACIÓN DE BASE DE DATOS EN MEMORIA ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Bistec en chile morita": {"precio": 25, "activo": True},
        "Longaniza con papas": {"precio": 22, "activo": True},
        "Chicharrón en salsa verde": {"precio": 25, "activo": False}
    }

if 'ventas' not in st.session_state:
    st.session_state.ventas = []

if 'form_key_counter' not in st.session_state:
    st.session_state.form_key_counter = 0

# --- SISTEMA DE AUTENTICACIÓN / ROLES ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'rol_usuario' not in st.session_state:
    st.session_state.rol_usuario = None

# TÍTULO PRINCIPAL
st.title("🌮 ¡Que tacos!")
st.caption("Sistema inteligente de control de ventas y administración")

# Si no ha iniciado sesión, mostramos la pantalla de acceso
if not st.session_state.autenticado:
    st.markdown("### 🔐 Acceso al Sistema")
    
    with st.form("form_login"):
        rol_seleccionado = st.selectbox("Selecciona tu rol", ["Celular (Cajero / Ventas)", "Panel de Dueño (Reportes y Menú)"])
        
        password = ""
        if rol_seleccionado == "Panel de Dueño (Reportes y Menú)":
            password = st.text_input("Contraseña de Dueño", type="password")
            
        btn_entrar = st.form_submit_button("Entrar al Sistema 🚀", use_container_width=True)
        
        if btn_entrar:
            if rol_seleccionado == "Panel de Dueño (Reportes y Menú)":
                if password == "1234":  
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = "dueño"
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")
            else:
                st.session_state.autenticado = True
                st.session_state.rol_usuario = "cajero"
                st.rerun()

# Si ya inició sesión, mostramos la aplicación según su rol
else:
    # BARRA SUPERIOR DE SESIÓN
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        st.info(f"👤 Sesión activa: **{st.session_state.rol_usuario.upper()}**")
    with col_s2:
        if st.button("🔒 Salir", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.rol_usuario = None
            st.rerun()
    
    st.markdown("---")

    # ==========================================
    # VISTA 1: CAJERO (MODERNO Y RÁPIDO)
    # ==========================================
    if st.session_state.rol_usuario == "cajero":
        st.header("📲 Terminal de Venta")
        st.markdown("Selecciona la cantidad de tacos para armar la orden:")

        guisados_activos = {g: info for g, info in st.session_state.menu.items() if info["activo"]}

        if not guisados_activos:
            st.warning("⚠ No hay guisados activos hoy. Pídele al administrador que active el menú.")
        else:
            cantidades = {}
            total_orden_previo = 0

            for guisado, info in guisados_activos.items():
                with st.container():
                    col_g, col_p, col_c = st.columns([2, 1, 1])
                    with col_g:
                        st.markdown(f"**{guisado}**")
                    with col_p:
                        st.markdown(f"<span style='color: #64748b;'>${info['precio']} c/u</span>", unsafe_allow_html=True)
                    with col_c:
                        cantidades[guisado] = st.number_input(
                            "Cant", min_value=0, max_value=50, value=0, 
                            key=f"cajero_{guisado}", label_visibility="collapsed"
                        )
                st.divider()
                total_orden_previo += cantidades[guisado] * info['precio']

            # Resumen flotante de cobro
            st.markdown(f"""
                <div style="background-color: #f1f5f9; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #0f172a;">Total a cobrar: ${total_orden_previo} MXN</h3>
                </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Cobrar y Registrar Venta", type="primary", use_container_width=True):
                items_vendidos = {g: cant for g, cant in cantidades.items() if cant > 0}
                
                if not items_vendidos:
                    st.warning("⚠️ Selecciona al menos un taco para registrar la venta.")
                else:
                    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    for guisado, cantidad in items_vendidos.items():
                        precio_unitario = st.session_state.menu[guisado]["precio"]
                        total_linea = precio_unitario * cantidad
                        
                        st.session_state.ventas.append({
                            "Hora": hora_actual,
                            "Guisado": guisado,
                            "Cantidad": cantidad,
                            "Total": total_linea
                        })
                        
                    st.success(f"¡Venta registrada con éxito! Total cobrado: ${total_orden_previo} MXN")

        if st.session_state.ventas:
            st.markdown("---")
            st.subheader("📋 Ventas Recientes")
            df_ventas = pd.DataFrame(st.session_state.ventas)
            st.dataframe(df_ventas.tail(6), use_container_width=True, hide_index=True)

    # ==========================================
    # VISTA 2: PANEL DE DUEÑO (MODERNO)
    # ==========================================
    elif st.session_state.rol_usuario == "dueño":
        st.header("📊 Panel de Control")
        
        tab1, tab2 = st.tabs(["📈 Reportes", "⚙️ Gestión de Menú"])

        with tab1:
            st.subheader("Resumen General")
            if not st.session_state.ventas:
                st.info("Aún no hay ventas registradas hoy.")
            else:
                df_ventas = pd.DataFrame(st.session_state.ventas)
                
                total_dinero = df_ventas["Total"].sum()
                total_tacos = df_ventas["Cantidad"].sum()
                
                col1, col2 = st.columns(2)
                col1.metric("Dinero Total", f"${total_dinero} MXN")
                col2.metric("Tacos Vendidos", total_tacos)
                
                st.markdown("### Guisados Más Vendidos")
                ventas_por_guisado = df_ventas.groupby("Guisado")["Cantidad"].sum()
                st.bar_chart(ventas_por_guisado)

                st.markdown("---")
                if st.button("🗑️️ Borrar Historial de Ventas", type="secondary"):
                    st.session_state.ventas = []
                    st.success("¡Historial de ventas borrado con éxito!")
                    st.rerun()

        with tab2:
            st.subheader("Modificar Precios y Disponibilidad")
            
            with st.form("form_editar_menu"):
                nuevos_precios = {}
                nuevos_estados = {}
                
                for guisado, info in st.session_state.menu.items():
                    st.markdown(f"**🌮 {guisado}**")
                    col_p, col_a = st.columns(2)
                    with col_p:
                        nuevos_precios[guisado] = st.number_input(
                            f"Precio de {guisado}", 
                            min_value=0, 
                            value=info["precio"], 
                            key=f"precio_{guisado}"
                        )
                    with col_a:
                        nuevos_estados[guisado] = st.checkbox(
                            "¿Disponible hoy?", 
                            value=info["activo"], 
                            key=f"activo_{guisado}"
                        )
                    st.divider()
                    
                guardar_cambios = st.form_submit_button("Guardar Cambios 💾", use_container_width=True)
                
                if guardar_cambios:
                    for guisado in st.session_state.menu:
                        st.session_state.menu[guisado]["precio"] = nuevos_precios[guisado]
                        st.session_state.menu[guisado]["activo"] = nuevos_estados[guisado]
                    st.success("¡Menú y precios actualizados correctamente!")

            st.markdown("---")
            st.subheader("➕ Agregar Nuevo Guisado")
            
            form_key = f"form_agregar_guisado_{st.session_state.form_key_counter}"
            with st.form(form_key):
                nuevo_nombre = st.text_input("Nombre del nuevo guisado (ej. Suadero)")
                nuevo_precio = st.number_input("Precio inicial ($ MXN)", min_value=0, value=25)
                btn_agregar = st.form_submit_button("Agregar al Menú 🚀", use_container_width=True)
                
                if btn_agregar:
                    if nuevo_nombre.strip():
                        if nuevo_nombre in st.session_state.menu:
                            st.warning("⚠ Ese guisado ya existe en el menú.")
                        else:
                            st.session_state.menu[nuevo_nombre] = {"precio": nuevo_precio, "activo": True}
                            st.session_state.form_key_counter += 1
                            st.success(f"¡Guisado '{nuevo_nombre}' agregado con éxito!")
                            st.rerun()
                    else:
                        st.error("❌ Escribe un nombre válido para el guisado.")

            st.markdown("---")
            st.subheader("🗑️ Eliminar Guisado")
            if st.session_state.menu:
                guisado_a_borrar = st.selectbox("Selecciona el guisado que deseas eliminar", list(st.session_state.menu.keys()))
                if st.button("Eliminar Platillo ❌", use_container_width=True):
                    del st.session_state.menu[guisado_a_borrar]
                    st.success(f"¡Platillo '{guisado_a_borrar}' eliminado del menú!")
                    st.rerun()
            else:
                st.info("No hay guisados en el menú para eliminar.")
