from flask import Flask, render_template, request, Response
import threading
import queue
import kick   # kick.py içindeki fonksiyonları kullanacağız

app = Flask(__name__)

log_queue = queue.Queue()   # Çıktıları siteye aktarmak için

# kick.py içindeki print() yerine kullanılacak fonksiyon
def log(message):
    log_queue.put(message)

# Botu başlatan wrapper
def start_bot(channel, viewers):
    kick.run(viewers, channel, logger=log)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        channel = request.form.get("channel")
        viewers = int(request.form.get("viewers"))

        t = threading.Thread(target=start_bot, args=(channel, viewers))
        t.daemon = True
        t.start()

        return render_template("index.html", started=True)

    return render_template("index.html", started=False)


# Canlı log yayını
@app.route("/stream")
def stream():
    def event_stream():
        while True:
            msg = log_queue.get()
            yield f"data: {msg}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True)
