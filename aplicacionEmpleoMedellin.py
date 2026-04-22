#Importamos las librerias necesarias
import streamlit as st
import pandas as pd
from pandasql import sqldf
import plotly.express as px

#Vamos a crar el dataframe con los datos de empleo en Medellín
df_empleo = pd.read_csv('empleo_medellin.csv', sep=',')

# Consulta 1: Ingreso promedio por nivel_estudio
df_ingreso_promedio_nivel_estudio = sqldf("SELECT nivel_estudio, AVG(ingreso_mensual) as ingreso_promedio FROM df_empleo GROUP BY nivel_estudio")

# Consulta 2: Cuántas personas menores de edad trabajan
df_menores_trabajando = sqldf("SELECT COUNT(*) as cantidad_menores_trabajando FROM df_empleo WHERE edad < 18 AND trabaja = 'Sí'")

# Consulta 3: Distribución del trabajo por estrato
df_distribucion_trabajo_estrato = sqldf("SELECT estrato, COUNT(*) as cantidad FROM df_empleo WHERE trabaja = 'Sí' GROUP BY estrato")

# Consulta 4: Distribución si el sueldo es el indicado para vivir bien (>= 2500000)
df_distribucion_vivir_bien = sqldf("SELECT CASE WHEN ingreso_mensual >= 2500000 THEN 'Vivir bien' ELSE 'No vivir bien' END as categoria, COUNT(*) as cantidad FROM df_empleo GROUP BY categoria")

# Consulta 5a: Distribución por comuna
df_distribucion_comuna = sqldf("SELECT comuna, COUNT(*) as cantidad FROM df_empleo WHERE trabaja = 'Sí' GROUP BY comuna")

# Consulta 5b: Distribución por rangos de edad
df_distribucion_rangos_edad = sqldf("SELECT CASE WHEN edad BETWEEN 7 AND 17 THEN '7-17' WHEN edad BETWEEN 18 AND 30 THEN '18-30' WHEN edad BETWEEN 30 AND 50 THEN '30-50' WHEN edad BETWEEN 50 AND 80 THEN '50-80' END as rango_edad, COUNT(*) as cantidad FROM df_empleo WHERE trabaja = 'Sí' GROUP BY rango_edad")

# Consulta 6: Distribución de cuántos trabajan por nivel_estudio
df_distribucion_nivel_estudio = sqldf("SELECT nivel_estudio, COUNT(*) as cantidad FROM df_empleo WHERE trabaja = 'Sí' GROUP BY nivel_estudio")

# Adicional: Trabajan por nivel de estudio (sí/no)
df_trabajan_por_nivel = sqldf("SELECT nivel_estudio, trabaja, COUNT(*) as cantidad FROM df_empleo GROUP BY nivel_estudio, trabaja")

# Adicional: Rangos de edad por comuna
df_rangos_edad_por_comuna = sqldf("SELECT comuna, CASE WHEN edad BETWEEN 7 AND 17 THEN '7-17' WHEN edad BETWEEN 18 AND 30 THEN '18-30' WHEN edad BETWEEN 30 AND 50 THEN '30-50' WHEN edad BETWEEN 50 AND 80 THEN '50-80' END as rango_edad, COUNT(*) as cantidad FROM df_empleo WHERE trabaja = 'Sí' GROUP BY comuna, rango_edad")

# Cálculos para la página de inicio
total_personas = len(df_empleo)
menores_trabajando = df_menores_trabajando.iloc[0, 0]
total_trabajando = df_empleo[df_empleo['trabaja'] == 'Sí'].shape[0]
desempleo_pct = ((total_personas - total_trabajando) / total_personas) * 100
vivir_bien_count = df_distribucion_vivir_bien[df_distribucion_vivir_bien['categoria'] == 'Vivir bien']['cantidad'].iloc[0] if not df_distribucion_vivir_bien[df_distribucion_vivir_bien['categoria'] == 'Vivir bien'].empty else 0

# Configuración de la página
st.set_page_config(page_title="Empleo en Medellín", layout="wide")

# CSS para estilos
st.markdown("""
<style>
body {
    font-family: 'Arial', sans-serif;
    background-color: #FFF8DC;  /* Color cálido */
    color: #8B4513;  /* Marrón cálido */
}
.sidebar .sidebar-content {
    background-color: #FFE4B5;  /* Fondo sidebar */
}
.stButton>button {
    background-color: #FFA500;  /* Naranja */
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
    font-size: 16px;
}
.stButton>button:hover {
    background-color: #FFFF00;  /* Amarillo */
    color: black;
}
.analysis {
    font-family: 'Times New Roman', serif;
    font-size: 14px;
}
.title {
    font-weight: bold;
    font-size: 18px;
    color: #FF4500;
}
</style>
""", unsafe_allow_html=True)

# Navegación
if 'page' not in st.session_state:
    st.session_state.page = 'Inicio'

