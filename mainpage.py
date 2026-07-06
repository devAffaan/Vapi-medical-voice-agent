import streamlit as st
import datetime as dt
import requests

st.title(" Al Shifa Hospital Appointment Booking Portal ")
base_url=st.text_input("Backend URL", "http://localhost:4444").rstrip("/")

patient_name = st.text_input("Patient Name")
reason = st.text_input("Reason for Appointment")
start_date = st.date_input("Date", value=dt.date.today() + dt.timedelta(days=1))
start_time = st.time_input("Time", value=dt.time(9, 0))

if st.button("Schedule"):
    start_dt = dt.datetime.combine(start_date, start_time)
    
    payload = {
        "patient_name": patient_name.strip(),
        "reason": reason.strip() or None,
        "start_time": start_dt.isoformat(),
    }
    
    try:
        resp = requests.post(f"{base_url}/schedule_appointment/", json=payload, timeout=10)
        
        resp.raise_for_status()
        
        st.success("Scheduled")
        
    except requests.RequestException as exc:
        st.error(f"Schedule failed: {exc}")

st.divider()
st.subheader("Cancel")

cancel_name = st.text_input("Patient name to cancel", key="cancel_name")
cancel_date = st.date_input("Date to cancel", key="cancel_date", value=dt.date.today())

if st.button("Cancel appointments"):
    payload = {"patient_name": cancel_name.strip(), "date": cancel_date.isoformat()}
    try:
        resp = requests.post(f"{base_url}/cancel_appointment/", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json() if resp.content else {}
        st.success(f"Canceled: {data.get('cancel_count', 0)}")
    except requests.HTTPError:
        st.error(resp.text)
    except requests.RequestException as exc:
        st.error(f"Cancel failed: {exc}")

appointments_date = st.date_input("Date to check appointments", key="check_appointment_date", value=dt.date.today())
if st.button("Check appointments"):
    try:
        params = {"date": appointments_date.isoformat()}
        resp = requests.get(f"{base_url}/list_appointments/", params=params, timeout=10)
        resp.raise_for_status()
        st.dataframe(resp.json(), use_container_width=True, hide_index=True)
    except requests.RequestException as exc:
        st.warning(f"Could not load appointments: {exc}")

st.divider()
st.subheader("Doctor Availability")

if st.button("Show all doctors"):
    try:
        resp = requests.get(f"{base_url}/list_doctors/", timeout=10)
        resp.raise_for_status()
        st.dataframe(resp.json(), use_container_width=True, hide_index=True)
    except requests.RequestException as exc:
        st.warning(f"Could not load doctors: {exc}")

availability_doctor_name = st.text_input("Doctor name", key="availability_doctor_name")
availability_date = st.date_input("Date to check availability", key="availability_date", value=dt.date.today())

if st.button("Check doctor availability"):
    try:
        params = {"doctor_name": availability_doctor_name.strip(), "date": availability_date.isoformat()}
        resp = requests.get(f"{base_url}/check_availability/", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("is_working_day"):
            st.warning(f"{data.get('doctor_name')} does not work on this day.")
        else:
            slots = data.get("available_slots", [])
            if slots:
                st.success(f"Available slots for {data.get('doctor_name')} on {data.get('date')}:")
                st.write(", ".join(slots))
            else:
                st.info(f"{data.get('doctor_name')} is fully booked on {data.get('date')}.")
    except requests.RequestException as exc:
        st.warning(f"Could not check availability: {exc}")