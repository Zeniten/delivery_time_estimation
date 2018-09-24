if [ ! -d "venv" ]; then
    virtualenv venv -p python3
fi
source venv/bin/activate
pip install -r requirements.txt
python deliverytimes.py
