"""
Telesales CRM Portfolio — aplikasi CRM sederhana berbasis Python + SQLite.
Jalankan: python app.py
Tidak memerlukan library eksternal.
"""
import csv
import sqlite3
from datetime import datetime, date
from pathlib import Path

DB_PATH = Path(__file__).with_name("telesales.db")
OUTCOMES = {
    "1": "Connected",
    "2": "No Answer",
    "3": "Call Back",
    "4": "Interested",
    "5": "Not Interested",
    "6": "Converted",
}
STATUSES = ("New", "Contacted", "Follow-up", "Interested", "Not Interested", "Converted")


def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            company TEXT DEFAULT '',
            source TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'New',
            notes TEXT DEFAULT '',
            follow_up TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS call_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
            called_at TEXT NOT NULL,
            outcome TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL DEFAULT 0,
            notes TEXT DEFAULT ''
        );
        """)


def pause():
    input("\nTekan Enter untuk kembali ke menu...")


def ask(prompt, required=False, default=""):
    while True:
        suffix = f" [{default}]" if default else ""
        value = input(f"{prompt}{suffix}: ").strip()
        value = value or default
        if required and not value:
            print("Bagian ini wajib diisi.")
            continue
        return value


def list_leads():
    with connect() as con:
        rows = con.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()
    if not rows:
        print("\nBelum ada prospek. Tambahkan prospek baru dari menu.")
        return
    print("\n" + "-" * 105)
    print(f"{'ID':<4} {'Nama':<22} {'Telepon':<16} {'Perusahaan':<20} {'Status':<17} {'Follow-up':<12}")
    print("-" * 105)
    for r in rows:
        print(f"{r['id']:<4} {r['name'][:21]:<22} {r['phone'][:15]:<16} {r['company'][:19]:<20} {r['status']:<17} {r['follow_up'] or '-':<12}")
    print("-" * 105)


def add_lead():
    print("\n=== TAMBAH PROSPEK ===")
    name = ask("Nama calon pelanggan", True)
    phone = ask("Nomor telepon", True)
    company = ask("Perusahaan/instansi")
    source = ask("Sumber prospek (iklan, referral, dll.)")
    notes = ask("Catatan awal")
    with connect() as con:
        cur = con.execute(
            "INSERT INTO leads(name, phone, company, source, notes, created_at) VALUES(?,?,?,?,?,?)",
            (name, phone, company, source, notes, datetime.now().isoformat(timespec="seconds"))
        )
        lead_id = cur.lastrowid
    print(f"Prospek berhasil disimpan dengan ID {lead_id}.")


def get_lead(lead_id):
    with connect() as con:
        return con.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone()


def log_call():
    list_leads()
    try:
        lead_id = int(ask("\nMasukkan ID prospek", True))
    except ValueError:
        print("ID harus berupa angka.")
        return
    lead = get_lead(lead_id)
    if not lead:
        print("Prospek tidak ditemukan.")
        return
    print("\nHasil panggilan:")
    for key, label in OUTCOMES.items():
        print(f" {key}. {label}")
    outcome = ask("Pilih hasil (1-6)", True)
    if outcome not in OUTCOMES:
        print("Pilihan hasil panggilan tidak valid.")
        return
    try:
        duration = int(ask("Durasi panggilan (detik)", default="0"))
        if duration < 0:
            raise ValueError
    except ValueError:
        print("Durasi harus berupa angka nol atau lebih.")
        return
    notes = ask("Catatan percakapan")
    follow_up = ""
    if outcome in ("3", "4"):
        follow_up = ask("Tanggal follow-up (YYYY-MM-DD, kosong jika belum ditentukan)")
        if follow_up:
            try:
                date.fromisoformat(follow_up)
            except ValueError:
                print("Format tanggal tidak valid. Log panggilan dibatalkan.")
                return
    status = {
        "1": "Contacted", "2": "Contacted", "3": "Follow-up",
        "4": "Interested", "5": "Not Interested", "6": "Converted"
    }[outcome]
    with connect() as con:
        con.execute(
            "INSERT INTO call_logs(lead_id, called_at, outcome, duration_seconds, notes) VALUES(?,?,?,?,?)",
            (lead_id, datetime.now().isoformat(timespec="seconds"), OUTCOMES[outcome], duration, notes)
        )
        con.execute("UPDATE leads SET status=?, follow_up=?, notes=? WHERE id=?",
                    (status, follow_up, notes or lead["notes"], lead_id))
    print(f"Log panggilan tersimpan. Status prospek: {status}.")


def dashboard():
    with connect() as con:
        total = con.execute("SELECT COUNT(*) n FROM leads").fetchone()["n"]
        calls = con.execute("SELECT COUNT(*) n FROM call_logs").fetchone()["n"]
        connected = con.execute("SELECT COUNT(*) n FROM call_logs WHERE outcome NOT IN ('No Answer')").fetchone()["n"]
        converted = con.execute("SELECT COUNT(*) n FROM leads WHERE status='Converted'").fetchone()["n"]
        duration = con.execute("SELECT COALESCE(SUM(duration_seconds),0) n FROM call_logs").fetchone()["n"]
        statuses = con.execute("SELECT status, COUNT(*) n FROM leads GROUP BY status ORDER BY n DESC").fetchall()
    connect_rate = (connected / calls * 100) if calls else 0
    conversion_rate = (converted / total * 100) if total else 0
    avg_duration = duration / calls if calls else 0
    print("\n" + "=" * 45)
    print("         TELESALES PERFORMANCE DASHBOARD")
    print("=" * 45)
    print(f"Total prospek             : {total}")
    print(f"Total aktivitas panggilan : {calls}")
    print(f"Panggilan terhubung*      : {connected}")
    print(f"Rasio connect*            : {connect_rate:.1f}%")
    print(f"Prospek converted         : {converted}")
    print(f"Conversion rate**         : {conversion_rate:.1f}%")
    print(f"Rata-rata durasi call     : {avg_duration:.0f} detik")
    print("\nDistribusi status:")
    for s in statuses:
        print(f"  {s['status']:<18} {s['n']}")
    print("\n* Connect rate di aplikasi ini menghitung semua outcome selain 'No Answer'.")
    print("** Conversion rate = prospek berstatus Converted / seluruh prospek.")


def follow_ups():
    today = date.today().isoformat()
    with connect() as con:
        rows = con.execute("""
            SELECT id, name, phone, company, status, follow_up
            FROM leads WHERE follow_up <> '' AND follow_up <= ?
            ORDER BY follow_up, name
        """, (today,)).fetchall()
    print(f"\n=== FOLLOW-UP JATUH TEMPO (sampai {today}) ===")
    if not rows:
        print("Tidak ada follow-up yang jatuh tempo.")
        return
    for r in rows:
        flag = "TERLAMBAT" if r["follow_up"] < today else "HARI INI"
        print(f"#{r['id']} | {r['name']} | {r['phone']} | {r['status']} | {r['follow_up']} ({flag})")


def lead_history():
    try:
        lead_id = int(ask("ID prospek", True))
    except ValueError:
        print("ID harus berupa angka.")
        return
    lead = get_lead(lead_id)
    if not lead:
        print("Prospek tidak ditemukan.")
        return
    print(f"\n=== PROFIL PROSPEK #{lead['id']} ===")
    for field in ("name", "phone", "company", "source", "status", "notes", "follow_up", "created_at"):
        print(f"{field.replace('_',' ').title():<15}: {lead[field] or '-'}")
    with connect() as con:
        logs = con.execute("SELECT * FROM call_logs WHERE lead_id=? ORDER BY called_at DESC", (lead_id,)).fetchall()
    print("\nRiwayat panggilan:")
    if not logs:
        print("Belum ada aktivitas.")
    for log in logs:
        print(f"- {log['called_at']} | {log['outcome']} | {log['duration_seconds']} detik | {log['notes'] or '-'}")


def update_status():
    list_leads()
    try:
        lead_id = int(ask("\nID prospek yang diperbarui", True))
    except ValueError:
        print("ID harus berupa angka.")
        return
    if not get_lead(lead_id):
        print("Prospek tidak ditemukan.")
        return
    for i, status in enumerate(STATUSES, 1):
        print(f"{i}. {status}")
    choice = ask("Pilih status", True)
    if not choice.isdigit() or not 1 <= int(choice) <= len(STATUSES):
        print("Pilihan tidak valid.")
        return
    status = STATUSES[int(choice)-1]
    with connect() as con:
        con.execute("UPDATE leads SET status=? WHERE id=?", (status, lead_id))
    print("Status prospek berhasil diperbarui.")


def export_csv():
    destination = Path(__file__).with_name("telesales_report.csv")
    with connect() as con:
        rows = con.execute("""
            SELECT l.id, l.name, l.phone, l.company, l.source, l.status, l.follow_up,
                   l.created_at, COUNT(c.id) call_count,
                   COALESCE(SUM(c.duration_seconds),0) total_call_seconds
            FROM leads l LEFT JOIN call_logs c ON l.id=c.lead_id
            GROUP BY l.id ORDER BY l.id
        """).fetchall()
    with destination.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Nama", "Telepon", "Perusahaan", "Sumber", "Status",
                         "Tanggal Follow-up", "Dibuat", "Jumlah Call", "Total Durasi (detik)"])
        writer.writerows([tuple(r) for r in rows])
    print(f"Data berhasil diekspor ke: {destination.name}")


def seed_demo():
    with connect() as con:
        count = con.execute("SELECT COUNT(*) n FROM leads").fetchone()["n"]
        if count:
            print("Database sudah berisi data. Demo tidak ditambahkan agar data Anda aman.")
            return
        demo = [
            ("Dina Pratiwi", "081234567801", "CV Sinar Jaya", "Referral", "Interested", "Minta penawaran", date.today().isoformat()),
            ("Budi Santoso", "081234567802", "Toko Makmur", "Website", "Follow-up", "Hubungi kembali", date.today().isoformat()),
            ("Rina Amelia", "081234567803", "Personal", "Campaign", "Converted", "Berhasil closing", ""),
            ("Agus Setiawan", "081234567804", "UD Berkah", "Cold call", "Not Interested", "Belum membutuhkan", ""),
            ##("Bobon Santoso", "081234567899", "Personal", "Cold call", "Interested", "Membutuhkan", ""),
        ]
        for name, phone, company, source, status, notes, follow_up in demo:
            cur = con.execute("""INSERT INTO leads(name,phone,company,source,status,notes,follow_up,created_at)
                                 VALUES(?,?,?,?,?,?,?,?)""",
                              (name, phone, company, source, status, notes, follow_up,
                               datetime.now().isoformat(timespec="seconds")))
            if status != "New":
                con.execute("INSERT INTO call_logs(lead_id,called_at,outcome,duration_seconds,notes) VALUES(?,?,?,?,?)",
                            (cur.lastrowid, datetime.now().isoformat(timespec="seconds"),
                             {"Interested":"Interested","Follow-up":"Call Back","Converted":"Converted",
                              "Not Interested":"Not Interested"}[status], 95, notes))
    print("4 data demo ditambahkan. Anda dapat menghapus file telesales.db untuk mulai dari nol.")


def main():
    init_db()
    while True:
        print("""
========================================
       TELESALES CRM PORTFOLIO
========================================
1. Dashboard performa
2. Lihat semua prospek
3. Tambah prospek
4. Catat hasil panggilan
5. Lihat follow-up jatuh tempo
6. Lihat profil & riwayat prospek
7. Perbarui status prospek
8. Ekspor laporan ke CSV
9. Isi data demo (opsional)
0. Keluar
""")
        choice = input("Pilih menu: ").strip()
        actions = {"1": dashboard, "2": list_leads, "3": add_lead, "4": log_call,
                   "5": follow_ups, "6": lead_history, "7": update_status,
                   "8": export_csv, "9": seed_demo}
        if choice == "0":
            print("Terima kasih. Sampai jumpa!")
            break
        action = actions.get(choice)
        if action:
            action()
            if choice not in ("1", "2"):
                pause()
            elif choice in ("1", "2"):
                pause()
        else:
            print("Menu tidak tersedia. Pilih angka 0–9.")


if __name__ == "__main__":
    main()
