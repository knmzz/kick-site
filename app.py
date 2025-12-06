from flask import Flask, render_template, request, Response
import threading
import queue
import kick   # kick.py içindeki fonksiyonları kullanıyoruz

app = Flask(__name__)

# Logları almak için kullanılan Queue
log_queue = queue.Queue()

# Log mesajlarını Queue'ya ekleyecek fonksiyon
def log(message):
    log_queue.put(message)

# Botu başlatan fonksiyon
def start_bot(channel, viewers):
    kick.run(viewers, channel, logger=log)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        channel = request.form.get("channel")
        viewers = int(request.form.get("viewers"))

        # Botu arka planda çalıştırmak için thread başlatıyoruz
        t = threading.Thread(target=start_bot, args=(channel, viewers))
        t.daemon = True
        t.start()

        return render_template("index.html", started=True, channel=channel, viewers=viewers)

    return render_template("index.html", started=False)

# Logları web'e canlı yayınlamak için EventStream
@app.route("/stream")
def stream():
    def event_stream():
        while True:
            msg = log_queue.get()
            yield f"data: {msg}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
