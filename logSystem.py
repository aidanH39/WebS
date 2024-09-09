import sys
import os

class colors:
    reset = '\033[0m'
    bold = '\033[01m'
    underline = '\033[04m'
    strikethrough = '\033[09m'
 
    class Fore:
        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        orange = '\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        lightgrey = '\033[37m'
        darkgrey = '\033[90m'
        lightred = '\033[91m'
        lightgreen = '\033[92m'
        yellow = '\033[93m'
        lightblue = '\033[94m'
        pink = '\033[95m'
        lightcyan = '\033[96m'

class Logger():

    def __init__(self, server):
        self._cpServer = server._cpServer
        if not os.path.isdir(os.getcwd() + "/logs"):
            os.mkdir(os.getcwd() + "/logs")
        
        
        self._fwrite = open(os.getcwd() + "/logs/" + server.ip + "-" + str(server.port) + ".log", "a", encoding="utf-8")
        self._fwrite.write("""         

    ██╗    ██╗███████╗██████╗ ███████╗    ██████╗     ██████╗ 
    ██║    ██║██╔════╝██╔══██╗██╔════╝    ╚════██╗   ██╔═████╗
    ██║ █╗ ██║█████╗  ██████╔╝███████╗     █████╔╝   ██║██╔██║
    ██║███╗██║██╔══╝  ██╔══██╗╚════██║    ██╔═══╝    ████╔╝██║
    ╚███╔███╔╝███████╗██████╔╝███████║    ███████╗██╗╚██████╔╝
    ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝    ╚══════╝╚═╝ ╚═════╝ 
                                                      
              
                           
""")
        self.info("Started logging for server `" + server.ip + ":" + str(server.port) + "`...")
        
        

    def access(self, request):
        prefix = ""
        if self._cpServer:
            prefix = colors.bold + colors.Fore.lightgreen + "[CP] " + colors.reset

        print(prefix + colors.reset + "["+ colors.Fore.lightgreen + "ACCESS" + colors.reset + "] {0} | {1} {2} ({3}) {4}".format(request.getContext().getIP(), request.getContext().http_version, request.getContext().status, request.getContext().method, request.getContext().getPath()))
        self._fwrite.write(prefix + "[ACCESS] {0} | {1} {2} ({3}) {4}\n".format(request.getContext().getIP(), request.getContext().http_version, request.getContext().status, request.getContext().method, request.getContext().getPath()))
        self._fwrite.flush()

    def warning (self, message, request=None):
        prefix = ""
        if self._cpServer:
            prefix = colors.bold + colors.Fore.lightgreen + "[CP] " + colors.reset

        print(prefix + colors.reset + "["+ colors.Fore.yellow + "WARNING" + colors.reset + "] {0}".format(message))
        self._fwrite.write(prefix + "[WARNING] {0}\n".format(message))
        self._fwrite.flush()

    def error(self, message, request=None):
        prefix = ""
        if self._cpServer:
            prefix = colors.bold + colors.Fore.lightgreen + "[CP] " + colors.reset

        if request == None:
            print(prefix + colors.reset + "["+ colors.Fore.lightred + "ERROR" + colors.reset + "] {0}".format(message))
            self._fwrite.write(prefix + "[ERROR] {0}\n".format(message))
        else:
            print(prefix + colors.reset + "["+ colors.Fore.lightred + "ERROR" + colors.reset + "] {0} | Error while handling request : {1}".format(request.getContext().getIP(), message))
            self._fwrite.write(prefix + "[ERROR] {0} | Error while handling request : {1}\n".format(request.getContext().getIP(), message))
        self._fwrite.flush()

    def info(self, message):
        prefix = ""
        if self._cpServer:
            prefix = colors.bold + colors.Fore.lightgreen + "[CP] " + colors.reset
            print(prefix + colors.reset + "["+ colors.Fore.cyan + "INFO" + colors.reset + "] {0}".format(message))
            self._fwrite.write(prefix + "[INFO] {0}\n".format(message))
        else:
            print(colors.reset + "["+ colors.Fore.cyan + "INFO" + colors.reset + "] {0}".format(message))
            self._fwrite.write(prefix + "[INFO] {0}\n".format(message))
        
        
        self._fwrite.flush()

if sys.platform == 'win32':
    
    if 'TERM_PROGRAM' not in os.environ.keys() or os.environ['TERM_PROGRAM'] != 'vscode':
        colors.Fore.black = ''
        colors.Fore.red = ''
        colors.Fore.green = ''
        colors.Fore.orange = ''
        colors.Fore.blue = ''
        colors.Fore.purple = ''
        colors.Fore.cyan = ''
        colors.Fore.lightgrey = ''
        colors.Fore.darkgrey = ''
        colors.Fore.lightred = ''
        colors.Fore.lightgreen = ''
        colors.Fore.yellow = ''
        colors.Fore.lightblue = ''
        colors.Fore.pink = ''
        colors.Fore.lightcyan = ''
        colors.reset = ''
        colors.bold = ''
        colors.underline = ''
        colors.strikethrough = ''