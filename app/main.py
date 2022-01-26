from flask import Flask, request, Response
import requests
import logging
import os
import sys
import cups

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


async def download(files):
    if os.environ.get('token-slack') is not None:
        token = os.environ.get('token-slack')
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
    printer_name = "Virtual"
    conn.printFile(printer_name,path,"",{})    



@app.route("/event",  methods=['GET', 'POST'])
def event():
    
    if request.json is not None: 
        content = request.json

        if os.environ.get('docker-slack-cups') == "dev":
            print(content, flush=True)
            if "challenge" in content:
                return content['challenge'], 200

        if "event" in content:
            if "files" in content['event']:
                files = content['event']['files'][0] 
                
                app.logger.info("New file sent " + str(files['title']))
                download(files)
                    
                return Response(status=200)

    return Response(status=201)

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port='80')