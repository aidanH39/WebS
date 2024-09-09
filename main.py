import json
from typing import Tuple
from http import HTTPStatus
import os
from httpServer import WebS
from httpServer import RequestContext

# Create server object
api = WebS("localhost", port=80, workingDirectory=os.getcwd() + "/Server 1", fileWebServer=True)
api2 = WebS("localhost", port=2000, workingDirectory=os.getcwd() + "/Server 2", fileWebServer=True)




import time

# Endpoints

@api.endpoint("/api/empty")
async def empty_test(context):
    print("Sending nothing")

@api.endpoint("/api/server1")
def serv1(context):
    no()
    return "Server 1"

@api2.endpoint("/api/server2")
def serv2(context):
    return "Server 2"


@api.endpoint("/api/test")
async def test_endpoint(context):
    time.sleep(30)
    return {"test":"Success", "form": context.form, "body": context.body}

@api.endpoint("/api/login")
async def login_endpoint(context : RequestContext):
    body = context.body
    if (body.get("username", None) == None) or (body.get("password", None) == None):
        context.status = 400
        return {"error":"Invalid POST args"}
    if not os.path.isfile("users/" + body.get("username")):
        context.status = 401
        return {"status":401, "message":"Incorrect email or password"}

    file = open("users/" + body.get("username"), "r")
    data = json.loads(file.read())

    if body.get("password", None) == data["password"]:
        context.status = 200
        return {"success":"You have logged in as user \"{0}\"".format(body.get("username"))}
    else:
        context.status = 401
        return {"status":401, "message":"Incorrect email or password"}

@api.endpoint("/api/signup")
async def test_endpoint(context):

    body = context.form

    if (body.get("username", None) == None) or (body.get("password", None) == None):
        return {"error":"Invalid POST args"}

    if os.path.isfile("users/" + body.get("username")):
        return {"error":"User already exists"}

    file = open("users/" + body.get("username"), "w")
    file.write(json.dumps({"username": body.get("username"), "password": body.get("password")}))

    #if os.path.isfile(os.getcwd() + "/users/" + user)
    return {"status": "200", "username":body.get("username"), "password":body.get("password")}


# @api.error_document(404)
# def document404(context):
#     return "<h1>404</h1>"



if __name__ == "__main__":
    # Run the server
    api.start_server(newThread=True)
    #api2.start_server(newThread=False)