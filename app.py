import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta

from db import init_db,insert_fast, close_active_fast, get_logs, get_active_fast
from fasting_logic import (
    calculate_fasting_duration,
    calculate_eating_duration,
    fasting_progress,
    remaining_time,
)

st.set_page_config(
    page_title="Calculadora de Ayuno 16/8", 
    page_icon="⏳", 
    layout="wide")

init_db()  # Initialize the database

st.title("⏳ Calculadora de Ayuno Intermitente 16/8")
st.caption("Control simple de horarios, ventana de comida e historial de ayunos.")

tab1, tab2, tab3 = st.tabs(["Ayuno Actual", "Registrar Ayuno",  "Historial de Ayunos"])

# =========================
# TAB 1: AYUNO ACTUAL
# =========================

with tab1:
    st.subheader("Estados del ayuno actual")

    active = get_active_fast()

    if active.empty:
        st.info("No hay ayuno activo actualmente.")

    else:
        row = active.iloc[0]
        start_time = pd.to_datetime(row['start_time']).to_pydatetime()
        target_end_time = pd.to_datetime(row['target_end_time']).to_pydatetime()
        fasting_hours = int(row['fasting_hours'])
        eating_hours = int(row['eating_hours'])

        now=datetime.now()
        progress = fasting_progress(start_time, target_end_time, now)
        eating_end = calculate_eating_duration(target_end_time, eating_hours)

        col1, col2, col3 = st.columns(3)
        col1.metric("Inicio del Ayuno", start_time.strftime("%Y-%m-%d %H:%M:%S"))
        col2.metric("Meta para romper el ayuno", target_end_time.strftime("%Y-%m-%d %H:%M:%S"))
        col3.metric("Tiempo Restante", f"{remaining_time(target_end_time, now)}")

        st.progress(progress)

        if now > target_end_time:
            st.success("¡Has completado tu ayuno! Ahora puedes comer.")
        else:
            st.warning("Aún estás en tu ventana de ayuno. ¡Sigue así!")
        
        st.write(f"Tu ventana de comida termina a las: {eating_end.strftime('%Y-%m-%d %H:%M:%S')}")

        if st.button("Cerrar Ayuno"):
            close_active_fast(datetime.now())
            st.success("Ayuno cerrado exitosamente. ¡Buen trabajo!")
            st.rerun()  # Refresh the page to update the state


# =========================
# TAB 2: REGISTRAR AYUNO
# =========================

with tab2:
    st.subheader("Registrar un nuevo ayuno")

    st.write("Ejemplo: si cenaste a las 7:00 PM y haras 16 horas, romperias a las 11:00 AM del día siguiente.")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Fecha de inicio del ayuno", value=datetime.today().date())
        start_hour = st.time_input("Hora de inicio", value=time(19, 0))

    with col2:
        fasting_hours = st.number_input("Duración del ayuno (horas)", min_value=12, max_value=48, value=16)
        eating_hours = st.number_input("Duración de la ventana de comida (horas)", min_value=1, max_value=24, value=8)

    notes = st.text_area("Notas", placeholder="Ejemplo: cene pollo, vegetales y aguacate")

    start_time = datetime.combine(start_date, start_hour)
    target_end_time = calculate_fasting_duration(start_time, fasting_hours)
    eating_end_time = calculate_eating_duration(target_end_time, eating_hours)

    st.info(f"Tu ayuno terminará a las: {target_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    st.info(f"Tu ventana de comida terminará a las: {eating_end_time.strftime('%Y-%m-%d %H:%M:%S')}")   

    if st.button("Guardar Ayuno", type="primary"):
        insert_fast(
            start_time = start_time,
            fasting_hours = fasting_hours,
            eating_hours = eating_hours,
            target_end_time = target_end_time,
            status = 'activo',
            actual_end_time = None,
            notes = notes
        )
        st.success("Ayuno registrado exitosamente. ¡Buen trabajo!")
        st.rerun()  # Refresh the page to update the state

# =========================
# TAB 3: HISTORIAL
# =========================

with tab3:
    st.subheader("Historial de Ayunos")

    logs = get_logs()

    if logs.empty:
        st.info("No hay registros de ayunos.")
    else:
        logs['start_time'] = pd.to_datetime(logs['start_time'])
        logs['target_end_time'] = pd.to_datetime(logs['target_end_time'])
        logs['actual_end_time'] = pd.to_datetime(logs['actual_end_time'])
   
        st.dataframe(logs, use_container_width=True)

        closed = logs[logs['status'] == 'cerrado'].copy()

        if not closed.empty:
            closed["duration_hours"] = (
                closed["actual_end_time"] - closed["start_time"]
                ).dt.total_seconds() / 3600
            
            st.subheader("Resumen")

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Ayunos Cerrados", len(closed))
            col2.metric("Duración Promedio (horas)", round(closed["duration_hours"].mean(), 2))
            col3.metric("Duración Máxima (horas)", round(closed["duration_hours"].max(), 2))

            chart_data = closed[["start_time", "duration_hours"]].sort_values("start_time")
            st.line_chart(chart_data, x="start_time", y="duration_hours")