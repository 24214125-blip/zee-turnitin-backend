import urllib.parse
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 🔥 NOMOR WA LU SUDAH DIGANTI DAN DIATUR SUPAYA LANGSUNG MASUK CHAT
NOMOR_WA_OWNER = "6285928102713" 

@app.route('/api/order', methods=['POST'])
def process_manual_order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Data order kosong'}), 400
        
        wa_cust = data.get('whatsapp', '')
        jml_lembar = data.get('pages', '1')
        filters = data.get('filters', {})
        total_harga = data.get('total_price', 'Rp 7.000')
        isi_esai = data.get('text_content', '')

        # Batasi cuplikan esai biar chat WA tidak kepanjangan
        cuplikan_esai = isi_esai[:500] + "..." if len(isi_esai) > 500 else isi_esai

        # Susunan template pesan orderan rapi untuk admin
        template_chat = (
            f"🛒 *ZEE TURNITIN — NOTIFIKASI ORDER BARU* 🛒\n\n"
            f"📱 *Data Customer:*\n"
            f"   - No. WA Cust: {wa_cust}\n"
            f"   - Jumlah Lembar: {jml_lembar} Halaman\n\n"
            f"🛠️ *Request Settings Filter:*\n"
            f"   - Exclude Bibliography: {filters.get('excludeBib', 'Mati')}\n"
            f"   - Exclude Quotes: {filters.get('excludeQuotes', 'Mati')}\n"
            f"   - Exclude Methods: {filters.get('excludeMethods', 'Mati')}\n\n"
            f"💰 *Rincian Pembayaran:* \n"
            f"   - Total Biaya: *{total_harga}*\n"
            f"   - Metode: QRIS (Bukti Bayar Terlampir)\n\n"
            f"📝 *Isi/Cuplikan Dokumen Teks:* \n"
            f"\" {cuplikan_esai} \"\n\n"
            f"--- Mohon segera diproses ya Admin! ---"
        )

        # Encode teks agar aman dikirim via URL Link WhatsApp
        teks_encoded = urllib.parse.quote(template_chat)
        wa_api_url = f"https://api.whatsapp.com/send?phone={NOMOR_WA_OWNER}&text={teks_encoded}"

        print(f"\n✅ Sukses menyusun rincian order ke nomor admin baru!")
        return jsonify({
            'status': 'success',
            'whatsapp_url': wa_api_url
        })

    except Exception as e:
        print(f"❌ Eror backend: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)