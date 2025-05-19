import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import requests
import webbrowser
import os
from dotenv import load_dotenv
import csv
from PIL import Image, ImageTk
import io

load_dotenv()

API_KEY = os.getenv('COLLECTAPI_KEY')
BASE_URL = "https://api.collectapi.com/news/getNews"
VALID_TAGS = ("general", "sport", "economy", "technology")
COUNTRIES = ("tr", "de", "en", "ru")

current_page = 0
news_data = []

# Veritabanı bağlantısı
conn = sqlite3.connect("news.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS articles (
    news_id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    url TEXT,
    source TEXT,
    published_at TEXT,
    country TEXT,
    category TEXT,
    image TEXT,
    is_favorite INTEGER
)
""")
conn.commit()


def fetch_news(country, tag, paging=0):
    headers = {
        "authorization": f"apikey {API_KEY}",
        "content-type": "application/json"
    }
    params = {
        "country": country,
        "tag": tag,
        "paging": paging
    }
    r = requests.get(BASE_URL, headers=headers, params=params)
    if r.status_code != 200:
        raise Exception("API isteği başarısız")
    result = r.json()
    if not result.get("success", False):
        raise Exception("API cevabı başarısız: " + result.get("message", ""))
    return result["result"]


def save_articles(articles, country, category):
    for a in articles:
        news_id = a.get("url")
        title = a.get("name", "")
        description = a.get("description", "")
        url = a.get("url", "")
        source = a.get("source", "")
        published = a.get("publishedAt", "")
        image = a.get("image", "")
        c.execute("""
    INSERT OR IGNORE INTO articles 
    (news_id, title, description, url, source, published_at, country, category, image)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (news_id, title, description, url, source, published, country, category, image))
    conn.commit()


# Ana Pencere
root = tk.Tk()
root.title("📰 Mini Haber Okuyucu")
root.geometry("1250x500")
root.configure(bg="#f4f4f4")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Arial", 10), padding=6)
style.configure("TLabel", font=("Arial", 10))
style.configure("TCombobox", padding=4)

# Üst Menü
frame_top = ttk.Frame(root)
frame_top.pack(pady=10)

lbl_country = ttk.Label(frame_top, text="Ülke:")
lbl_country.pack(side="left", padx=(0, 5))
cmb_country = ttk.Combobox(
    frame_top, values=COUNTRIES, state="readonly", width=10)
cmb_country.set("tr")
cmb_country.pack(side="left", padx=(0, 15))

lbl_cat = ttk.Label(frame_top, text="Kategori:")
lbl_cat.pack(side="left", padx=(0, 5))
cmb_category = ttk.Combobox(
    frame_top, values=VALID_TAGS, state="readonly", width=12)
cmb_category.set("general")
cmb_category.pack(side="left", padx=(0, 15))

btn_fetch = ttk.Button(frame_top, text="📥 Haberleri Getir")
btn_fetch.pack(side="left", padx=(0, 5))

# Yapay zekadan yardım alındı, resim 1
btn_load_more = ttk.Button(frame_top, text="📄 Daha Fazla Haber Getir")
btn_load_more.pack(side="left", padx=(0, 15))

entry_search = ttk.Entry(frame_top, width=20)
entry_search.pack(side="left", padx=(5, 0))
entry_search.insert(0, "Ara...")

btn_search = ttk.Button(frame_top, text="🔎")
btn_search.pack(side="left", padx=(5, 0))

btn_export = ttk.Button(frame_top, text="📤 Dışa Aktar")
btn_export.pack(side="left", padx=(5, 0))

# Yapay zekadan yardım alındı, resim 3
btn_favs = ttk.Button(frame_top, text="⭐ Favoriler")
btn_favs.pack(side="left", padx=(5, 0))

# Yapay zekadan yardım alındı, resim 6
# Liste Alanı
frame_list = ttk.Frame(root)
frame_list.pack(fill="both", expand=True, padx=10, pady=10)

columns = ("title", "source")
tree = ttk.Treeview(frame_list, columns=columns, show="headings")
tree.heading("title", text="Haber Başlığı")
tree.heading("source", text="Kaynak")
tree.column("title", anchor="w", width=500)
tree.column("source", anchor="center", width=120)

vsb = ttk.Scrollbar(frame_list, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)

tree.pack(side="left", fill="both", expand=True)
vsb.pack(side="right", fill="y")


def load_articles(country, category, only_favorites=False):
    tree.delete(*tree.get_children())
    news_data.clear()

    query = """
        SELECT title, source, substr(published_at,1,10), news_id, description, url 
        FROM articles 
        WHERE country=? AND category=?
    """
    params = [country, category]
    if only_favorites:
        query += " AND is_favorite=1"
    query += " ORDER BY rowid DESC"

    c.execute(query, params)
    rows = c.fetchall()
    for title, source, date, news_id, desc, url in rows:
        c.execute("SELECT image FROM articles WHERE news_id=?", (news_id,))
        img_result = c.fetchone()
        img_url = img_result[0] if img_result else ""
        tree.insert("", "end", values=(title[:120], source))
        news_data.append((title, desc, url, img_url))


