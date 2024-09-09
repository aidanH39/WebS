import http.server
import socketserver
from http import HTTPStatus
from typing import Tuple
import json
from functools import partial, wraps
import traceback
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs, parse_qsl

class RequsetContext:

    def __init__(self):
        self._status = 200
        self._form = dict()
        
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, code):
        self._status = code

    @property
    def form(self):
        return self._form
    



class WebS_Handler(http.server.CGIHTTPRequestHandler):

    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
        super().__init__(request, client_address, server)

    def do_POST(self):
        self.send_response(200)

        content_type = "text/html"

        self.send_header("Content-Type", content_type)
        self.end_headers()
            
        self.wfile.write(bytes("test".encode()))


    def do_GET(self):
        try:
            self.server_version = "WebS 1.0.0"
            self.sys_version = ""

            urlparsed = urlparse(self.path)
            path = urlparsed.path

            context = RequsetContext()
            params = urlparsed.query
            try :
                if params != None:
                    params = dict ( [ tuple ( p.split("=") ) for p in params[0:].split ( "&" ) ] )
                    context._form = params
            except:
                pass
        
            response = None     
            
            if self.webs.endpoints.get(path, None) != None:
                response = self.webs.endpoints.get(path, None)(context)

            if response == None:
                response = self.webs.getErrorDocument(404, context)
            
            self.send_response(context.status)

            content_type = "text/html"
            if type(response) == dict:
                response = json.dumps(response)
                content_type = "application/json"

            self.send_header("Content-Type", content_type)
            self.end_headers()
                
            self.wfile.write(bytes(response.encode()))
        except Exception as e:
            print("Exception:" + "\n" + traceback.format_exc())
            context = RequsetContext()
            response = self.webs.getErrorDocument(500, context)
                
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            content_type = "text/html"
            if type(response) == dict:
                response = json.dumps(response)
                content_type = "application/json"

            self.send_header("Content-Type", content_type)
            self.end_headers()
                
            self.wfile.write(bytes(response.encode()))

        
            
            
            

        


class WebS:

    def __init__(self):
        self.endpoints = dict()
        self.errorDoc_funcs = dict()
        self.server_version = "WebS 1.0.0"
        self.sys_version = ""


    def endpoint(self, route):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            self.endpoints[route] = wrapper
        return decorator

    def default_errorDocument(self, code, context):
        context.status = code
        description = ""
        if code == 404:
            description = "Page not found <span style='font-size: 18px; margin-left: 10px;'>:(</span>"
        elif code == 500:
            description = "Internal Server Error"

        return """
        <body style="color: white;" class="css-selector">
        <div style="text-align: center; font-family: sans-serif; padding-top: 80px;">
            <h1 style="font-size: 56px; font-weight: 900;">{0}</h1>
            <p>{1}</p>
        </div>
        <div style="bottom: 0; font-family: sans-serif; position: absolute; font-size: 12px;">
            <p>Server: {2}</p>
        </div>


        <style>

            .css-selector {{
                background: linear-gradient(227deg, #b400ff 20%, #036ff9, #036ff9);
                background-size: 400% 400%;

                -webkit-animation: AnimationName 10s ease infinite;
                -moz-animation: AnimationName 10s ease infinite;
                animation: AnimationName 10s ease infinite;
            }}

            @-webkit-keyframes AnimationName {{
                0%{{background-position:0% 51%}}
                50%{{background-position:100% 50%}}
                100%{{background-position:0% 51%}}
            }}

            @-moz-keyframes AnimationName {{
                0%{{background-position:0% 51%}}
                50%{{background-position:100% 50%}}
                100%{{background-position:0% 51%}}
            }}
            @keyframes AnimationName {{
                0%{{background-position:0% 51%}}
                50%{{background-position:100% 50%}}
                100%{{background-position:0% 51%}}
            }}

        </style>
        

        """.format(code, description, self.server_version)

    def getErrorDocument(self, code, context):
        if self.errorDoc_funcs.get(code) != None:
            return self.errorDoc_funcs.get(code)(context)
        else:
            return self.default_errorDocument(code, context)

    def error_document(self, code):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            self.errorDoc_funcs[code] = wrapper
        return decorator
            


    def start_server(self, port=80):
        
        self.httpServer = socketserver.TCPServer(("0.0.0.0", port), WebS_Handler)
        self.httpServer.RequestHandlerClass.webs = self
        print(f"Web Server started on port {port}")
        self.httpServer.serve_forever()
        