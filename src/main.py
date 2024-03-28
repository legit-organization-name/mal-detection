import traceback
from flask import Flask, request, Response

from src.ingest import process_webhook

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def respond():
    try:
        report = process_webhook(request.json, request.headers)
    except Exception as e:
        print(f"Error processing webhook: {traceback.format_exc()}")
        return Response(status=500)

    if report is not None:
        report.printout()

    return Response(status=200)
