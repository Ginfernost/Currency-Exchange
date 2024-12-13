import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Predefined list of supported currency codes including "None"
available_currencies = [
    "None", "USD", "HKD", "GBP", "AUD", "CAD", "SGD", "CHF", "JPY", "ZAR", 
    "SEK", "NZD", "THB", "PHP", "IDR", "EUR", "KRW", "VND", "MYR", "CNY"
]

# Function to fetch historical data for the last 6 months
def fetch_currency_history(currency_code):
    if currency_code == "None":
        return None

    url = f"https://rate.bot.com.tw/xrt/quote/l6m/{currency_code}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", class_="table")
        rows = table.find_all("tr")

        data = []
        for row in rows[1:]:
            cells = row.find_all("td")
            if cells:
                date = cells[0].text.strip()
                spot_buying = cells[4].text.strip().replace(",", "")
                spot_selling = cells[5].text.strip().replace(",", "")
                data.append([date, float(spot_buying), float(spot_selling)])

        df = pd.DataFrame(data, columns=["Date", "Spot Buying", "Spot Selling"])
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    else:
        return None

# Function to plot a single graph
def plot_single_graph(df, currency_code, graph_frame):
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(df["Date"], df["Spot Buying"], label="Spot Buying", marker='o')
    ax.plot(df["Date"], df["Spot Selling"], label="Spot Selling", marker='o')
    ax.set_title(f"{currency_code} Exchange Rates")
    ax.set_xlabel("Date")
    ax.set_ylabel("Rate")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    return canvas

# Function to create the GUI
def create_gui():
    root = tk.Tk()
    root.title("Currency Exchange Rate Trends")
    root.state("zoomed")

    def on_closing():
        root.destroy()
        exit()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Main container layout
    container = ttk.Frame(root)
    container.pack(fill=tk.BOTH, expand=True)

    # Sidebar frame for controls
    sidebar = ttk.Frame(container, width=300, padding=(10, 10, 10, 10))
    sidebar.pack(side=tk.LEFT, fill=tk.Y)

    # Graph display frame
    graph_frame = ttk.Frame(container, padding=(10, 10, 10, 10))
    graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Sidebar title
    tk.Label(sidebar, text="Currency Selector", font=("Arial", 16, "bold")).pack(pady=10)

    # Dropdowns for currency selection
    currency_combobox1 = ttk.Combobox(sidebar, values=available_currencies, font=("Arial", 12))
    currency_combobox1.set("None")
    currency_combobox1.pack(pady=5, fill=tk.X)

    currency_combobox2 = ttk.Combobox(sidebar, values=available_currencies, font=("Arial", 12))
    currency_combobox2.set("None")
    currency_combobox2.pack(pady=5, fill=tk.X)

    error_label = tk.Label(sidebar, text="", font=("Arial", 12), fg="red")
    error_label.pack(pady=10)

    graph_canvas1 = None
    graph_canvas2 = None

    def on_select():
        nonlocal graph_canvas1, graph_canvas2

        # Clear previous graphs
        for widget in graph_frame.winfo_children():
            widget.destroy()

        error_label.config(text="")

        selected_currency1 = currency_combobox1.get()
        selected_currency2 = currency_combobox2.get()

        # Fetch and plot the first currency
        if selected_currency1 != "None":
            df1 = fetch_currency_history(selected_currency1)
            if df1 is not None:
                graph_canvas1 = plot_single_graph(df1, selected_currency1, graph_frame)
            else:
                error_label.config(text=f"Failed to fetch data for {selected_currency1}.")
        
        # Fetch and plot the second currency
        if selected_currency2 != "None":
            df2 = fetch_currency_history(selected_currency2)
            if df2 is not None:
                graph_canvas2 = plot_single_graph(df2, selected_currency2, graph_frame)
            else:
                error_label.config(text=f"Failed to fetch data for {selected_currency2}.")

    # Fetch data button
    ttk.Button(sidebar, text="Fetch Data", command=on_select).pack(pady=20, fill=tk.X)

    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    create_gui()
