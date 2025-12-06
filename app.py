from flask import Flask, render_template, request
import threading
import kick  # kick.py dosyasını buraya import ediyoruz

app = Flask(__name__)

bot_thread = None  # Botu başlatacak thread

# Botu başlatmak için bir fonksiyon
def start_bot(channel, viewers):
    kick.run(viewers, channel)  # kick.py'yi kullanarak botu başlatıyoruz

# Ana sayfa
@app.route("/", methods=["GET", "POST"])
def index():
    global bot_thread

    if request.method == "POST":  # Eğer form submit edilmişse
        channel = request.form.get("channel")  # Kanal adı
        viewers = int(request.form.get("viewers"))  # İzleyici sayısı

        # Yeni bir thread başlatıyoruz
        bot_thread = threading.Thread(target=start_bot, args=(channel, viewers))
        bot_thread.daemon = True  # Thread backgroundda çalışacak
        bot_thread.start()

        return "Bot başlatıldı! Terminale bakabilirsin."

    # Ana sayfa render ediliyor
    return render_template("index.html")

# Flask uygulamasını çalıştırma
if __name__ == "__main__":
    app.run(debug=True)
