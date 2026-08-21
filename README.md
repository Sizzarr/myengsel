# MYnyak Engsel Sunset

![banner](bnr.png)

CLI client for a certain Indonesian mobile internet service provider.

# How to get environtment Variables
Go to [OUR TELEGRAM CHANNEL](https://t.me/alyxcli)
Copy the provided environment variables and paste it into a text file named `.env` in the same directory as `main.py`.
You can use nano or any text editor to create the file.

# How to run with TERMUX
1. Update & Upgrade Termux
```
pkg update && pkg upgrade -y
```
2. Install Git
```
pkg install git -y
```
3. Clone this repo
```
git clone https://github.com/purplemashu/me-cli-sunset
```
4. Open the folder
```
cd me-cli-sunset
```
5. Setup
```
bash setup.sh
```
6. Run the script
```
python main.py
```

# Info

## PS for Certain Indonesian mobile internet service provider

Instead of just delisting the package from the app, ensure the user cannot purchase it.
What's the point of strong client side security when the server don't enforce it?

## Terms of Service
By using this tool, the user agrees to comply with all applicable laws and regulations and to release the developer from any and all claims arising from its use.

## Contact

contact@mashu.lol

## Web UI (Desktop)

Project ini sekarang memiliki web UI lokal yang tetap memakai logic/API dan file token yang sama dengan CLI.
CLI lama tidak dihapus dan tetap dapat dijalankan dengan `python main.py`.

### Menjalankan Web UI

1. Siapkan `.env` yang sama seperti penggunaan CLI.
2. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan:
   ```bash
   python web.py
   ```
   atau di Windows klik `run-web.bat`.
4. Buka browser:
   ```text
   http://127.0.0.1:8765
   ```

### Fitur web yang tersedia

- Landing page desktop
- Login OTP 6 digit
- Multi-account / switch account
- Dashboard (balance, points/tier, notifications, active package)
- My Packages + unsubscribe
- Store Packages, Family List, dan Store Segments
- Package detail
- Pembelian normal: Balance, DANA, ShopeePay, GoPay, OVO, QRIS
- Transaction History
- Family Plan / Akrab Organizer
- XL Circle + member/bonus/spending overview
- Redeemables / Rewards
- Bookmark
- Notifications + mark all unread as read
- Dukcapil registration dan Validate MSISDN di halaman Support/Tools

Web UI sengaja **tidak** menampilkan shortcut eksperimental seperti decoy, overwrite amount,
atau loop purchase. Fitur tersebut tetap berada di CLI/source lama dan tidak dijadikan flow web normal.
