import datetime as dt

from sqlalchemy import select
from database import init_db, Appointment, get_db
from sqlalchemy.orm import Session
import datetime as dt

init_db()

from pydantic import BaseModel

class AppointmentRequest(BaseModel):
    patient_name: str
    reason: str
    start_time: dt.datetime

class AppointmentResponse(BaseModel):
    id: int
    patient_name: str
    reason: str | None
    start_time: dt.datetime
    cancelled: bool
    created_at: dt.datetime

class CancelAppointmentRequest(BaseModel):
    patient_name: str
    date: dt.datetime

class CancelAppointmentResponse(BaseModel):
    cancel_count: int



# Now Creating Endpointsssss

from fastapi import Depends, FastAPI, HTTPException

app = FastAPI()

@app.post("/schedule_appointment/")
def schedule_appointment(request: AppointmentRequest, db: Session = Depends(get_db)):
    new_appointment = Appointment(
        patient_name=request.patient_name,
        reason=request.reason,
        start_time=request.start_time
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    new_appointment_return_obj = AppointmentResponse(
        id = new_appointment.id,
        patient_name = new_appointment.patient_name,
        reason = new_appointment.reason,
        start_time = new_appointment.start_time,
        cancelled = new_appointment.cancelled,
        created_at = new_appointment.created_at 
    )
    return new_appointment_return_obj


@app.post("/cancel_appointment/")
def cancel_appointment(request: CancelAppointmentRequest, db: Session = Depends(get_db)):
    start_dt = dt.datetime.combine(request.date, dt.time.min)
    end_dt = start_dt + dt.timedelta(days=1)
    result = db.execute(
        select(Appointment)
        .where(Appointment.patient_name == request.patient_name)
        .where(Appointment.start_time >= start_dt)  
        .where(Appointment.start_time <= end_dt)
        .where(Appointment.cancelled == False)
    )
    appointments = result.scalars().all()
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointments found for the given details.")
    for appointment in appointments:
        appointment.cancelled = True
    
    db.commit()

    return CancelAppointmentResponse(cancel_count=len(appointments))


@app.get("/list_appointments/")
def list_appointments(date: dt.date, db: Session = Depends(get_db)):
    start_dt = dt.datetime.combine(date, dt.time.min)
    end_dt = start_dt + dt.timedelta(days=1)
    result = db.execute(
        select(Appointment)
        .where(Appointment.cancelled == False)
        .where(Appointment.start_time >= start_dt)  
        .where(Appointment.start_time <= end_dt)
        .order_by(Appointment.start_time.asc())
    )
    booked_appointments = []
    for appointment in result.scalars():
        appointment_obj = AppointmentResponse(
            id=appointment.id,
            patient_name=appointment.patient_name,
            reason=appointment.reason,
            start_time=appointment.start_time,
            cancelled=appointment.cancelled,
            created_at=appointment.created_at
        )
        booked_appointments.append(appointment_obj)

    return booked_appointments

from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.orm import declarative_base

DoctorBase = declarative_base()

class Doctor(DoctorBase):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialty = Column(String, nullable=True)
    working_days = Column(String) 
    start_time = Column(Time)
    end_time = Column(Time)

from database import engine, SessionLocal
DoctorBase.metadata.create_all(bind=engine)

def _seed_doctors():
    db = SessionLocal()
    try:
        if db.query(Doctor).count() == 0:
            db.add_all([
                Doctor(name="Dr. John Smith", specialty="General Physician",
                       working_days="Mon,Tue,Wed,Thu,Fri",
                       start_time=dt.time(9, 0), end_time=dt.time(17, 0)),
                Doctor(name="Dr. Sara", specialty="Cardiologist",
                       working_days="Mon,Wed,Fri",
                       start_time=dt.time(10, 0), end_time=dt.time(15, 0)),
            ])
            db.commit()
    finally:
        db.close()

_seed_doctors()

class DoctorResponse(BaseModel):
    id: int
    name: str
    specialty: str | None
    working_days: str
    start_time: dt.time
    end_time: dt.time

class AvailabilityResponse(BaseModel):
    doctor_name: str
    date: dt.date
    is_working_day: bool
    available_slots: list[str]

DAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SLOT_MINUTES = 30

@app.get("/list_doctors/")
def list_doctors():
    db = SessionLocal()
    try:
        doctors = db.execute(select(Doctor)).scalars().all()
        return [
            DoctorResponse(
                id=d.id, name=d.name, specialty=d.specialty,
                working_days=d.working_days, start_time=d.start_time, end_time=d.end_time,
            )
            for d in doctors
        ]
    finally:
        db.close()

@app.get("/check_availability/")
def check_availability(doctor_name: str, date: dt.date):
    db = SessionLocal()
    try:
        doctor = db.execute(select(Doctor).where(Doctor.name == doctor_name)).scalars().first()
        if not doctor:
            raise HTTPException(status_code=404, detail=f"No doctor found with name '{doctor_name}'.")

        weekday_abbr = DAY_ABBR[date.weekday()]
        working_days = [d.strip() for d in doctor.working_days.split(",")]

        if weekday_abbr not in working_days:
            return AvailabilityResponse(doctor_name=doctor.name, date=date, is_working_day=False, available_slots=[])

        day_start = dt.datetime.combine(date, doctor.start_time)
        day_end = dt.datetime.combine(date, doctor.end_time)

        result = db.execute(
            select(Appointment)
            .where(Appointment.cancelled == False)
            .where(Appointment.start_time >= day_start)
            .where(Appointment.start_time < day_end)
        )
        booked_times = {a.start_time for a in result.scalars()}

        slots = []
        current = day_start
        while current < day_end:
            if current not in booked_times:
                slots.append(current.strftime("%H:%M"))
            current += dt.timedelta(minutes=SLOT_MINUTES)

        return AvailabilityResponse(doctor_name=doctor.name, date=date, is_working_day=True, available_slots=slots)
    finally:
        db.close()


import uvicorn  
if __name__ == "__main__":
    uvicorn.run("configuration:app", host="127.0.0.1", port=4444, reload=True)