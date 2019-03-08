# -*- coding:utf8 -*-
"""VC HTTP Server.

This module builds on BaseHTTPServer by implementing the standard GET
 POST and HEAD requests in a fairly straightforward manner.

"""

__version__ = "0.1"

__all__ = ["CRHTTPRequestHandler"]

import os
import sys
import cgi
import time
import shutil
import base64
import logging
import mimetypes
import posixpath

from PIL import Image
from io import BytesIO
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

from CaptchaHelper import captcha_init

class CRHTTPRequestHandler(BaseHTTPRequestHandler):

    """Simple HTTP request handler with GET and HEAD commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method.

    The GET and HEAD requests are identical except that the HEAD
    request omits the actual contents of the file.

    """
    server_version = "CRHTTP/" + __version__
    def do_POST(self):
        """Serve a POST request."""

        global cr_config

        ctype, pdict = cgi.parse_header(self.headers.get('Content-type'))
        dicts={}

        for key in pdict.keys():
            dicts[key]= bytes(pdict[key], encoding = "utf8")

        body = {}
        length = int(self.headers.get('Content-Length'))

        if ctype == 'multipart/form-data':
            body = cgi.parse_multipart(self.rfile, dicts)
        elif ctype == 'application/x-www-form-urlencoded':
            qs = self.rfile.read(length)
            body = cgi.parse_qs(qs, keep_blank_values=1)
        else:
            body = {}

        if 'type' in body.keys():
            captcha_type = str(body['type'][0], encoding='utf-8')
        else:
            captcha_type = ''

        if 'pic' in body.keys():
            b64_img = str(body['pic'][0], encoding='utf-8')
        else:
            b64_img = ''

        if len(captcha_type) > 0 and len(b64_img) > 0:
            logger.info(captcha_type + ':' + b64_img)
            bytes_img = base64.b64decode(b64_img)
            image = Image.open(BytesIO(bytes_img))
            handler, recogn_ner = cr_config[captcha_type]
            sub_images = handler.handle(image)

            if len(sub_images) > 0:
                capcha_text = ''.join(recogn_ner.predict(sub_images))
            else:
                capcha_text = '0000'
        else:
            capcha_text = '0000'

        f = BytesIO()
        f.write(bytes(capcha_text, encoding="utf8"))

        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        
        self.copyfile(f, self.wfile)
        f.close()

    def do_GET(self):
        f = BytesIO()
        f.write(bytes('welcome.', encoding="utf8"))
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        self.copyfile(f, self.wfile)
        f.close()

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

logger = None
cr_config = {}
httpd = None

def init_logger(log_dir='/home/jupyter/ocr/src/',
                log_file_name=time.strftime('%Y%m%d', time.localtime(time.time())) + '.log',
                log_type=logging.INFO):
    global logger

    log_file = log_dir + '/' + log_file_name

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    logger = logging
    logger.basicConfig(
        filename=log_file,
        level=log_type
    )

def start(hostname, port, captcha_config, log_dir):

    global httpd
    global cr_config

    init_logger(log_dir=log_dir)
    cr_config = captcha_init(captcha_config)
    handler = CRHTTPRequestHandler
    httpd = HTTPServer((hostname,port), handler)
    httpd.serve_forever()
    
def stop():

    global httpd

    httpd.shutdown()

if __name__ == '__main__':

    #args = list(sys.argv)
    args = [sys.argv[0],
            '192.168.2.10',
            8000,
            '{"ntsms" : ("NTSMSCaptchaHandler", "SVMCaptchaRecognitioner", "C:/workspace/python/captcha2/model/ntsms/1495605689_model.bin", "C:/workspace/python/captcha2/model/ntsms/1495605689_index_label.bin")}',
            'C:/workspace/python/captcha2/log']

    if len(args) == 2:

        hostname = '0.0.0.0'
        port = 8000
        captcha_config = args[1]
        log_dir = './'
        start(hostname, port, captcha_config, log_dir)

    elif len(args) == 5:

        hostname = args[1]
        port = int(args[2])
        captcha_config = args[3]
        log_dir = args[4]
        start(hostname, port, captcha_config, log_dir)

    else:
        print(args, 'error args!')