def refresh():
    global current_page
    current_page = 0

    country = cmb_country.get()
    category = cmb_category.get()
    if not country or not category:
        messagebox.showerror("Hata", "Lütfen ülke ve kategori seçin.")
        return

    try:
        articles = fetch_news(country, category, paging=current_page)
        if not articles:
            messagebox.showinfo(
                "Bilgi", "Bu kriterlere uygun haber bulunamadı.")
        save_articles(articles, country, category)
        load_articles(country, category)
    except Exception as e:
        messagebox.showerror("Hata", str(e))


def load_more():
    global current_page
    country = cmb_country.get()
    category = cmb_category.get()
    if not country or not category:
        messagebox.showerror("Hata", "Lütfen ülke ve kategori seçin.")
        return

    try:
        current_page += 1
        articles = fetch_news(country, category, paging=current_page)
        if not articles:
            messagebox.showinfo("Bilgi", "Daha fazla haber bulunamadı.")
            current_page -= 1
            return
        save_articles(articles, country, category)
        load_articles(country, category)
    except Exception as e:
        messagebox.showerror("Hata", str(e))

# Yapay zekadan yardım alındı, resim 4


def search_articles(keyword):
    tree.delete(*tree.get_children())
    news_data.clear()
    kw = f"%{keyword}%"
    c.execute("""
        SELECT title, source, substr(published_at,1,10), news_id, description, url 
        FROM articles 
        WHERE (title LIKE ? OR description LIKE ?)
        ORDER BY rowid DESC
    """, (kw, kw))
    rows = c.fetchall()
    for title, source, date, news_id, desc, url in rows:
        c.execute("SELECT image FROM articles WHERE news_id=?", (news_id,))
        img_result = c.fetchone()
        img_url = img_result[0] if img_result else ""
        tree.insert("", "end", values=(title[:120], source))
        news_data.append((title, desc, url, img_url))

# Yapay zekadan yardım alındı, resim 4


def export_to_csv(data):
    if not data:
        messagebox.showinfo("Bilgi", "Dışa aktarılacak haber bulunamadı.")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Dosyası", "*.csv")]
    )
    if not file_path:
        return
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Başlık", "Açıklama", "URL", "Resim URL"])
        for row in data:
            writer.writerow(row)
    messagebox.showinfo("Başarılı", "Haberler başarıyla dışa aktarıldı.")

# Yapay zekadan yardım alındı, resim 5


def open_detail(event):
    selected = tree.selection()
    if not selected:
        return
    idx = tree.index(selected[0])
    title, desc, url, img_url = news_data[idx]

    win = tk.Toplevel(root)
    win.title("📄 Haber Detayı")
    win.geometry("600x800")
    win.configure(bg="#ffffff")

    # Yapay zekadan yardım alındı, resim 3
    def add_to_favorites():
        c.execute("SELECT is_favorite FROM articles WHERE url=?", (url,))
        result = c.fetchone()
        if result and result[0] == 1:
            messagebox.showinfo("Bilgi", "Bu haber zaten favorilerde.")
        else:
            c.execute("UPDATE articles SET is_favorite=1 WHERE url=?", (url,))
            conn.commit()
            messagebox.showinfo("Favori", "Haber favorilere eklendi.")

    btn_fav = ttk.Button(win, text="⭐ Favorilere Ekle",
                         command=add_to_favorites)
    btn_fav.pack(pady=5)

    lbl_title = ttk.Label(win, text=title, wraplength=580,
                          font=("Arial", 12, "bold"))
    lbl_title.pack(pady=10)

    if img_url and img_url.startswith("http"):
        try:
            resp = requests.get(img_url, timeout=5)
            img_data = resp.content
            pil_img = Image.open(io.BytesIO(img_data))
            pil_img = pil_img.resize((300, 200))
            tk_img = ImageTk.PhotoImage(pil_img)
            img_label = tk.Label(win, image=tk_img, bg="#ffffff")
            img_label.image = tk_img
            img_label.pack(pady=5)
        except Exception as e:
            print("Görsel yüklenemedi:", e)

    txt_desc = tk.Text(win, height=10, wrap="word", font=("Arial", 10))
    txt_desc.insert("1.0", desc)
    txt_desc.config(state="disabled", bg="#fefefe")
    txt_desc.pack(padx=10, pady=5, fill="both", expand=True)

    def open_in_browser():
        webbrowser.open(url)

    btn_browser = ttk.Button(
        win, text="🌐 Tarayıcıda Aç", command=open_in_browser)
    btn_browser.pack(pady=5)


# Yapay zekadan yardım alındı
btn_fetch.config(command=refresh)
btn_load_more.config(command=load_more)
btn_search.config(command=lambda: search_articles(entry_search.get()))
btn_export.config(command=lambda: export_to_csv(news_data))
btn_favs.config(command=lambda: load_articles(
    cmb_country.get(), cmb_category.get(), only_favorites=True))
cmb_country.bind("<Return>", lambda e: refresh())
cmb_category.bind("<Return>", lambda e: refresh())
tree.bind("<Double-1>", open_detail)

load_articles("tr", "general")
root.mainloop()

