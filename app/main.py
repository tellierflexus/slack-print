from flask import Flask, request, Response
import requests
import logging
import os
import sys
import cups
from threading import Thread
from functools import wraps
import hmac
import time

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)



def check_signature(f): 
    @wraps(f)
    def wrap(*args, **kwargs):
        def refused(*args, **kwargs):
            return "Not authorized", 403

        if os.environ.get('slack-print-mode') == "dev":
            return func(*args, **kwargs)

        if request.headers is not None and 'X-Slack-Request-Timestamp' in request.headers:
            timestamp = request.headers['X-Slack-Request-Timestamp']
        else:
            return refused(*args, **kwargs)

        if abs(time.time() - timestamp) > 60 * 5: #Too old request, it may be a replay attack (well according to slack)
            return refused(*args, **kwargs)

        sig_basestring = 'v0:' + timestamp + ':' + request_body
        slack_signing_secret = os.environ.get('slack-print-signing')
        my_signature = 'v0=' + hmac.compute_hash_sha256(slack_signing_secret,sig_basestring).hexdigest()
        slack_signature = request.headers['X-Slack-Signature']

        if hmac.compare(my_signature, slack_signature):
            return func(*args, **kwargs)
        else:
            app.logger.warning("Signature not matching !")
            return refused(*args, **kwargs)
    return wrap



    return refused

def download(files):
    if os.environ.get('slack-print-token') is not None:
        token = os.environ.get('slack-print-token')
    else:
        token = ""
    r = requests.get(files["url_private_download"], headers={'Authorization': 'Bearer %s' % token})
    open(files['title'], 'wb').write(r.content)  
    print_file(files['title'])

def print_file(path):
    cups.setServer ("192.168.2.118:632")
    conn = cups.Connection()
    printers = conn.getPrinters()
    #printer_name = printers.keys()[0]
    printer_name = "Redaction"
    conn.printFile(printer_name,path,"",{})    



@app.route("/event",  methods=['GET', 'POST'])
@check_signature
def event():
    
    if request.json is not None: 
        content = request.json

        if os.environ.get('slack-print-mode') == "dev":
            print(content, flush=True)
            if "challenge" in content:
                return content['challenge'], 200

        if "event" in content:
            if "files" in content['event']:
                files = content['event']['files'][0] 
                
                app.logger.info("New file sent " + str(files['title']))
                thread = Thread(target=download, args=[files])
                thread.start()
                    
                return Response(status=200)

    return Response(status=201)

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port='80')