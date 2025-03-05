from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')

import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

class StockPage(BoxLayout):
    def __init__(self, **kwargs):
        super(StockPage, self).__init__(orientation='vertical', **kwargs)
        
        self.tickers = ['NVDA', 'CVS', 'FNILX', 'PLTR', 'RGTI']
        self.ticker_index = 0
        self.stock_data = {}  # Dictionary to store preloaded stock data
        self.initial = None  
        
        self.price_label = Label(text="Fetching price...", font_size='24sp', size_hint=(1, 0.2))
        self.add_widget(self.price_label)
        
        self.graph_image = Image(allow_stretch=True, keep_ratio=True, size_hint=(1, 0.8))
        self.add_widget(self.graph_image)
        
        self.preload_stock_data()  # Start preloading data
        self.update_page()
        Clock.schedule_interval(lambda dt: self.update_page(), 60)
    
    def preload_stock_data(self):
        def fetch_data():
            for ticker in self.tickers:
                stock = yf.Ticker(ticker)
                self.stock_data[ticker] = stock.history(period="1mo")
        
        threading.Thread(target=fetch_data, daemon=True).start()
    
    def update_page(self):
        current_ticker = self.tickers[self.ticker_index]
        if current_ticker not in self.stock_data:
            return  # Skip update if data is not ready yet
        
        data = self.stock_data[current_ticker]
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        
        ax.plot(data.index, data['Close'], linewidth=2, color='royalblue',
                marker='o', markersize=4, label='Close Price')
        
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        fig.autofmt_xdate()
        
        ax.set_title(f"{current_ticker} Stock Price (Last Month)", fontsize=16, pad=10)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Price (USD)", fontsize=12)
        ax.legend(fontsize=10, loc='upper left')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)
        
        core_image = CoreImage(buf, ext="png")
        self.graph_image.texture = core_image.texture
        self.graph_image.canvas.ask_update()
        
        stock = yf.Ticker(current_ticker)
        current_price = stock.info.get("regularMarketPrice", None)
        self.price_label.text = f"{current_ticker} Price: ${current_price:.2f}" if current_price else f"{current_ticker} Price: N/A"
    
    def on_touch_down(self, touch):
        self.initial = touch.x
        return super(StockPage, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.initial is None:
            return super(StockPage, self).on_touch_up(touch)

        swipe_threshold = 50  
        if touch.x < self.initial - swipe_threshold:
            self.ticker_index = (self.ticker_index + 1) % len(self.tickers)
        elif touch.x > self.initial + swipe_threshold:
            self.ticker_index = (self.ticker_index - 1) % len(self.tickers)
        
        Clock.unschedule(self.update_page)
        Clock.schedule_once(lambda dt: self.update_page(), 0)
        self.initial = None
        return super(StockPage, self).on_touch_up(touch)

class StockApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        return StockPage()

if __name__ == '__main__':
    StockApp().run()
