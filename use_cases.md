# Use Cases

## Actors
- **Patient**: Books and manages appointments.
- **Doctor**: Manages appointment requests.

---

## UC1: View Doctor Availability
- **Actor:** Patient
- **Description:** The patient views the available days and time slots for a specific doctor.
- **Precondition:** Patient is logged into the system. The doctor has published availability.
- **Main Flow:**
  1. Patient selects a doctor from the system.
  2. System retrieves and displays the doctor's available days and time slots.
- **Alternative Flow (A1):**
  - If the doctor has no free slots, the system displays: *"No availability for this doctor."*

---

## UC2: Book Appointment
- **Actor:** Patient
- **Description:** The patient books an appointment in an available time slot.
- **Precondition:** Patient has fewer than N (3) upcoming appointments (counting only `Pending` + `Accepted`).
- **Main Flow:**
  1. Patient selects an available time slot.
  2. System verifies the slot is still free.
  3. System verifies the patient has fewer than N upcoming appointments.
  4. System creates a new appointment with status `Pending`.
  5. System confirms the booking request to the patient.
- **Alternative Flow (A1) - Slot already taken:**
  - If the slot was booked by another patient, the system rejects the booking and displays: *"This time slot is no longer available."*
- **Alternative Flow (A2) - Maximum limit reached:**
  - If the patient already has N (3) upcoming appointments (Pending + Accepted), the system rejects the booking and displays: *"Maximum upcoming appointments limit reached."*

---

## UC3: Manage Appointment Request
- **Actor:** Doctor
- **Description:** The doctor reviews and accepts or declines a pending appointment request.
- **Precondition:** There is at least one `Pending` appointment request for the doctor.
- **Main Flow:**
  1. Doctor views the list of pending requests.
  2. Doctor selects a request and chooses `Accept` or `Decline`.
  3. System updates the appointment status accordingly.
  4. System notifies the patient of the decision.
- **Alternative Flow (A1):**
  - If the doctor declines the request, the appointment status becomes `Declined` and **does NOT count** toward the patient's N limit. The time slot is freed.

---

## UC4: Cancel Appointment
- **Actor:** Patient
- **Description:** The patient cancels an upcoming appointment.
- **Precondition:** The appointment exists and is in `Pending` or `Accepted` status (not past).
- **Main Flow:**
  1. Patient selects an upcoming appointment to cancel.
  2. System changes the appointment status to `Cancelled`.
  3. System confirms the cancellation to the patient.
  4. The cancelled appointment **does NOT count** toward the patient's N limit.
- **Alternative Flow (A1):**
  - If the appointment is in the past, the system rejects the cancellation: *"Cannot cancel past appointments."*