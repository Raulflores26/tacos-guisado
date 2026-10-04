import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuración inicial de la página
st.set_page_config(page_title="¡Que tacos!", page_icon="🌮", layout="centered")

# --- ARCHIVO DE PERSISTENCIA LOCAL ---
ARCHIVO_VENTAS = "ventas_historico.csv"

def cargar_ventas():
    if os.path.exists(ARCHIVO_VENTAS):
        try:
            df = pd.read_csv(ARCHIVO_VENTAS)
            # Asegurar compatibilidad si el archivo antiguo no tenía estas columnas
            for col in ["EfectivoRecibido", "Cambio"]:
                if col not in df.columns:
                    df[col] = 0.0
            return df
        except Exception:
            return pd.DataFrame(columns=["Fecha", "Hora", "Guisado", "Cantidad", "Total", "EfectivoRecibido", "Cambio"])
    else:
        return pd.DataFrame(columns=["Fecha", "Hora", "Guisado", "Cantidad", "Total", "EfectivoRecibido", "Cambio"])

def guardar_venta_en_csv(nueva_venta):
    df_actual = cargar_ventas()
    df_nueva_fila = pd.DataFrame([nueva_venta])
    df_combinado = pd.concat([df_actual, df_nueva_fila], ignore_index=True)
    df_combinado.to_csv(ARCHIVO_VENTAS, index=False)

