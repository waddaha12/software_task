"""Doctor Appointment Booking System
Implements class_diagram.md and sequence_diagram.md.
Run: python main.py
"""
from enum import Enum


class AppointmentStatus(Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    DECLINED = "Declined"
    CANCELLED = "Cancelled"


class TimeSlot:
    def __init__(self, day, start_time):
        self.day = day
        self.startTime = start_time
        self.isFree = True
        self.doctor = None  # set by Doctor.addSlot

    def book(self):
        self.isFree = False

    def free(self):
        self.isFree = True

    def __str__(self):
        return f"{self.day} {self.startTime}"


class Appointment:
    _next_id = 1

    def __init__(self, patient, doctor, slot):
        self.id = Appointment._next_id
        Appointment._next_id += 1
        self.patient = patient
        self.doctor = doctor
        self.slot = slot
        self.status = AppointmentStatus.PENDING
        self.isPast = False

    def cancel(self):
        self.status = AppointmentStatus.CANCELLED

    def __str__(self):
        return f"Appointment#{self.id} [{self.slot}] -> {self.status.value}"


class Doctor:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.slots = []
        self.appointments = []  # Doctor "1" --> "*" Appointment : receives

    def addSlot(self, slot):
        slot.doctor = self
        self.slots.append(slot)

    def getFreeSlots(self):
        return [s for s in self.slots if s.isFree]

    def getPendingRequests(self):
        return [a for a in self.appointments
                if a.status == AppointmentStatus.PENDING]

    def accept(self, appointment):
        if appointment.status != AppointmentStatus.PENDING:
            print("  [System] Only Pending requests can be accepted.")
            return False
        appointment.status = AppointmentStatus.ACCEPTED
        return True

    def decline(self, appointment):
        if appointment.status != AppointmentStatus.PENDING:
            print("  [System] Only Pending requests can be declined.")
            return False
        appointment.status = AppointmentStatus.DECLINED
        appointment.slot.free()  # declined -> slot becomes free again (UC3-A1)
        return True


class BookingSystem:
    """The 'System' participant in the sequence diagram."""

    def view_availability(self, doctor):
        return doctor.getFreeSlots()                       # S->>D: getFreeSlots()

    def book_appointment(self, patient, slot):
        doctor = slot.doctor
        if not slot.isFree:                                # S->>T: check isFree
            print("  [System] This time slot is no longer available.")
            return None
        if patient.countUpcoming() >= Patient.MAX_UPCOMING:  # S->>P: countUpcoming()
            print("  [System] Maximum upcoming appointments limit reached.")
            return None
        slot.book()                                        # S->>T: book()
        appt = Appointment(patient, doctor, slot)          # S->>A: create(Pending)
        patient.appointments.append(appt)
        doctor.appointments.append(appt)
        print(f"  [System] Booking request sent (Pending): {appt}")
        print(f"  [System] Notify {doctor.name}: new request")  # S->>D: notify
        return appt

    def doctor_decision(self, appointment, accepted):
        doctor = appointment.doctor
        if accepted:
            ok = doctor.accept(appointment)                # status = Accepted
        else:
            ok = doctor.decline(appointment)               # status = Declined, T.free()
        if not ok:
            return
        print(f"  [System] Notify {appointment.patient.name}: {appointment}")

    def cancel_appointment(self, appointment):
        if appointment.isPast:                             # UC4-A1
            print("  [System] Cannot cancel past appointments.")
            return
        if appointment.status not in (AppointmentStatus.PENDING,
                                      AppointmentStatus.ACCEPTED):
            print("  [System] Only Pending or Accepted appointments can be cancelled.")
            return
        appointment.cancel()
        appointment.slot.free()
        print(f"  [System] Cancelled: {appointment}")


class Patient:
    MAX_UPCOMING = 3

    def __init__(self, id, name, system):
        self.id = id
        self.name = name
        self.system = system
        self.appointments = []

    def viewAvailability(self, doctor):
        return self.system.view_availability(doctor)

    def countUpcoming(self):
        # upcoming = not past, and still Pending/Accepted
        active = (AppointmentStatus.PENDING, AppointmentStatus.ACCEPTED)
        return sum(1 for a in self.appointments
                   if not a.isPast and a.status in active)

    def bookAppointment(self, slot):
        return self.system.book_appointment(self, slot)

    def cancelAppointment(self, appointment):
        self.system.cancel_appointment(appointment)


def show_slots(patient, doctor):
    slots = patient.viewAvailability(doctor)
    if not slots:                                          # UC1-A1
        print("  [System] No availability for this doctor.")
    else:
        print(f"{patient.name} sees free slots of {doctor.name}: "
              f"{[str(s) for s in slots]}")
    return slots


def main():
    system = BookingSystem()
    doctor = Doctor(1, "Dr. Ahmed")
    for day, t in [("Sat", "10:00"), ("Sat", "11:00"), ("Sun", "10:00"),
                   ("Sun", "11:00"), ("Mon", "10:00")]:
        doctor.addSlot(TimeSlot(day, t))

    p1 = Patient(1, "Sara", system)
    p2 = Patient(2, "Omar", system)

    print("=== Scenario 1: view availability ===")
    slots = show_slots(p1, doctor)

    print("\n=== Scenario 2: book + doctor accepts ===")
    a1 = p1.bookAppointment(slots[0])
    system.doctor_decision(a1, accepted=True)

    print("\n=== Scenario 3: slot already taken ===")
    p2.bookAppointment(slots[0])

    print("\n=== Scenario 4: book + doctor declines (slot freed) ===")
    a2 = p2.bookAppointment(slots[1])
    system.doctor_decision(a2, accepted=False)
    show_slots(p2, doctor)

    print("\n=== Scenario 5: max 3 upcoming appointments ===")
    p1.bookAppointment(doctor.getFreeSlots()[0])
    p1.bookAppointment(doctor.getFreeSlots()[0])
    print(f"  Sara upcoming = {p1.countUpcoming()}")
    p1.bookAppointment(doctor.getFreeSlots()[0])  # 4th -> rejected

    print("\n=== Scenario 6: cancel ===")
    p1.cancelAppointment(a1)
    print(f"  Sara upcoming = {p1.countUpcoming()}")

    print("\n=== Scenario 7: cannot cancel a past appointment ===")
    a1b = p1.appointments[1]
    a1b.isPast = True
    p1.cancelAppointment(a1b)
    print(f"  Sara upcoming = {p1.countUpcoming()} (past one not counted)")

    print("\n=== Scenario 8: doctor pending list + no availability ===")
    print(f"  Pending for {doctor.name}: {[str(a) for a in doctor.getPendingRequests()]}")
    empty_doctor = Doctor(2, "Dr. Empty")
    show_slots(p1, empty_doctor)


if __name__ == "__main__":
    main()