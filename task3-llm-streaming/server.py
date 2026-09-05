# Mock LLM Server

from flask import Flask, Response
import time

app = Flask(__name__)


@app.route("/v1/completions", methods=["POST"])
def completions():
    chunks = [
        "Hello, my name is Swapnil. ",
        "You can reach me at swapnil",
        "@gmail.com or call ",
        "my office. My SSN is 123",
        "-45-6789 and my card ",
        "number is 4111-1111-",
        "1111-1111. Thanks!",
    ]

    def generate():
        for chunk in chunks:
            yield chunk
            time.sleep(0.1)

    return Response(generate(), content_type="text/plain")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9001)