From python:3.10
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python3", "setting.py"]