import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración inicial de la página
st.set_page_config(page_title="Control Taquería de Guisados", page_icon="🌮", layout="centered")

# --- SIMULACIÓN DE BASE DE DATOS EN MEMORIA (Luego la conectamos a la nube) ---
if 'menu' not in st.session_state:
    st.session_state.menu = {
        "Bistec en chile morita": {"precio": 25, "activo": True},
        "Longaniza con papas": {"precio": 22, "activo": True},
        "Chicharrón en salsa verde": {"precio": 25, "activo": False}
    }

if 'ventas' not in st.session_state:
    st.session_state.ventas = []

# --- TÍTULO PRINCIPAL ---
st.title("🌮 Control de Ventas - Taquería")

# Menú lateral para elegir la vista
modo = st.sidebar.selectbox("Selecciona la Vista", ["Celular (Cajero / Ventas)", "Panel de Dueño (Reportes y Menú)"])

# ==========================================
# VISTA 1: CELULAR - REGISTRO RÁPIDO DE VENTAS
# ==========================================
if modo == "Celular (Cajero / Ventas)":
    st.header("📲 Terminal de Venta")
    st.write("Selecciona el guisado y la cantidad vendida:")

    # Filtramos solo los guisados activos del día
    guisados_activos = [g for g, info in st.session_state.menu.items() if info["activo"]]

    if not guisados_activos:
        st.warning("⚠ No hay guisados activos hoy. Pídele al administrador que actualice el menú.")
    else:
        with st.form("form_venta"):
            guisado_elegido = st.selectbox("Guisado", guisados_activos)
            cantidad = st.number_input("Cantidad de tacos / órdenes", min_value=1, max_value=50, value=1)
            
            # Botón de registro
            enviar = st.form_submit_button("Registrar Venta 🚀")
            
            if enviar:
                precio_unitario = st.session_state.menu[guisado_elegido]["precio"]
                total_venta = precio_unitario * cantidad
                hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Guardamos en la lista de ventas
                st.session_state.ventas.append({
                    "Hora": hora_actual,
                    "Guisado": guisado_elegido,
                    "Cantidad": cantidad,
                    "Total": total_venta
                })
                st.success(f"¡Venta registrada! {cantidad}x {guisado_elegido} (${total_venta} MXN)")

    # Mostrar ventas recientes de la sesión para control rápido
    if st.session_state.ventas:
        st.subheader("📋 Ventas Recientes de Hoy")
        df_ventas = pd.DataFrame(st.session_state.ventas)
        st.dataframe(df_ventas.tail(5), use_container_width=True)

# ==========================================
# VISTA 2: PANEL DE DUEÑO (REPORTES Y MENÚ)
# ==========================================
elif modo == "Panel de Dueño (Reportes y Menú)":
    st.header("📊 Panel de Control y Administración")
    
    # Pestañas dentro del panel de dueño
    tab1, tab2 = st.tabs(["📈 Gráficas y Reportes", "⚙️ Modificar Menú y Precios"])

    with tab1:
        st.subheader("Resumen de Ventas")
        if not st.session_state.ventas:
            st.info("Aún no hay ventas registradas hoy.")
        else:
            df_ventas = pd.DataFrame(st.session_state.ventas)
            
            # Métricas rápidas
            total_dinero = df_ventas["Total"].sum()
            total_tacos = df_ventas["Cantidad"].sum()
            
            col1, col2 = st.columns(2)
            col1.metric("Dinero Total Vendido", f"${total_dinero} MXN")
            col2.metric("Total de Unidades Vendidas", total_tacos)
            
            # Gráfica visual de los más vendidos
            st.markdown("### Guisados Más Vendidos")
            ventas_por_guisado = df_ventas.groupby("Guisado")["Cantidad"].sum()
            st.bar_chart(ventas_por_guisado)

    with tab2:
        st.subheader("Configuración del Menú y Precios")
        st.write("Modifica los precios o activa/desactiva los platillos y presiona el botón inferior para aplicar los cambios.")
        
        # Usamos un formulario para asegurar que los cambios se guarden solo al dar clic en el botón
        with st.form("form_editar_menu"):
            nuevos_datos = {}
            
            for guisado, info in st.session_state.menu.items():
                st.markdown(f"### 🍲 {guisado}")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    activo_ing = st.checkbox("¿Disponible hoy?", value=info["activo"], key=f"chk_{guisado}")
                with col_b:
                    precio_ing = st.number_input("Precio ($ MXN)", min_value=0, value=info["precio"], key=f"prc_{guisado}")
                
                nuevos_datos[guisado] = {"precio": precio_ing, "activo": activo_ing}
                st.divider()
                
            # Botón exclusivo para confirmar la actualización
            guardar_menu = st.form_submit_button("💾 Guardar Cambios del Menú")
            
            if guardar_menu:
                st.session_state.menu = nuevos_datos
                st.success("¡Menú y precios actualizados exitosamente! Ya se reflejan en la terminal.")