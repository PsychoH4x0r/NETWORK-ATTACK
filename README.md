# 1. Masuk ke direktori proyek
cd "C:\Users\username\path\"

# 2. Buat virtual environment (hanya sekali)
python3 -m venv venv

# 3. Aktifkan virtual environment
#   (Command Prompt)
venv\Scripts\activate
#   (ATAU PowerShell)
# .\venv\Scripts\Activate.ps1

# 4. Instal scapy *di dalam* virtual environment
pip install scapy

# 5. Jalankan skrip
python main.py

# 6. (Setelah selesai) Nonaktifkan virtual environment
deactivate
---------------------------------------------------------
pip3 install -r requirements.txt


pip install -r requirements.txt
