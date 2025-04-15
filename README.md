# Tutor Dek

1. Clone repo
```bash
git clone https://gitlab.cs.ui.ac.id/pkpl/kelompok-82/health-mate-be.git
git branch auth/joy
git checkout auth/joy
git pull origin auth/joy
git branch {branch-kalian} (contoh nama branch: auth/joy)
git checkout {branch-kalian}

# kalo udah commit ke branch masing2 dulu, klo aman merge ke dev
git add .
git commit -m “commit-message”
git push origin {branch-kalian}
```

2. Aktifkan env dan install dependency
```bash 
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

3. Buat database Postgres
```bash
-- Create the database
CREATE DATABASE health_mate;

-- Create PATIENT table
CREATE TABLE patient (
    patient_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    name VARCHAR(100),
    sex VARCHAR(10),
    phone VARCHAR(20),
    blood_type VARCHAR(5),
    password VARCHAR(100),
    birthdate DATE,
    address TEXT
);

-- Create HEALTHMATE_WALLET table
CREATE TABLE healthmate_wallet (
    id_hmw SERIAL PRIMARY KEY,
    pin VARCHAR(10),
    balance DECIMAL(10, 2),
    patient_id INTEGER UNIQUE REFERENCES patient(patient_id)
);

-- Create DOCTOR table
CREATE TABLE doctor (
    doctor_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    name VARCHAR(100),
    sex VARCHAR(10),
    phone VARCHAR(20),
    specialization VARCHAR(100),
    password VARCHAR(100),
    birthdate DATE,
    address TEXT,
    experience INTEGER
);

-- Create ADMIN table
CREATE TABLE admin (
    admin_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    name VARCHAR(100),
    sex VARCHAR(10),
    phone VARCHAR(20),
    password VARCHAR(100),
    birthdate DATE
);

-- Create APPOINTMENT table
CREATE TABLE appointment (
    appointment_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patient(patient_id),
    doctor_id INTEGER REFERENCES doctor(doctor_id),
    doctor_name VARCHAR(100),
    specialization VARCHAR(100),
    date DATE,
    time TIME
);

-- Create PRESCRIPTION table
CREATE TABLE prescription (
    prescription_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patient(patient_id),
    medicine TEXT,
    advice TEXT
);

CREATE TABLE bill (
    bill_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patient(patient_id),
    date DATE,
    time TIME,
    amount NUMERIC(10, 2),
    status VARCHAR(10) DEFAULT 'Unpaid',
    appointment_id INTEGER REFERENCES appointment(appointment_id) ON DELETE CASCADE
);

-- Create AUDIT LOG table
CREATE TABLE IF NOT EXISTS audit_log (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    user_role VARCHAR(20) NOT NULL,
    action VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    details TEXT
);

-- ====================
-- Dummy Data: ADMIN
-- ====================
INSERT INTO ADMIN (First_Name, Last_Name, Sex, Phone, Password, Birthdate) VALUES
('Rina',   'Saputra', 'F', '081234567890', 
    '8d2cb1dc9e018c72324103e5077586c625c3256e88f94544830c1a1619c1f0e4', '1980-05-12'), -- pass : Adm!n123Xy
('Budi',   'Hartono', 'M', '082345678901',
    '476a210ae9f19014d9f3aa1986c52f08cb776f022861529fd31f6c7335a1767e', '1975-11-03'), -- pass : Secr3t#123A
('Siti',   'Kurnia',  'F', '083456789012',
    '51cc18bcd87e3a451b7254cce59629ddeb6a0d351cc30f90074ae8f8abcb949c', '1988-07-25'); -- pass : 123$PowerAd

-- ====================
-- Dummy Data: PATIENT
-- ====================
INSERT INTO PATIENT (First_Name, Last_Name, Sex, Phone, Blood_Type, Password, Birthdate, Address) VALUES
('Andi',   'Wijaya',    'M', '081122334455', 'O', 
    '06969f74536db93dd77da2e6481cdad0dc6880203353c34c07b96cff09374482', '1990-02-14', 'Jl. Melati No. 5, Jakarta'), -- pass : Pati456!ent
('Maya',   'Permata',   'F', '081133445566', 'A', 
    '01dd8976482db553a66aab03c7efdb844bf57f711a9c838f30d6ff47d49a425d', '1992-08-30', 'Jl. Kenanga No. 12, Bandung'), -- pass : 456$HeaLthy
('Dewi',   'Sari',      'F', '081144556677', 'B', 
    '8dc906ac27d93bc529b6c7d17e127eed06580f3db71a341f3b9b93624430f308', '1985-12-05', 'Jl. Mawar No. 8, Surabaya'); -- pass : MyP@ss456x

-- ====================
-- Dummy Data: DOCTOR
-- ====================
INSERT INTO DOCTOR (First_Name, Last_Name, Sex, Phone, Address, Password, Birthdate, Specialization, Experience) VALUES
('Dr. Agus', 'Prasetyo', 'M', '081155667788', 'Jl. Dokter No. 3, Jakarta', 
    'cd2ee21fb82aa97efd7f1ddc9339273fd8d598ddb6843f1cddfd6471abd30e18', '1970-04-20', 'Cardiology', 15),  -- pass : Doc#789Med
('Dr. Lina', 'Setiawan', 'F', '081166778899', 'Jl. Sehat No. 7, Bandung', 
    '124a0fdf0cd34aa8790b45a210c2b6223b7c6f6ac98fce9cc59cfcc1398f31a4', '1978-09-11', 'Dermatology', 10), -- pass : 789DrC@re!
('Dr. Eko',  'Santoso',  'M', '081177889900', 'Jl. Klinik No. 10, Surabaya', 
    '14abd7bcdd543db0d2a29feb308c461b74d1b763da625af9fe4a6a23761a0bd8', '1982-01-30', 'Pediatrics', 8); -- pass : Cl1n!c789a

-- ====================
-- Dummy Data: AUDIT LOG
-- ====================
INSERT INTO audit_log (user_id, user_role, action, ip_address, details)
VALUES 
-- Patient Andi Wijaya (user_id: 1)
(1, 'patient', 'login', '192.168.1.100', 'Path: /auth/login, Method: POST'),
(1, 'patient', 'view_profile', '192.168.1.100', 'Path: /patient/profile, Method: GET'),

-- Doctor Dr. Lina Setiawan (user_id: 2)
(2, 'doctor', 'login', '192.168.0.101', 'Path: /auth/login, Method: POST'),
(2, 'doctor', 'access_doctor_dashboard', '192.168.0.101', 'Path: /doctor/dashboard, Method: GET'),

-- Admin Rina Saputra (user_id: 1 in admin table)
(1, 'admin', 'login', '192.168.0.50', 'Path: /auth/login, Method: POST');
```

4. Setting Postgres ke Django
- buat file `.env`
isinya: 
```bash
DEBUG=True
SECRET_KEY=
DB_NAME=health_mate
DB_USER=postgres
DB_PASSWORD={password_kalian}
DB_HOST=localhost
DB_PORT=5432
```
cara dapetin secret_key, copas dibawah di terminal
`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

5. Done, kalian udh bisa coba run n login pake dummy data yang udah dibuat tadi
contoh input login:
Phone Number: 081122334455
Password : $2y$10$abcd1234efgh5678ijkl
Role : Patient