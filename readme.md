# this is boilerplate all subject to change! 

You must install docker desktop for this project


to run cd into /app/
python -m venv venv
activate venv based on your computer 
pip install -r requirements.txt

docker run -d --name mongo -p 27017:27017 mongo

uvicorn main:app --reload

server at http://127.0.0.1:8000