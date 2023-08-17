@echo off

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
python -m pip install --upgrade pip

pip install numpy
pip install pandas
pip install psycopg2
pip install sqlalchemy
pip install asammdf
pip install pyarrow

echo:
echo =======================
echo Installation completed!
pause