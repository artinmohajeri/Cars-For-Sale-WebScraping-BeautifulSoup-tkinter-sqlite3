from requests_html import HTMLSession
from bs4 import BeautifulSoup
import tkinter as tk
import ttkbootstrap as tb
from tkinter import ttk
from tkinter import messagebox
import sqlite3, time


win = tb.Window(themename="darkly")
style = tb.Style(theme="darkly")
win.title("Car Data")
win.minsize(600,350)


car = None
home_url = "https://www.autoscout24.com/"
all_cars = []
try:
    ses = HTMLSession()
    result = ses.get(home_url)
except:
    messagebox.showerror(title="Error", message="Connection Problem")
doc = BeautifulSoup(result.text, "html.parser")
cars_menu = doc.find(attrs={"aria-label": "cars-make-filter"})
cars_menu = cars_menu.find_all("optgroup")

connect = sqlite3.connect("./cars.db")
cursor = connect.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cars(
                name TEXT,
                model TEXT,
                price TEXT,
                mileage TEXT,
                gearbox TEXT,
                First_registration TEXT,
                fuel_type TEXT,
                power TEXT
    )''')

for car in cars_menu[0]:
    all_cars.append(car.string)
for car in cars_menu[1]:
    all_cars.append(car.string)


def click(item):
    global car
    my_menu.configure(text=item)
    car = item

def search():
    try:
        cursor.execute('DELETE FROM cars')
        session = HTMLSession()
        param = {"page":1}
        url = f"https://www.autoscout24.com/lst/{car}?atype=C&desc=0&sort=standard&source=homepage_search-mask&ustate=N%2CU"
        while True:
            res = session.get(url, params=param)
            doc = BeautifulSoup(res.text, "html.parser")
            names = doc.find_all("h2")
            models = doc.find_all(class_="ListItem_version__jNjur")
            prices = doc.find_all(class_="Price_price__WZayw PriceAndSeals_current_price__XscDn")
            details = doc.find_all(class_="VehicleDetailTable_container__mUUbY")
            # images = doc.find_all(class_="NewGallery_img__bi92g")
            next_btn = doc.find(attrs={"aria-label": "Go to next page"})

            for name,model,price,detail in zip(names,models,prices,details):
                name = name.contents[0]
                model = model.string
                price = price.string
                milage = detail.contents[0].contents[1]
                gearbox = detail.contents[1].contents[1]
                First_registration = detail.contents[2].contents[1]
                fuel_type = detail.contents[3].contents[1]
                power = detail.contents[4].contents[1]
                cursor.execute('INSERT INTO cars (name, model, price, mileage, gearbox, First_registration, fuel_type, power) VALUES (?,?,?,?,?,?,?,?)', (name, model, price, milage, gearbox, First_registration, fuel_type, power))

            if not next_btn:
                break
            param["page"] += 1
        connect.commit()
        lab.configure(text="data recieved successfuly!!", fg="lightgreen")

        with open("display.py","w") as f:
            f.write('''

from tkinter import *
from tkinter import ttk
import sqlite3
                
# window configurations
win = Tk()
win.title("cars database")

# connecting to the database
connect = sqlite3.connect("cars.db")
cursor = connect.cursor()
cursor.execute("SELECT * FROM cars")
rows = cursor.fetchall()

total = 0
# style of the table
style = ttk.Style()
style.configure("Treeview", font=("Arial", 12), rowheight=30, foreground="black", background="white")

tree = ttk.Treeview(win, columns=("name", "model", "price", "mileage","gearbox","First_registration", "fuel_type","power"), show="headings")
tree.heading("name", text="name")
tree.heading("model", text="model")
tree.heading("price", text="price")
tree.heading("mileage", text="mileage")
tree.heading("gearbox", text="gearbox")
tree.heading("First_registration", text="first_registration")
tree.heading("fuel_type", text="fuel_type")
tree.heading("power", text="power")

tree.column("price", width=150, anchor="center")
tree.column("mileage", width=150, anchor="center")
tree.column("gearbox", width=150, anchor="center")
tree.column("First_registration", width=150, anchor="center")
tree.column("fuel_type", width=150, anchor="center")
tree.column("power", width=150, anchor="center")

tree.tag_configure("evenrow", background="#d1d1d1")
tree.tag_configure("oddrow", background="white")

vsb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
vsb.pack(side="right", fill="y")
tree.configure(yscrollcommand=vsb.set)

for i, row in enumerate(rows):
    total += 1
    if i % 2 == 0:
        tree.insert("", "end", values=row, tags=("evenrow",))
    else:
        tree.insert("", "end", values=row, tags=("oddrow",))
tree.pack()

lbl = Label(win, text=f"{total} results found", font=("None",16))
lbl.pack(pady=40)

win.mainloop()

    ''')
    
    except:
        messagebox.showerror(title="Error", message="Data did NOT recieved")
        

style.configure('TMenubutton', font=('Helvetica', 14))
my_menu = tb.Menubutton(win, bootstyle="outline-info", text="choose a car", cursor="hand2")
my_menu.pack(pady=(30,0))

inside_menu = tb.Menu(my_menu)
item_var = tk.StringVar()
for item in all_cars:
    inside_menu.add_radiobutton(label=item, command=lambda item=item:click(item))
my_menu["menu"] = inside_menu

style.configure('TButton', font=('Helvetica', 14))
btn = tb.Button(win, text="Search Car", bootstyle="outline-success", cursor="hand2", command=search)
btn.pack(pady=(100,0))

lab = tk.Label(win, text="it may take a few seconds...", font=("None",12))
lab.pack(pady=(40,0))

win.mainloop()
connect.close()
