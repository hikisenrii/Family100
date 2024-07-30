Tentu! Berikut adalah template `README.md` yang detail untuk proyek Python Anda, siap untuk digunakan dalam deploy ke Heroku. Ini mencakup instruksi mulai dari persiapan lokal hingga langkah-langkah deploy ke Heroku.

# Super Family 100 Bot

Bot Telegram untuk memainkan permainan Super Family 100.

## Fitur

- Mulai permainan dengan mengetik `/play`
- Menyerah dari permainan dengan mengetik `/nyerah`
- Mendapatkan pertanyaan berikutnya dengan mengetik `/next`
- Melihat statistik pribadi dengan mengetik `/stats`
- Melihat top skor global dengan mengetik `/top`
- Melihat top skor grup dengan mengetik `/topgrup`
- Melihat aturan bermain dengan mengetik `/peraturan`
- Mendapatkan bantuan dengan mengetik `/help`

## Persyaratan

- Python 3.9 atau lebih baru
- Dependensi yang tercantum di `requirements.txt`

## Instalasi

1. Clone repository ini:
    ```sh
    git clone https://github.com/username/super-family-100-bot.git
    cd super-family-100-bot
    ```

2. Buat dan aktifkan virtual environment (opsional tetapi direkomendasikan):
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # Linux/Mac
    .\venv\Scripts\activate   # Windows
    ```

3. Instal dependensi:
    ```sh
    pip install -r requirements.txt
    ```

4. Buat file `.env` di root direktori proyek dan tambahkan variabel berikut:
    ```env
    API_ID=your_api_id
    API_HASH=your_api_hash
    BOT_TOKEN=your_telegram_bot_token
    OWNER_ID=your_telegram_id
    ```

5. Jalankan bot:
    ```sh
    python bot.py
    ```

## Penggunaan

### Perintah

- `/start` - Memulai bot dan menampilkan pesan sambutan.
- `/play` - Memulai permainan.
- `/nyerah` - Menyerah dari permainan.
- `/next` - Mendapatkan pertanyaan berikutnya.
- `/stats` - Melihat statistik pribadi.
- `/top` - Melihat top skor global.
- `/topgrup` - Melihat top skor grup.
- `/peraturan` - Melihat aturan bermain.
- `/help` - Mendapatkan bantuan.
- `/blacklist [user_id/grup_id]` - Menambahkan pengguna atau grup ke daftar hitam (hanya untuk pemilik bot).
- `/whitelist [user_id/grup_id]` - Menghapus pengguna atau grup dari daftar hitam (hanya untuk pemilik bot).

### Contoh Perintah

```sh
/start
/play
/nyerah
/next
/stats
/top
/topgrup
/peraturan
/help
/blacklist 123456789
/whitelist 123456789
