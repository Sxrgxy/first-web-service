# run docker app
docker-compose up
# run bash/other prog of the containre command
docker exec -it flask-hello_flask_1 bash
docker exec -it flask-hello_flask_1 python train_model.py
# show all docker running processes
docker ps
# posting (POST) JSON data with cURL?
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"flower":"1,2,3,4"}' \ 
  http://localhost:5000/iris_post