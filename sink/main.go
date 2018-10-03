package main

import (
	"flag"
	"github.com/gocelery/gocelery"
	"github.com/kataras/iris"
	"io/ioutil"
	"log"
)

/**
Define global connectors to RabbitMQ with Celery backend
 */
var celeryBroker = gocelery.NewAMQPCeleryBroker("amqp://guest:guest@localhost:5672/")
var celeryBackend = gocelery.NewAMQPCeleryBackend("amqp://guest:guest@localhost:5672/")

/**
Process errors and write message to logs
 */
func failOnError(err error, msg string, ctx iris.Context) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
		ctx.JSON(iris.Map{
			"result": "fail",
			"msg":    "Failed to get payload from POST body",
		})
		//panic(fmt.Sprintf("%s: %s", msg, err))
	}
}

/**
Initialize app
 */
func init() {
	flag.Parse()
}

/**
Catcher handler
 */
func receive(ctx iris.Context) {

	// Get JSON payload
	rawBodyAsBytes, err := ioutil.ReadAll(ctx.Request().Body)
	if err != nil {
		failOnError(err, "Failed to get payload from POST body", ctx)
	}

	// Initialize celery Client and push task to Celery queue
	celeryClient, _ := gocelery.NewCeleryClient(celeryBroker, celeryBackend, 0)
	asyncResult, err := celeryClient.Delay("broker.catch", rawBodyAsBytes)
	_ = asyncResult

	if err != nil {
		failOnError(err, "Failed to Publish on RabbitMQ", ctx)
	} else {
		ctx.JSON(iris.Map{
			"result": "success",
		})
	}

}

/**
Initialize HTTP server
 */
func main() {
	app := iris.Default()

	// Define python catcher for now
	app.Post("/catcher/python", receive)

	// listen and serve on http://0.0.0.0:8081.
	app.Run(iris.Addr(":8081"))
}
