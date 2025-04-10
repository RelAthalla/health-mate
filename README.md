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

2. Buat database Postgres
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

-- Create BILL table
CREATE TABLE bill (
    bill_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patient(patient_id),
    date DATE,
    time TIME,
    amount DECIMAL(10, 2)
);

-- ====================
-- Dummy Data: ADMIN
-- ====================
INSERT INTO ADMIN (First_Name, Last_Name, Sex, Phone, Password, Birthdate) VALUES
('Rina',   'Saputra', 'F', '081234567890',  -- Password: hashed versi 'admin123'
    '$2y$10$abcdefghijklmnopqrstuv', '1980-05-12'),
('Budi',   'Hartono', 'M', '082345678901',
    '$2y$10$mnopqrstuvabcdefghijkl', '1975-11-03'),
('Siti',   'Kurnia',  'F', '083456789012',
    '$2y$10$uvwxyzabcdef12345678', '1988-07-25');

-- ====================
-- Dummy Data: PATIENT
-- ====================
INSERT INTO PATIENT (First_Name, Last_Name, Sex, Phone, Blood_Type, Password, Birthdate, Address) VALUES
('Andi',   'Wijaya',    'M', '081122334455', 'O', 
    '$2y$10$abcd1234efgh5678ijkl', '1990-02-14', 'Jl. Melati No. 5, Jakarta'),
('Maya',   'Permata',   'F', '081133445566', 'A', 
    '$2y$10$mnop1234qrst5678uvwx', '1992-08-30', 'Jl. Kenanga No. 12, Bandung'),
('Dewi',   'Sari',      'F', '081144556677', 'B', 
    '$2y$10$yzab1234cdef5678ghij', '1985-12-05', 'Jl. Mawar No. 8, Surabaya');

-- ====================
-- Dummy Data: DOCTOR
-- ====================
INSERT INTO DOCTOR (First_Name, Last_Name, Sex, Phone, Address, Password, Birthdate, Specialization, Experience) VALUES
('Dr. Agus', 'Prasetyo', 'M', '081155667788', 'Jl. Dokter No. 3, Jakarta', 
    '$2y$10$1234abcd5678efghijkl', '1970-04-20', 'Cardiology', 15),
('Dr. Lina', 'Setiawan', 'F', '081166778899', 'Jl. Sehat No. 7, Bandung', 
    '$2y$10$5678mnop1234qrstuvwx', '1978-09-11', 'Dermatology', 10),
('Dr. Eko',  'Santoso',  'M', '081177889900', 'Jl. Klinik No. 10, Surabaya', 
    '$2y$10$9012yzab3456cdefghij', '1982-01-30', 'Pediatrics', 8);
```

3. Setting Postgres ke Django
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

4. Done, kalian udh bisa coba run n login pake dummy data yang udah dibuat tadi
contoh input login:
Phone Number: 081122334455
Password : $2y$10$abcd1234efgh5678ijkl
Role : Patient