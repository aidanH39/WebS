#
#
# ██╗    ██╗███████╗██████╗ ███████╗    ██████╗     ██████╗ 
# ██║    ██║██╔════╝██╔══██╗██╔════╝    ╚════██╗   ██╔═████╗
# ██║ █╗ ██║█████╗  ██████╔╝███████╗     █████╔╝   ██║██╔██║
# ██║███╗██║██╔══╝  ██╔══██╗╚════██║    ██╔═══╝    ████╔╝██║
# ╚███╔███╔╝███████╗██████╔╝███████║    ███████╗██╗╚██████╔╝
#  ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝    ╚══════╝╚═╝ ╚═════╝ 
#
#                                                         

import re
from io import TextIOWrapper
import socket # For gethostbyaddr()
import socketserver
from socketserver import  BaseRequestHandler
from typing import Any
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs, parse_qsl
import os
import threading
import asyncio
import json
import traceback
import time
import selectors
import types
import urllib
from logSystem import Logger, colors
import inspect

controlPanel = True
_init = False

# TODO: Add logging system

class WebS():
    """
        Creates a HTTP web server. Start the server with `start_server()`

        `fileWebServer` - Enable file hosting on the web server. Will allow requests to folders, and files within the working directory.
        
    """
    def __init__(self, ip="localhost", port=80, workingDirectory=os.getcwd(), fileWebServer=True):

        # Init vars
        self.endpoints = dict()
        self.ip = ip
        self.port = port
        self.fileWebServer = fileWebServer
        self.server_version = "WebS V2.0.0"
        self.errorDoc_funcs = dict()
        self.workingDirectory = workingDirectory
        self._cpServer = False
        self.accessFileEnabled = True

    def getLogger(self) -> Logger:
        return self._logger


    def start_server(self, newThread=False):
        """
        Start the web server
        `newThread` - If true starts the web server in a new thread. Can be useful to host multiple servers at once. Default: False
        """
        loop = asyncio.get_event_loop()
        
        global _init
        if not _init:
            print(colors.Fore.cyan + """


                ██╗    ██╗███████╗██████╗ ███████╗    ██████╗     ██████╗ 
                ██║    ██║██╔════╝██╔══██╗██╔════╝    ╚════██╗   ██╔═████╗
                ██║ █╗ ██║█████╗  ██████╔╝███████╗     █████╔╝   ██║██╔██║
                ██║███╗██║██╔══╝  ██╔══██╗╚════██║    ██╔═══╝    ████╔╝██║
                ╚███╔███╔╝███████╗██████╔╝███████║    ███████╗██╗╚██████╔╝
                ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝    ╚══════╝╚═╝ ╚═════╝ 

                                                        
                """ + colors.reset)

        self._logger = Logger(self)
        


        if controlPanel and not _init:
            # Create control panel
            cp_server = WebS("localhost", 2444, fileWebServer=False, workingDirectory=os.path.dirname(os.path.realpath(__file__)) + "/ControlPanel")
            cp_server._cpServer = True
            
            _init = True
            # Start control panel server
            cp_server.start_server(newThread=True)
            

        
        self.getLogger().info("Starting TCP server...")

        
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(False)
        self.server.bind((self.ip, self.port))
        self.server.listen(5)
        if self._cpServer:
            requestHandler = ControlPanelHandler(self)
            requestHandler._fileWebServer = self.fileWebServer
        else:
            requestHandler = RequestHandler(self)
            requestHandler._fileWebServer = self.fileWebServer
        self.sel = selectors.DefaultSelector()


        # Set up TCP server, and accept connection then register the selector
        def accept_wrapper(sock):
            conn, addr = sock.accept()  # Should be ready to read
            conn.setblocking(False)
            data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
            self.sel.register(conn, events, data=data)
            
            
        # Accept requests and start handling the requests in a new thread.
        def service_connection(key, mask):
            
            client = key.fileobj
            data = key.data
            if mask & selectors.EVENT_READ:
                try:
                    recv_data = client.recv(1024)  # Should be ready to read
                except ConnectionAbortedError as e:
                    return
                if recv_data:

                    def _newRequest():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        loop.run_until_complete(requestHandler.handle(client, recv_data, data.addr))
                        loop.close()
                    
                    _thread = threading.Thread(target=_newRequest)
                    _thread.start()

                     
                else:
                    self.sel.unregister(client)
                    client.close()
        
        # Runs the TCP server             
        def __run__():
            self.sel.register(self.server, selectors.EVENT_READ, data=None)        
            try:
                self.getLogger().info("Started HTTP Web Server on address '{0}'...".format((self.ip + ":" + str(self.port))))
                while True:
                    events = self.sel.select(timeout=None)
                    for key, mask in events:
                        if key.data is None:
                            accept_wrapper(key.fileobj)
                        else:
                            service_connection(key, mask)
            except KeyboardInterrupt:
                print("Caught keyboard interrupt, exiting")
            finally:
                self.sel.close()
        
        if newThread:
            # Run server in new thread
            def __handle_in_thread():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                asyncio.get_event_loop().run_until_complete(__run__())
                loop.close()
                

            thread = threading.Thread(target=__handle_in_thread)
            if self._cpServer:
                thread.setName("(Control Panel) Port: " + str(self.port))
            else:
                thread.setName("(Web Server) Port: " + str(self.port))
            thread.start()
        else:
            # Run server on current thread
            __run__()
            loop.close()
      
    def _templateFile(self):

        # TODO: Put these templates into HTML / CSS files to load from.

        # Light mode template
        lightMode = """

                    :root {
                        --elementBg: #f7f7f7;
                        --elementColor: black;
                    }

                    html {
                        transition: 1s all;
                    }

                    
                    
                    body {
                    transition: 1s all;
                        box-shadow: inset 0 0px 20px 20px #0000001a;
    margin: 0;

                        background: linear-gradient(227deg, #ffffff 20%, #ffffff, #9b9b9b);
                        background-size: 400% 400%;
                        color: black;

                        -webkit-animation: AnimationName 10s ease infinite;
                        -moz-animation: AnimationName 10s ease infinite;
                        animation: AnimationName 10s ease infinite;
                        font-family: sans-serif;
                    }

                    @-webkit-keyframes AnimationName {
                        0%{background-position:0% 51%}
                        50%{background-position:100% 50%}
                        100%{background-position:0% 51%}
                    }

                    @-moz-keyframes AnimationName {
                        0%{background-position:0% 51%}
                        50%{background-position:100% 50%}
                        100%{background-position:0% 51%}
                    }
                    @keyframes AnimationName {
                        0%{background-position:0% 51%}
                        50%{background-position:100% 50%}
                        100%{background-position:0% 51%}
                    }
                    .goback img {
                        transition: 1s all;
                    }
               

        """

        # Dark mode template
        darkMode = """

        
                
                    :root {
                        --elementBg: #00000014;
                        --elementColor: white;
                    }
                    html {
                        background: linear-gradient(227deg, rgb(39 38 38) 20%, rgb(25 25 25), #000000);
                        transition: 1s all;
                    }
                    body {
                    transition: 1s all;
                    box-shadow: inset 0 0px 20px 20px #0000001a;
    margin: 0;
                        
                        background-size: 400% 400%;
                        color: white;

                        -webkit-animation: AnimationName 10s ease infinite;
                        -moz-animation: AnimationName 10s ease infinite;
                        animation: AnimationName 10s ease infinite;
                        font-family: sans-serif;
                    }

                    @-webkit-keyframes AnimationName {
                        0%{background-position:0% 51%}
                        50%{background-position:100% 50%}
                        100%{background-position:0% 51%}
                    }

                    @-moz-keyframes AnimationName {
                        0%{background-position:0% 51%}
                        50%{background-position:100% 50%}
                        100%{background-position:0% 51%}
                    }
                    @keyframes AnimationName {
                        0%{background-position:0% 51%}
                        50%{background-position:100% 50%}
                        100%{background-position:0% 51%}
                    }

                    .goback img {
                        transition: 1s all;
                        filter: contrast(0) brightness(2);
                    }
                

        """

        return """

        <style id="css"></style>

        <script>
            function checkTheme() {{
                if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {{
                    // dark mode
                    document.getElementById("css").innerHTML = `{1}`;
                }} else {{
                    document.getElementById("css").innerHTML = `{0}`;
                }}
            }}

            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {{
                const newColorScheme = event.matches ? "dark" : "light";
                checkTheme();
            }});

            checkTheme();
        </script>



        """.format(lightMode, darkMode)



        

    def default_errorDocument(self, code, context):
        """
        Create default error document page
        """
        context.status = code
        description = ""
        if code == 404:
            description = "Page not found <span style='font-size: 18px; margin-left: 10px;'>:(</span>"
        elif code == 500:
            description = "Internal Server Error"

        return """
        {0}
        <body>
        
        <div style="text-align: center; font-family: sans-serif; padding-top: 80px;">
            <h1 style="font-weight: 900;">ERROR</h1>
            <h1 style="font-size: 56px; font-weight: 900;">{1}</h1>
            <p>{2}</p>
        </div>
        <p style="top: 0; right: 0; position: fixed; margin-right: 20px;">Server: {3}</p>

        

        """.format(self._templateFile(), code, description, self.server_version)
 
    def getErrorDocument(self, code, context):
        """
        Get registered error document, will look for pre defined error documents, else will load default template
        """
        if self.errorDoc_funcs.get(code) != None:
            return self.errorDoc_funcs.get(code)(context)
        else:
            return self.default_errorDocument(code, context)

    def parse_endpoint_route(self):
        pattern = re.compile(r"<[A-Za-z0-9]+>", re.IGNORECASE)
        return pattern.match(input_text)

    def error_document(self, code):
        """
        Decorator to create a error page landing.

        `code` - The status code of the error
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            self.errorDoc_funcs[code] = wrapper
        return decorator

    def endpoint(self, route):
        """
        Creates a REST API endpoint, allowing to return data back.
        Ideadly string or directory.
        """
        def decorator(func):
            
            async def wrapper(*args, **kwargs):
                c = inspect.iscoroutinefunction(func)
            
                # Catch async exceptions 
                if c:
                    return await func(*args, **kwargs)
                else:
                    self.getLogger().warning("Endpoint '{0}()' needs to be a async method.".format(func.__name__))
                    return func(*args, **kwargs)
                
            self.endpoints[route] = wrapper
        
        return decorator



class RequestContext:
    """
    Contains infomation about a request, allowing to modify the request return parameters as well.
    """

    def __init__(self, path, form, body):
        self.status = 200
        self.method = "GET"
        self._form = form
        self._httpVersion = ""
        self._path = path
        self.body = body
        self._headers = dict()
        self._ip = ""
        self.http_version = ""
        self._request = None

    @property
    def form(self):
        return self._form
    
    def getPath(self) -> str:
        """
        Get decoded path
        """
        return urllib.parse.unquote(self._path)
    
    def getIP(self) -> str:
        return self._ip[0]

    def getEncodedPath(self) -> str:
        """
        Get encoded path
        """
        return self._path

    def header(self, name) -> str:
        """
        Get response header value.
        """
        return self._headers[name]
    
    def getRequest(self):
        """
        Returns the Request object
        """
        return self._request

    def set_header(self, name, value):
        """
        Set response header value
        """
        self._headers[name] = value
    
    def redirect(self, location, code=301):
        """
        Redirect client to a different web page
        `location` - Location to redirec to
        `code` - Status code to return. Default: 301
        """
        self.status = code
        self.set_header("Location", location)
    

class Request():
    def __init__(self, client, context):
        self._client = client
        self._context = context
        self._context._request = self

    def getClient(self):
        return self._client
    
    def getContext(self) -> RequestContext:
        return self._context
        

class RequestHandler():
    def __init__(self, webs : WebS):
        self._headers = dict()
        self._fileWebServer = True
        self.webs = webs
        self._workingDirectory = webs.workingDirectory

    def getLogger(self) -> Logger:
        return self.webs.getLogger()

    async def handle(self, client, data, addr):
        """
        Handles incoming data to the server
        """
        async def __handle():
            requestd = data.decode().split("\r\n")

            httpRequest = requestd[0]
            _headersList = requestd[1:]
            headers = {}
            for header in _headersList:
                try:
                    i = header.split(": ")
                    headers[i[0]] = i[1]
                except:
                    break



            #body = request[:-1]
            body = "{}"
            
            _context = await self.parse_request(httpRequest, headers, body)
            _context._ip = addr
            request = Request(client, _context)
            await self.handle_request(request)
            self.getLogger().access(request)
            if request.getContext() == None:
                return
        
        def __handle_in_thread():
            asyncio.run(__handle())
            
        thread = threading.Thread(target=__handle_in_thread)
        thread.setName("(Handling Web Request) Thread " + str(threading.active_count() + 1))
        thread.start()
        
    
    async def directory_listing(self, request : Request):
        """
        Returns directory listing
        """
        content_list = ""
        
        folders = []
        files = []

        for file in os.listdir(self._workingDirectory + "/" + request.getContext().getPath()):
            if os.path.isdir(self._workingDirectory + "/" + request.getContext().getPath() + "/" + file):
                folders.append(file)
            else:
                files.append(file)


        p = request.getContext().getPath()
        if (p[-1] == "/"):
            p = p[:-1]
        
        if p != "":
            content_list += """
                    <a href="../" class="item goback">
                        <img style="    height: 34px;
    float: left;
    margin-right: 20px;
    margin-top: 8px;" src="https://cdn-icons-png.flaticon.com/512/0/340.png"> <p>Go Back</p>
                    </a>
                """

        for folder in folders:
            content_list += """
                    <a href="{0}" class="item">
                        <img style="    height: 34px;
    float: left;
    margin-right: 20px;
    margin-top: 8px;" src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/OneDrive_Folder_Icon.svg/640px-OneDrive_Folder_Icon.svg.png"> <p>/{1}</p>
                    </a>
                """.format(p + "/" + folder, folder)
            
        for file in files:
            content_list += """
                <a href="{0}" class="item">
                    <p>{1}</p>
                </a>
            """.format(p + "/" + file, file) 

        content = """
            <head>
                <title>Directory "{0}"</title>
                {3}    
            </head>
            
            <style>
                body {{
                    background: var(--elementBg) !important;
                }}
                .item {{
                    padding: 2px 0px 2px 15px;
                    display: block;
                    background: transparent;
                    margin: 2px;
                    color: var(--elementColor);
                    text-decoration: none;
                }}

                .item:hover {{
                    background: #007cff99;
                    cursor: pointer;
                }}
            </style>

            <div style="    padding: 40px;">
                <h2 style="    font-size: 30px;
    padding-bottom: 20px;">Directory "{0}"</h2>
                <div class="content">
                    {1}
                </div>
            </div>

            <p style="top: 0; right: 0; position: fixed; margin-right: 20px;">Server: {2}</p>

        """.format(request.getContext().getPath(), content_list, self.webs.server_version, self.webs._templateFile())

        await self.send_response(request, content)


    # Handle Request
    async def handle_request(self, request : Request):
        if not request.getContext():
            print("ERROR: NO CONTEXT")
            return
        
        if hasattr(self, "_fileWebServer") and self._fileWebServer:

            if os.path.isdir(self._workingDirectory + "/" + request.getContext().getPath()) and os.path.isfile(self._workingDirectory + "/" + request.getContext().getPath() + "/index.html"):
                request.getContext()._path += "/index.html"
        

            if os.path.isfile(self._workingDirectory + "/" + request.getContext().getPath()):
                file = open(self._workingDirectory + "/" + request.getContext().getPath(), "rb")
                data = file.read()
                await self.send_response(request, data)
                file.close()
                return
            elif os.path.isdir(self._workingDirectory + "/" + request.getContext().getPath()):
                if request.getContext().getPath()[-1:] != "/":
                    request.getContext().redirect(request.getContext().getPath() + "/")
                await self.directory_listing(request)
                return
        response = None
        try:
            if self.webs != None and self.webs.endpoints.get(request.getContext().getPath(), None) == None:
                response = self.webs.getErrorDocument(404, request.getContext())
                
            
            if self.webs != None and self.webs.endpoints.get(request.getContext().getPath(), None) != None:
                f = self.webs.endpoints.get(request.getContext().getPath(), None)
                c = inspect.iscoroutinefunction(f)
            
                # Catch async exceptions 
                if c:
                    response = await f(request.getContext())
                else:
                    self.getLogger().warning(request, "Endpoint '{0}' needs to be a async method.".format(request.getContext().getPath()))
                    response = f(request.getContext())
                    
        
            if response != None:
                if type(response) is dict:
                    request.getContext().set_header("Content-Type", "application/json")
                    await self.send_response(request, json.dumps(response))
                elif type(response) is str:
                    await self.send_response(request, response)
                elif type(response) is TextIOWrapper:
                    read = response.read()
                    response.close()
                    await self.send_response(request, read)
            else:
                print("test")
        except Exception as e:
            self.getLogger().error(request, traceback.format_exc())
            response = self.webs.getErrorDocument(500, request.getContext())
            await self.send_response(request, response)
                   

    async def parse_request(self, httpRequest, headers, body):
        try:

            # Read HTTP request header
            http_request_header = httpRequest.split()
            
            command = http_request_header[0]
            query = urlparse(http_request_header[1])
            http_version = http_request_header[2]



            form = {}
            if body == None:
                body = {}

            # Check for body content and decode it
            if headers.get("Content-Type", None) != None:
                if "application/x-www-form-urlencoded" in headers.get("Content-Type"):
                    p = parse_qs(body)
                    form = p
                elif "application/json" in headers.get("Content-Type"):
                    body = json.loads(body)
            
            # Check for GET parms
            if len(query.query) > 0:
                qs = parse_qs(query.query)
                form.update(qs)

            context = RequestContext(query.path, form, body)
            context.method = command
            context.http_version = http_version
            

            self._headers = dict()
            context._httpVersion = http_version
            return context
        except Exception as e:
            print("Error while handling request")
            print("Exception:")
            print(traceback.format_exc())
            return None

    def header(self, name, content):
        """Adds a header to the response"""
        self._headers[name] = content

    async def send_headers(self, request : Request):
        """
        Encode and send headers to the client.
        """

        self.header('Accept-Post', "*/*")
        self.header("Accept", "*/*")
        self.header('Server', "test v1.0.0")
        self.header('Date', "idk")
        self.header('Allow', "OPTIONS, GET, POST")
        self.header('Access-Control-Allow-Origin', "*")
        self.header('Access-Control-Allow-Headers', "*")
        self.header('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS")

        self._headers.update(request.getContext()._headers)

        # send headers
        buffer = []
        if request.getContext().method == "OPTIONS":
            request.getContext().status = 200
        buffer.append(("%s %d %s\r\n" %
                    (request.getContext()._httpVersion, request.getContext().status, "test")).encode(
                        'latin-1', 'strict'))
        
        for head, value in self._headers.items():
            buffer.append(bytes((head + ": " + value + "\r\n").encode("latin", "strict")))
        buffer.append(b"\r\n")

        self._headers.clear()
        try:
            request.getClient().send(b"".join(buffer))
        except:
            pass
    
    async def send_response(self, request : Request, content):
        """
        Sends a response to the client.
        Needs context, and body content to send
        """

        try:
            # Send headers first
            await self.send_headers(request)        
            # Send content as body
            if type(content) == bytes:
                request.getClient().send(content)
            else:
                request.getClient().send(bytes(content.encode()))
            self.webs.sel.unregister(request.getClient())
            request.getClient().close()
        except ConnectionAbortedError as e:
            return



class ControlPanelHandler(RequestHandler):

    def __init__(self, webs: WebS):
        super().__init__(webs)
        self.init_endpoints()


    def init_endpoints(self):
        @self.webs.endpoint("/")
        async def home(context):
            return open(self._workingDirectory + "/index.html", "r")

        @self.webs.endpoint("/dash")
        def dash(content):
            return open(self._workingDirectory + "/dash.html", "r")
        