import datetime as dt
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Time, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///./appointments.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialty = Column(String, nullable=True)
    working_days = Column(String)  
    start_time = Column(Time)     
    end_time = Column(Time)         

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    reason = Column(String, nullable=True)
    start_time = Column(DateTime, index=True)
    cancelled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)

    doctor = relationship("Doctor")

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _seed_doctors()

def _seed_doctors() -> None:
    """Add a couple of placeholder doctors if the table is empty."""
    db = SessionLocal()
    try:
        if db.query(Doctor).count() == 0:
            db.add_all([
                Doctor(
                    name="Dr. John Smith",
                    specialty="General Physician",
                    working_days="Mon,Tue,Wed,Thu,Fri",
                    start_time=dt.time(9, 0),
                    end_time=dt.time(17, 0),
                ),
                Doctor(
                    name="Dr. Sara",
                    specialty="Cardiologist",
                    working_days="Mon,Wed,Fri",
                    start_time=dt.time(10, 0),
                    end_time=dt.time(15, 0),
                ),
            ])
            db.commit()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()