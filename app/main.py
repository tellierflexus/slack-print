from flask import Flask, request, Response
import os
import sys

app = Flask(__name__)

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
                app.logger.info('This is info output')
                return Response(status=200)

    return Response(status=201)

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port='80')