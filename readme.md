# Python OCR

## First step

 python3 -m venv venv
 source venv/bin/activate
 pip install -r requirements.txt

## Running local
  uvicorn main:app --reload

## Running in docker - recommended
  docker-compose up --build  