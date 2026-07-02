import urllib.parse
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

NOMOR_WA_OWNER = "6285928102713" 

@app.route('/api/order', methods=['POST'])
def process_manual_order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Data kosong'}), 400
        
        wa_cust = data.get('whatsapp', '')
        jml_lembar = data.get('pages', '1')
        total_harga = data.get('total_price', 'Rp 7.000')
        filters = data.get('filters', {})
        isi_esai = data.get('text_content', '')

        # Format pesan WA rapi dengan melampirkan teks esai utuh di bawahnya
        template_chat = (
            f"🛒 *ZEE TURNITIN — DATA PESANAN BARU* 🛒\n\n"
            f"📱 *Data Customer:*\n"
            f"   - No. WA Cust: {wa_cust}\n"
            f"   - Jumlah Lembar: {jml_lembar} Halaman\n\n"
            f"🛠️ *Request Settings Filter Turnitin:*\n"
            f"   - Exclude Bibliography: {filters.get('excludeBib', 'Mati')}\n"
            f"   - Exclude Quoted: {filters.get('excludeQuotes', 'Mati')}\n"
            f"   - Exclude Cited: {filters.get('excludeCited', 'Mati')}\n"
            f"   - Exclude Small Matches: {filters.get('matchWords', '8')} Words\n\n"
            f"💰 *Status Pembayaran:* *LUNAS ({total_harga})*\n\n"
            f"===============================\n"
            f"📝 *ISI FILE ESAI UTUH CUSTOMER (SIAP COPY-PASTE):*\n"
            f"===============================\n\n"
            f"{isi_esai}"
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