from django.db import connection
import hashlib

def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def dictfetchone(cursor):
    """Return a single row from a cursor as a dict"""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))

def hash_password(password):
    """Simple password hashing for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

# User authentication functions
def authenticate_patient(phone, password):
    # hashed_password = hash_password(password)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT patient_id, name FROM patient WHERE phone = %s AND password = %s",
            [phone, password]
        )
        return dictfetchone(cursor)

def authenticate_doctor(phone, password):
    # hashed_password = hash_password(password)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT doctor_id, CONCAT(first_name, ' ', last_name) AS name FROM doctor WHERE phone = %s AND password = %s",
            [phone, password]
        )
        return dictfetchone(cursor)

def authenticate_admin(phone, password):
    hashed_password = hash_password(password)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT admin_id, CONCAT(first_name, ' ', last_name) AS name FROM admin WHERE phone = %s AND password = %s",
            [phone, hashed_password]
        )
        return dictfetchone(cursor)

# Patient related DB functions
def get_patient(patient_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM patient WHERE patient_id = %s",
            [patient_id]
        )
        return dictfetchone(cursor)

def update_patient(patient_id, data):
    fields = []
    values = []
    
    for key, value in data.items():
        if key != 'patient_id' and value is not None:
            fields.append(f"{key} = %s")
            values.append(value)
    
    if not fields:
        return False
    
    values.append(patient_id)
    
    with connection.cursor() as cursor:
        query = f"UPDATE patient SET {', '.join(fields)} WHERE patient_id = %s"
        cursor.execute(query, values)
        return cursor.rowcount > 0

# Doctor related DB functions
def get_doctor(doctor_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT *, CONCAT(first_name, ' ', last_name) AS name FROM doctor WHERE doctor_id = %s",
            [doctor_id]
        )
        return dictfetchone(cursor)

def get_all_doctors():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT *, CONCAT(first_name, ' ', last_name) AS name FROM doctor",
        )
        
        return dictfetchall(cursor)

def get_doctors_by_specialization(specialization):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT *, CONCAT(first_name, ' ', last_name) AS name FROM doctor WHERE specialization = %s",
            [specialization]
        )
        return dictfetchall(cursor)

# Admin related DB functions
def get_admin(admin_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM admin WHERE admin_id = %s",
            [admin_id]
        )
        return dictfetchone(cursor)

def create_appointment(patient_id, doctor_id, date, time, appointment_fee):
    with connection.cursor() as cursor:
        # Get doctor details
        cursor.execute(
            "SELECT CONCAT(first_name, ' ', last_name) AS name, specialization FROM doctor WHERE doctor_id = %s",
            [doctor_id]
        )
        doctor_info = dictfetchone(cursor)
        
        if not doctor_info:
            return None
        
        # Create appointment
        cursor.execute(
            """
            INSERT INTO appointment 
            (patient_id, doctor_id, doctor_name, specialization, date, time)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING appointment_id
            """,
            [patient_id, doctor_id, doctor_info['name'], doctor_info['specialization'], date, time]
        )
        result = cursor.fetchone()
        
        if result:
            appointment_id = result[0]
            
            # Create bill and link it to the new appointment
            cursor.execute(
                """
                INSERT INTO bill (patient_id, date, time, amount, status, appointment_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [patient_id, date, time, appointment_fee, 'Unpaid', appointment_id]
            )
            return appointment_id  # Return the appointment_id if everything is successful
        else:
            return None



def get_patient_appointments(patient_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT a.*, d.experience 
            FROM appointment a
            JOIN doctor d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s
            ORDER BY a.date DESC, a.time DESC
            """,
            [patient_id]
        )
        return dictfetchall(cursor)

def get_doctor_appointments(doctor_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT a.*, p.name as patient_name
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = %s
            ORDER BY a.date, a.time
            """,
            [doctor_id]
        )
        return dictfetchall(cursor)

# Prescription related DB functions
def create_prescription(patient_id, medicine, advice):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO prescription 
            (patient_id, medicine, advice)
            VALUES (%s, %s, %s)
            RETURNING prescription_id
            """,
            [patient_id, medicine, advice]
        )
        result = cursor.fetchone()
        return result[0] if result else None

def get_patient_prescriptions(patient_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM prescription WHERE patient_id = %s",
            [patient_id]
        )
        return dictfetchall(cursor)

# Bill/Payment related DB functions
def create_bill(patient_id, amount, date, time):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO bill 
            (patient_id, amount, date, time)
            VALUES (%s, %s, %s, %s)
            RETURNING bill_id
            """,
            [patient_id, amount, date, time]
        )
        result = cursor.fetchone()
        return result[0] if result else None

def get_patient_bills_paid(patient_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM bill WHERE patient_id = %s AND status = 'Paid'",
            [patient_id]
        )
        return dictfetchall(cursor)

def get_patient_bills(patient_id): 
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM bill WHERE patient_id = %s AND status = 'Unpaid'",
            [patient_id]
        )
        return dictfetchall(cursor)
    
def get_patient_bills_topup_or_paid(patient_id): 
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM bill WHERE patient_id = %s AND (status = 'Topup' OR status = 'Paid') ORDER BY date DESC, time DESC",
            [patient_id]
        )
        return dictfetchall(cursor)

def get_patient_bills_topup(patient_id): 
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM bill WHERE patient_id = %s AND status = 'Topup'",
            [patient_id]
        )
        return dictfetchall(cursor)
    
def get_patient_bills_topup_or_paid(patient_id): 
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM bill WHERE patient_id = %s AND (status = 'Topup' OR status = 'Paid') ORDER BY date DESC, time DESC",
            [patient_id]
        )
        return dictfetchall(cursor)

def get_patient_bills_topup(patient_id): 
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM bill WHERE patient_id = %s AND status = 'Topup'",
            [patient_id]
        )
        return dictfetchall(cursor)

def get_patient_phone(patient_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT phone FROM patient WHERE patient_id = %s",
            [patient_id]
        )
        result = dictfetchone(cursor)
        return result['phone'] if result else None

def update_wallet_balance(patient_id, amount, wallet_pin):
    with connection.cursor() as cursor:
        # Verify wallet PIN
        cursor.execute(
            "SELECT wallet_balance FROM patient WHERE patient_id = %s AND wallet_pin = %s",
            [patient_id, wallet_pin]
        )
        result = dictfetchone(cursor)
        
        if not result:
            return False
            
        # Update balance
        new_balance = result['wallet_balance'] + amount
        cursor.execute(
            "UPDATE patient SET wallet_balance = %s WHERE patient_id = %s",
            [new_balance, patient_id]
        )
        return cursor.rowcount > 0

def pay_from_wallet(patient_id, amount, wallet_pin):
    with connection.cursor() as cursor:
        # Verify wallet PIN and check balance
        cursor.execute(
            "SELECT wallet_balance FROM patient WHERE patient_id = %s AND wallet_pin = %s",
            [patient_id, wallet_pin]
        )
        result = dictfetchone(cursor)
        
        if not result or result['wallet_balance'] < amount:
            return False
            
        # Update balance
        new_balance = result['wallet_balance'] - amount
        cursor.execute(
            "UPDATE patient SET wallet_balance = %s WHERE patient_id = %s",
            [new_balance, patient_id]
        )
        return cursor.rowcount > 0