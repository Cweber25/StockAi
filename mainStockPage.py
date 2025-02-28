import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window

class StockPage(BoxLayout):
    def __init__(self, **kwargs):
        super(StockPage, self).__init__(orientation='vertical', **kwargs)
        
        # List of tickers to cycle through
        self.tickers = ['NVDA', 'CVS', 'FNILX', 'PLTR', 'RGTI']  # Add or remove tickers as desired
        self.ticker_index = 0  # Start with the first ticker in the list
        
        self.graph_file = "stock_graph.png"
        self.initial = None  # For tracking swipe starting point
        
        # Label to show the current price
        self.price_label = Label(text="Fetching price...", font_size='24sp', size_hint=(1, 0.2))
        self.add_widget(self.price_label)
        
        # Image widget to display the graph
        self.graph_image = Image(source=self.graph_file, allow_stretch=True, keep_ratio=True, size_hint=(1, 0.8))
        self.add_widget(self.graph_image)
        
        # Update immediately and then every 60 seconds
        self.update_page()
        Clock.schedule_interval(lambda dt: self.update_page(), 60)
    
    def update_page(self):
        # Get the current ticker from the list
        current_ticker = self.tickers[self.ticker_index]
        
        # Fetch one month of historical data for the current ticker
        stock = yf.Ticker(current_ticker)
        data = stock.history(period="1mo")
        
        # Apply a modern style to the graph (using an available style)
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Plot the closing prices with custom styling
        ax.plot(data.index, data['Close'], linewidth=2.5, color='royalblue',
                marker='o', markersize=5, label='Close Price')
        
        # Format the x-axis for dates
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        fig.autofmt_xdate()
        
        # Set title and labels with custom font sizes
        ax.set_title(f"{current_ticker} Stock Price (Last Month)", fontsize=18, pad=15)
        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel("Price (USD)", fontsize=14)
        ax.legend(fontsize=12, loc='upper left')
        
        # Remove top and right spines for a cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(self.graph_file)
        plt.close(fig)
        
        # Refresh the graph image widget
        self.graph_image.reload()
        
        # Update the current price label
        current_price = stock.info.get("regularMarketPrice", None)
        if current_price:
            self.price_label.text = f"{current_ticker} Price: ${current_price:.2f}"
        else:
            self.price_label.text = f"{current_ticker} Price: N/A"
    
    def on_touch_down(self, touch):
        # Capture the initial x-coordinate when a touch begins
        self.initial = touch.x
        return super(StockPage, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        # Determine swipe direction by comparing the ending x-coordinate with the initial value
        if self.initial is None:
            return super(StockPage, self).on_touch_up(touch)
        
        if touch.x < self.initial:
            # Swipe left: move to the next ticker
            self.ticker_index = (self.ticker_index + 1) % len(self.tickers)
            print("Swipe left detected. New ticker:", self.tickers[self.ticker_index])
            self.update_page()
        elif touch.x > self.initial:
            # Swipe right: move to the previous ticker
            self.ticker_index = (self.ticker_index - 1) % len(self.tickers)
            print("Swipe right detected. New ticker:", self.tickers[self.ticker_index])
            self.update_page()
        
        return super(StockPage, self).on_touch_up(touch)

class StockApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)  # White background
        return StockPage()

if __name__ == '__main__':
    StockApp().run()