# --- ESTILOS CSS MODERNOS (MODO UI CLEAN) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    div.stForm, div[data-testid="stVerticalBlock"] > div.element-container {
        border-radius: 12px;
    }
    .stButton button[kind="primary"], div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIMULACIÓN DE MENÚ EN MEMORIA ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Bistec en chile morita": {"precio": 25, "activo": True},
        "Longaniza con papas": {"precio": 22, "activo": True},
        "Chicharrón en salsa verde": {"precio": 25, "activo": False}
    }

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

            # Resumen y cálculo de cambio
            if total_orden_previo > 0:
                st.markdown(f"""
                    <div style="background-color: #f1f5f9; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px;">
                        <h3 style="margin: 0; color: #0f172a;">Total a cobrar: ${total_orden_previo} MXN</h3>
                    </div>
                """, unsafe_allow_html=True)

                pago_con = st.number_input("💵 ¿Con cuánto paga el cliente? ($ MXN)", min_value=0.0, step=10.0, value=float(total_orden_previo))
                
                if pago_con < total_orden_previo:
                    st.error("⚠️ El monto recibido es menor al total de la orden.")
                    cambio = 0
                else:
                    cambio = pago_con - total_orden_previo
                    st.success(f"🪙 **Cambio a regresar:** ${cambio:.2f} MXN")

                if st.button("🚀 Cobrar y Registrar Venta", type="primary", use_container_width=True):
                    if pago_con < total_orden_previo:
                        st.warning("⚠️ Ingresa un monto de pago válido.")
                    else:
                        items_vendidos = {g: cant for g, cant in cantidades.items() if cant > 0}
                        
                        if not items_vendidos:
                            st.warning("⚠️ Selecciona al menos un taco para registrar la venta.")
                        else:
                            fecha_actual = datetime.now().strftime("%Y-%m-%d")
                            hora_actual = datetime.now().strftime("%H:%M:%S")
                            
                            for guisado, cantidad in items_vendidos.items():
                                precio_unitario = st.session_state.menu[guisado]["precio"]
                                total_linea = precio_unitario * cantidad
                                
                                nueva_venta = {
                                    "Fecha": fecha_actual,
                                    "Hora": hora_actual,
                                    "Guisado": guisado,
                                    "Cantidad": cantidad,
                                    "Total": total_linea,
                                    "EfectivoRecibido": pago_con,
                                    "Cambio": cambio
                                }
                                guardar_venta_en_csv(nueva_venta)
                                
                            st.success(f"¡Venta registrada con éxito! Cambio entregado: ${cambio:.2f} MXN")

        df_ventas_actual = cargar_ventas()
        if not df_ventas_actual.empty:
            st.markdown("---")
            st.subheader("📋 Ventas Recientes")
            st.dataframe(df_ventas_actual.tail(6), use_container_width=True, hide_index=True)

    # ==========================================
    # VISTA 2: PANEL DE DUEÑO (REPORTES Y MENÚ)
    # ==========================================
    elif st.session_state.rol_usuario == "dueño":
        st.header("📊 Panel de Control")
        
        tab1, tab2, tab3 = st.tabs(["📈 Reportes y Fechas", "💵 Corte de Dinero Diario", "⚙️ Gestión de Menú"])

        with tab1:
            st.subheader("Resumen e Historial por Periodo")
            df_ventas = cargar_ventas()
            
            if df_ventas.empty:
                st.info("Aún no hay ventas registradas en el sistema.")
            else:
                tipo_filtro = st.radio("Filtrar reporte por:", ["Día Específico", "Mes Completo", "Histórico Total"], horizontal=True)
                
                df_filtrado = df_ventas.copy()
                
                if tipo_filtro == "Día Específico":
                    fechas_disponibles = sorted(df_ventas["Fecha"].unique(), reverse=True)
                    fecha_elegida = st.selectbox("Selecciona la fecha", fechas_disponibles)
                    df_filtrado = df_ventas[df_ventas["Fecha"] == fecha_elegida]
                    
                elif tipo_filtro == "Mes Completo":
                    df_ventas["Mes"] = df_ventas["Fecha"].astype(str).str.slice(0, 7)
                    meses_disponibles = sorted(df_ventas["Mes"].unique(), reverse=True)
                    mes_elegido = st.selectbox("Selecciona el mes (YYYY-MM)", meses_disponibles)
                    df_filtrado = df_ventas[df_ventas["Mes"] == mes_elegido]

                st.markdown("---")
                
                if df_filtrado.empty:
                    st.warning("No hay ventas registradas para el filtro seleccionado.")
                else:
                    total_dinero = df_filtrado["Total"].sum()
                    total_tacos = df_filtrado["Cantidad"].sum()
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Dinero Total", f"${total_dinero} MXN")
                    col2.metric("Tacos Vendidos", total_tacos)
                    
                    st.markdown("### Guisados Más Vendidos en este periodo")
                    ventas_por_guisado = df_filtrado.groupby("Guisado")["Cantidad"].sum()
                    st.bar_chart(ventas_por_guisado)

                    st.markdown("---")
                    with st.expander("Ver detalle completo de transacciones"):
                        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

        with tab2:
            st.subheader("💵 Ingresos Totales por Día (Corte Diario)")
            df_ventas = cargar_ventas()
            
            if df_ventas.empty:
                st.info("Aún no hay registros de dinero para mostrar.")
            else:
                df_corte_diario = df_ventas.groupby("Fecha").agg(
                    Dinero_Reunido=("Total", "sum"),
                    Total_Tacos_Vendidos=("Cantidad", "sum")
                ).reset_index()
                
                df_corte_diario = df_corte_diario.sort_values(by="Fecha", ascending=False)
                
                hoy_str = datetime.now().strftime("%Y-%m-%d")
                dinero_hoy = df_corte_diario.loc[df_corte_diario["Fecha"] == hoy_str, "Dinero_Reunido"]
                total_hoy_val = dinero_hoy.values[0] if not dinero_hoy.empty else 0
                
                st.metric("💰 Dinero Reunido Hoy", f"${total_hoy_val} MXN")
                st.markdown("---")
                
                st.markdown("### 📊 Gráfica de Ingresos Diarios")
                chart_data = df_corte_diario.set_index("Fecha")["Dinero_Reunido"]
                st.bar_chart(chart_data)
                
                st.markdown("### 📋 Tabla Histórica de Cortes Diarios")
                st.dataframe(df_corte_diario, use_container_width=True, hide_index=True)

            st.markdown("---")
            if st.button("🗑️ Borrar Todo el Historial Registrado", type="secondary"):
                if os.path.exists(ARCHIVO_VENTAS):
                    os.remove(ARCHIVO_VENTAS)
                st.success("¡Historial completo borrado con éxito!")
                st.rerun()

        with tab3:
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
