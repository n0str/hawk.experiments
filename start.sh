docker run -d --hostname rabbit --name hawk -p 5672:5672 -p 5671:5671 -p 8080:15672 rabbitmq:3-management
docker run --name hawk-mongo -d -p 27017:27017 -v mongo:/tmp/mongo -e DATA_DIR=/tmp/mongo mongo
