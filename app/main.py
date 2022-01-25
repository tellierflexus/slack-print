from flask import Flask, request, Response
import os

app = Flask(__name__)

@app.route("/event",  methods=['GET', 'POST'])
def event():
    if os.environ.get('docker-slack-cups') != "dev":
        return Response(status=201)

    if request.json is not None: 
        content = request.json
        print(content)
        if "challenge" in request.json:
            return content['challenge'], 200
        return Response(status=200)
        
    return Response(status=201)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')