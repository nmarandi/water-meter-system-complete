from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
import lib.ZaehlerstandClass
import os
import subprocess
import cgi, cgitb
import socketserver

import gc

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        global wasserzaehler
        url_parse = parse.urlparse(self.path)
        query_parse = parse.parse_qs(url_parse.query)

        if 'reload' in url_parse.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            result = 'Konfiguration wird neu geladen'
            self.wfile.write(bytes(result, 'UTF-8'))             
            del wasserzaehler
            gc.collect()
            wasserzaehler = lib.ZaehlerstandClass.Zaehlerstand()
            return
           

        if "/image_tmp/" in url_parse.path:
            self.send_response(200)
            size = str(os.stat('.'+self.path).st_size)
            self.send_header('Content-type', 'image/jpg')
            self.send_header('Content-length', size)
            self.end_headers()
            with open('.'+self.path, 'rb') as file: 
                self.wfile.write(file.read()) # Read the file and send the contents
            return

        url = ''
        if 'url' in query_parse:
            url = query_parse['url'][0]

        simple = True
        if ('&full' in self.path) or ('?full' in self.path):
            simple = False

        single = False
        if ('&single' in self.path) or ('?single' in self.path):
            single = True

        usePrevalue = False
        if ('&usePreValue' in self.path) or ('?usePreValue' in self.path) or ('&usePrevalue' in self.path) or ('?usePrevalue' in self.path):
            usePrevalue = True

        value = ''
        if 'value' in query_parse:
            value = query_parse['value'][0]

        if ('crash' in url_parse.path):
            a = 1
            b = 0
            c = a / b
            return

        if ('version' in url_parse.path) or ('ROI' in url_parse.path):
            result = "Version 6.1.1 (2020-04-23)"
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(result, 'UTF-8'))
            return

        if ('crash' in url_parse.path):
            result = "Crash in a second"
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(result, 'UTF-8'))
            print('Crash with division by zero!')
            a = 1
            b = 0
            c = a/b
            return

        if ('roi' in url_parse.path) or ('ROI' in url_parse.path):
            result = wasserzaehler.getROI(url)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(result, 'UTF-8'))
            return

        if 'setPreValue' in url_parse.path:
            result = wasserzaehler.setPreValue(value)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(result, 'UTF-8'))
            return

        if 'wasserzaehler.json' in url_parse.path:
            result = wasserzaehler.getZaehlerstandJSON(url, simple, usePrevalue, single)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(result, 'UTF-8'))
            return

        if 'wasserzaehler' in url_parse.path:
            result = wasserzaehler.getZaehlerstand(url, simple, usePrevalue, single)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(result, 'UTF-8'))
            return
    
    def do_POST(self):
        global wasserzaehler
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                         'CONTENT_TYPE':self.headers['Content-Type'],
                         })
        data = form['orig'].file.read()
        result = wasserzaehler.getZaehlerstandPOST(data)
        self.end_headers()
        self.wfile.write(bytes(result, 'UTF-8'))

if __name__ == '__main__':

    wasserzaehler = lib.ZaehlerstandClass.Zaehlerstand()

    PORT = 3300
    with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
        print("Wasserzaehler is serving at port", PORT)
        httpd.serve_forever()
