import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import yfinance as yf
import json
from datetime import datetime


class StockPortfolioTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Portfolio Tracker")
        self.root.geometry("800x600")

        self.original_bg_image = Image.open("C:\\Users\\marreddyGowthamreddy\\Downloads\\Portfolio.jpg")  
        self.update_background()

        self.root.bind("<Configure>", self.on_resize)

        self.style = ttk.Style()
        self.style.configure("Custom.TLabelframe", background="#f5f5f5")
        self.style.configure("Custom.TLabelframe.Label", background="#f5f5f5")
        self.style.configure("TLabel", background="#d9e4f5")
        self.style.configure("TButton", background="#f0f0f0")
        self.portfolio = self.load_portfolio()
        self.create_frames()
        self.create_widgets()
        self.update_prices()

    def update_background(self):
        self.bg_image = self.original_bg_image.resize(
            (self.root.winfo_width(), self.root.winfo_height()), Image.Resampling.LANCZOS
        )
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        if hasattr(self, "bg_label"):
            self.bg_label.config(image=self.bg_photo)
        else:
            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(relwidth=1, relheight=1, x=0, y=0)

    def on_resize(self, event):
        self.update_background()

    def create_frames(self):
        self.input_frame = ttk.LabelFrame(
            self.root, text="Add Stock", padding="10", style="Custom.TLabelframe"
        )
        self.input_frame.place(relx=0.05, rely=0.05, relwidth=0.9)

        self.portfolio_frame = ttk.LabelFrame(
            self.root, text="Current Portfolio", padding="10", style="Custom.TLabelframe"
        )
        self.portfolio_frame.place(relx=0.05, rely=0.2, relwidth=0.9, relheight=0.5)

        self.sensex_frame = ttk.LabelFrame(
            self.root, text="Sensex Index", padding="10", style="Custom.TLabelframe"
        )
        self.sensex_frame.place(relx=0.05, rely=0.75, relwidth=0.9)

    def create_widgets(self):
        ttk.Label(self.input_frame, text="Symbol:").grid(row=0, column=0, padx=5)
        self.symbol_entry = ttk.Entry(self.input_frame)
        self.symbol_entry.grid(row=0, column=1, padx=5)

        ttk.Label(self.input_frame, text="Shares:").grid(row=0, column=2, padx=5)
        self.shares_entry = ttk.Entry(self.input_frame)
        self.shares_entry.grid(row=0, column=3, padx=5)

        add_button = tk.Button(
            self.input_frame, text="Add Stock", bg="blue", fg="white", command=self.add_stock
        )
        add_button.grid(row=0, column=4, padx=5)

        columns = ("Symbol", "Shares", "Current Price", "Value", "Change %")
        self.tree = ttk.Treeview(self.portfolio_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.portfolio_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.tag_configure("positive", background="yellow")
        self.tree.tag_configure("negative", background="yellow")

        ttk.Button(self.portfolio_frame, text="Remove Selected", command=self.remove_stock).pack(pady=5)

        self.sensex_label = tk.Label(self.sensex_frame, text="Loading Sensex...", fg="red")
        self.sensex_label.pack()

        self.total_value_label = tk.Label(self.portfolio_frame, text="Total Portfolio Value: $0.00", fg= "green")
        self.total_value_label.pack(pady=5)

    def get_stock_price(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')
            if not hist.empty:
                return hist['Close'].iloc[-1]
            return None
        except Exception as e:
            print(f"Error getting price for {symbol}: {str(e)}")
            return None

    def load_portfolio(self):
        try:
            with open('portfolio.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("Error reading portfolio.json. Starting with an empty portfolio.")
            return []

    def save_portfolio(self):
        try:
            with open('portfolio.json', 'w') as f:
                json.dump(self.portfolio, f)
        except Exception as e:
            print(f"Error saving portfolio: {str(e)}")

    def add_stock(self):
        symbol = self.symbol_entry.get().upper()
        if not symbol:
            messagebox.showerror("Error", "Stock symbol cannot be empty.")
            return

        try:
            shares = float(self.shares_entry.get())
            if shares <= 0:
                raise ValueError("Shares must be greater than zero.")

            price = self.get_stock_price(symbol)
            if price is None:
                messagebox.showerror("Error", f"Could not get price for {symbol}")
                return

            self.portfolio.append({
                'symbol': symbol,
                'shares': shares,
                'purchase_price': price,
                'purchase_date': datetime.now().strftime('%Y-%m-%d')
            })

            self.save_portfolio()
            self.update_prices()

            self.symbol_entry.delete(0, tk.END)
            self.shares_entry.delete(0, tk.END)
            messagebox.showinfo("Success", f"Added {shares} shares of {symbol}")

        except ValueError as ve:
            messagebox.showerror("Error", f"Invalid input: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding stock: {str(e)}")

    def remove_stock(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a stock to remove")
            return

        symbol = self.tree.item(selected_item[0])['values'][0]
        self.portfolio = [stock for stock in self.portfolio if stock['symbol'] != symbol]
        self.save_portfolio()
        self.update_prices()
        messagebox.showinfo("Success", f"Removed {symbol} from portfolio")

    def update_prices(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_value = 0

        for stock in self.portfolio:
            try:
                current_price = self.get_stock_price(stock['symbol'])
                if current_price is not None:
                    value = current_price * stock['shares']
                    change = ((current_price - stock['purchase_price']) / stock['purchase_price']) * 100

                    tag = "positive" if change > 0 else "negative"

                    self.tree.insert('', 'end', values=(
                        stock['symbol'],
                        f"{stock['shares']:.2f}",
                        f"${current_price:.2f}",
                        f"${value:.2f}",
                        f"{change:+.2f}%"
                    ), tags=(tag,))

                    total_value += value

            except Exception as e:
                print(f"Error updating {stock['symbol']}: {str(e)}")

        self.total_value_label.config(text=f"Total Portfolio Value: ${total_value:,.2f}")

        try:
            sensex_price = self.get_stock_price('^BSESN')
            if sensex_price is not None:
                self.sensex_label.config(
                    text=f"Sensex: {sensex_price:,.2f}"
                )
        except Exception as e:
            print(f"Error updating Sensex: {str(e)}")

        self.root.after(300000, self.update_prices)


if __name__ == '__main__':
    root = tk.Tk()
    app = StockPortfolioTracker(root)
    root.mainloop()