with st.sidebar:
    st.title("Navegación")
    if st.button("Inicio"):
        st.session_state.page = 'Inicio'
    if st.button("Nivel de estudio"):
        st.session_state.page = 'Nivel de estudio'
    if st.button("Estrato y comuna"):
        st.session_state.page = 'Estrato y comuna'

# Páginas
if st.session_state.page == 'Inicio':
    st.title("📊 Inicio")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Personas encuestadas", total_personas)
    with col2:
        st.metric("👶 Menores de edad que trabajan", menores_trabajando)
    with col3:
        st.metric("📉 Porcentaje de desempleo", f"{desempleo_pct:.1f}%")
        st.progress(desempleo_pct / 100)
    with col4:
        st.metric("💰 Personas con sueldo para vivir bien", vivir_bien_count)
        pct_vivir_bien = (vivir_bien_count / total_personas) * 100
        st.write(f"📊 Porcentaje: {pct_vivir_bien:.1f}%")
        st.markdown('<p class="analysis">El porcentaje de personas con ingresos suficientes para vivir dignamente es bajo 😔, lo que indica desigualdades económicas y necesidad de políticas de empleo mejor remunerado. 💼</p>', unsafe_allow_html=True)

elif st.session_state.page == 'Nivel de estudio':
    st.title("🎓 Análisis por Nivel de Estudio")
    
    # Gráfico 1: Ingreso promedio por nivel de estudio
    st.subheader("📈 Ingreso Promedio por Nivel de Estudio")
    fig1 = px.bar(df_ingreso_promedio_nivel_estudio, x='nivel_estudio', y='ingreso_promedio', title="Ingreso Promedio por Nivel de Estudio", color_discrete_sequence=['#FFA500'])
    st.plotly_chart(fig1)
    st.markdown('<p class="analysis">Este gráfico muestra cómo el nivel educativo influye en los ingresos promedio 📚, destacando la importancia de la educación en el mercado laboral. 🎓</p>', unsafe_allow_html=True)
    
    # Gráfico 2: Cuántos trabajan por nivel de estudio
    st.subheader("👷 Distribución de Trabajo por Nivel de Estudio")
    fig2 = px.bar(df_trabajan_por_nivel, x='nivel_estudio', y='cantidad', color='trabaja', barmode='stack', title="Trabajan vs No Trabajan por Nivel de Estudio", color_discrete_sequence=['#FFD700', '#FF6347'])
    st.plotly_chart(fig2)
    st.markdown('<p class="analysis">La distribución revela patrones de empleo según educación 📖, sugiriendo oportunidades desiguales en el acceso al trabajo. 🤝</p>', unsafe_allow_html=True)

elif st.session_state.page == 'Estrato y comuna':
    st.title("🏠 Análisis por Estrato y Comuna")
    
    # Gráfico 1: Distribución por estrato
    st.subheader("📊 Distribución de Trabajo por Estrato")
    fig3 = px.pie(df_distribucion_trabajo_estrato, values='cantidad', names='estrato', title="Distribución de Trabajo por Estrato", color_discrete_sequence=['#FFA500', '#FFD700', '#FF6347', '#FF69B4', '#FFE4B5', '#DEB887', '#F0E68C'])
    st.plotly_chart(fig3)
    st.markdown('<p class="analysis">El estrato socioeconómico afecta el acceso al empleo 🏘️, con concentraciones en estratos medios. 📈</p>', unsafe_allow_html=True)
    
    # Gráfico 2: Distribución por comuna y rangos de edad
    st.subheader("🌆 Distribución por Rangos de Edad en Comuna Seleccionada")
    comuna_seleccionada = st.selectbox("🏙️ Selecciona una comuna (1-16)", list(range(1, 17)))
    df_comuna = df_rangos_edad_por_comuna[df_rangos_edad_por_comuna['comuna'] == comuna_seleccionada]
    if not df_comuna.empty:
        fig4 = px.bar(df_comuna, x='rango_edad', y='cantidad', title=f"Trabajadores por Rango de Edad en Comuna {comuna_seleccionada}", color_discrete_sequence=['#FFA500', '#FFD700', '#FF6347', '#FF69B4'])
        st.plotly_chart(fig4)
        st.markdown('<p class="analysis">Este gráfico ilustra la composición etaria de los trabajadores en la comuna seleccionada 👥, útil para políticas locales. 🏛️</p>', unsafe_allow_html=True)
    else:
        st.write("❌ No hay datos para esta comuna.")
    
    # Gráfico adicional: Distribución si sueldo es para vivir bien
    st.subheader("💵 Distribución de Sueldos para Vivir Bien")
    fig5 = px.pie(df_distribucion_vivir_bien, values='cantidad', names='categoria', title="Sueldos Suficientes para Vivir Bien", color_discrete_sequence=['#FFD700', '#FF6347'])
    st.plotly_chart(fig5)
    st.markdown('<p class="analysis">La mayoría de los ingresos no alcanzan el umbral para una vida digna 😟, reflejando problemas económicos y sociales profundos que requieren intervenciones urgentes. 🚨</p>', unsafe_allow_html=True)

