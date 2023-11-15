@echo off

winget install --id=Python.Python.3.x
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
python -m pip install --upgrade pip

pip install numpy
pip install pandas
pip install psycopg2
pip install sqlalchemy
pip install asammdf
pip install pyarrow
pip install can_decoder
pip install canedge_browser
pip install mdf_iter
pip install pytz
pip install tk
pip install tkcalendar
pip install customtkinter
pip install packaging

echo:
echo =======================
echo Installation completed!
pause