import os
import urllib.parse
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

NOMOR_WA_OWNER = "6285928102713"
UPLOAD_FOLDER = '/tmp' # Folder aman sementara di cloud Render
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/order', methods=['POST'])
def process_file_order():
    try:
        # Cek apakah ada file yang diupload oleh customer
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'File berkas tidak ditemukan'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'Nama file kosong'}), 400

        # Ambil data form lainnya
        wa_cust = request.form.get('whatsapp', '')
        jml_lembar = request.form.get('pages', '1')
        total_harga = request.form.get('total_price', 'Rp 7.000')
        ex_bib = request.form.get('excludeBib', 'Mati')
        ex_quotes = request.form.get('excludeQuotes', 'Mati')
        ex_cited = request.form.get('excludeCited', 'Mati')
        m_words = request.form.get('matchWords', '8')

        # Simpan file secara aman di server Render
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # LINK UNDUHAN (Sementara memanfaatkan nama file asli agar tersimpan di sistem data)
        # Catatan: Karena ini di server Render free, link ini berlaku internal. 
        # Customer akan membawa nama file asli yang valid di dalam chat WA Anda!
        
        template_chat = (
            f"🛒 *ZEE TURNITIN — PESANAN MASUK ULA* 🛒\n\n"
            f"📱 *Data Customer:*\n"
            f"   - No. WA Cust: {wa_cust}\n"
            f"   - Jumlah Lembar: {jml_lembar} Halaman\n\n"
            f"📋 *Nama File Berkas Anda:*\n"
            f"   👉 _{filename}_\n\n"
            f"🛠️ *Setelan Filter Turnitin:*\n"
            f"   - Exclude Bibliography: {ex_bib}\n"
            f"   - Exclude Quoted: {ex_quotes}\n"
            f"   - Exclude Cited: {ex_cited}\n"
            f"   - Exclude Small Matches: {m_words} Words\n\n"
            f"💰 *Total Bayar:* *LUNAS ({total_harga})*\n\n"
            f"===============================\n"
            f"Hai Admin Zee Turnitin, saya sudah transfer. Mohon diproses file skripsi saya di atas ya! Terima kasih! 🙏✨"
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