import os
import urllib.parse
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# MAX LIMIT FILE 16MB BIAR BEBAS UPLOAD SKRIPSI GEDE
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

NOMOR_WA_OWNER = "6285928102713"

# ========================================================
# ⚙️ PENGATURAN TELEGRAM AUTOMATION (SUDAH DISET OTOMATIS)
# ========================================================
TELEGRAM_TOKEN = "8845893202:AAH6WhHbVbMRNOx2fj3iHxMM6trlkwXB_nQ"
TELEGRAM_CHAT_ID = "6827958357"
# ========================================================

@app.route('/api/order', methods=['POST'])
def process_file_order():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'File berkas tidak terdeteksi oleh server'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'Nama file yang diupload kosong'}), 400

        wa_cust = request.form.get('whatsapp', '')
        jml_lembar = request.form.get('pages', '1')
        total_harga = request.form.get('total_price', 'Rp 7.000')
        ex_bib = request.form.get('excludeBib', 'Mati')
        ex_quotes = request.form.get('excludeQuotes', 'Mati')
        ex_cited = request.form.get('excludeCited', 'Mati')
        m_words = request.form.get('matchWords', '8')

        filename = secure_filename(file.filename)
        
        # 1. KIRIM FILE ASLI (.docx/.pdf) LANGSUNG KE TELEGRAM PRIBADI LU VIA BOT
        file.seek(0) # Reset pointer file sebelum dikirim
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        caption_telegram = (
            f"🔔 *BERKAS MASUK DARI WEB ZEE TURNITIN* 🔔\n\n"
            f"📱 WA Customer: {wa_cust}\n"
            f"📄 Jumlah: {jml_lembar} Halaman\n"
            f"💰 Status: LUNAS ({total_harga})"
        )
        
        # Eksekusi kirim dokumen fisik asli ke Telegram
        files_data = {'document': (filename, file.read())}
        data_data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption_telegram, 'parse_mode': 'Markdown'}
        requests.post(telegram_url, files=files_data, data=data_data)

        # 2. FORMAT NOTA UNTUK DIBAWA CUSTOMER KE WHATSAPP LU
        template_chat = (
            f"🛒 *ZEE TURNITIN — PESANAN MASUK* 🛒\n\n"
            f"📱 *Data Customer:*\n"
            f"   - No. WA Cust: {wa_cust}\n"
            f"   - Jumlah Lembar: {jml_lembar} Halaman\n\n"
            f"📋 *Nama File Berkas:* \n"
            f"   👉 _{filename}_\n\n"
            f"🛠 *Setelan Filter Turnitin:*\n"
            f"   - Exclude Bibliography: {ex_bib}\n"
            f"   - Exclude Quoted: {ex_quotes}\n"
            f"   - Exclude Cited: {ex_cited}\n"
            f"   - Exclude Small Matches: {m_words} Words\n\n"
            f"💰 *Total Bayar:* *LUNAS ({total_harga})*\n\n"
            f"===============================\n"
            f"Hai Admin Zee Turnitin, saya sudah transfer. File berkas asli sudah terunggah otomatis ke server. Mohon diproses ya, bos! 🙏✨"
        )

        teks_encoded = urllib.parse.quote(template_chat)
        wa_api_url = f"https://api.whatsapp.com/send?phone={NOMOR_WA_OWNER}&text={teks_encoded}"

        return jsonify({
            'status': 'success',
            'whatsapp_url': wa_api_url
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)