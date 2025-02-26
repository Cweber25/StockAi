import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense
from keras.callbacks import Callback
import matplotlib.pyplot as plt  # Import matplotlib

# 1. Fetch and Prepare Data
ticker = "NVDA"
stock = yf.Ticker(ticker)
data = stock.history(period="1y")
prices = data[['Close']].values

# Normalize data to [0, 1]
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_prices = scaler.fit_transform(prices)

# Function to create sequences
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

seq_length = 60  # Use the last 60 days to predict the next day
X, y = create_sequences(scaled_prices, seq_length)

# Split into training and testing sets
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# 2. Build the LSTM Model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(seq_length, 1)))
model.add(LSTM(50))
model.add(Dense(1))
# For now, we're using MSE loss. (You can switch to Huber loss as shown previously.)
model.compile(optimizer='adam', loss='mean_squared_error', run_eagerly=True)

# 3. Create a Custom Callback for Threshold Accuracy
class ThresholdStopping(Callback):
    def __init__(self, X_val, y_val, scaler, threshold=0.05, required_accuracy=70):
        super(ThresholdStopping, self).__init__()
        self.X_val = X_val
        self.y_val = y_val
        self.scaler = scaler
        self.threshold = threshold  # Relative error threshold (e.g., 5%)
        self.required_accuracy = required_accuracy  # Required percentage
        
    def on_epoch_end(self, epoch, logs=None):
        predictions = self.model.predict(self.X_val)
        predictions = self.scaler.inverse_transform(predictions)
        actuals = self.scaler.inverse_transform(self.y_val)
        accurate_count = np.sum(np.abs(actuals - predictions) / actuals < self.threshold)
        accuracy_percentage = (accurate_count / len(actuals)) * 100
        print(f"Epoch {epoch + 1}: Threshold accuracy = {accuracy_percentage:.2f}%")
        if accuracy_percentage >= self.required_accuracy:
            print(f"Threshold accuracy reached {accuracy_percentage:.2f}%! Stopping training.")
            self.model.stop_training = True

# Instantiate the callback using the validation set and scaler
threshold_callback = ThresholdStopping(X_test, y_test, scaler, threshold=0.05, required_accuracy=70)

# 4. Train the Model with the Callback
model.fit(X_train, y_train, epochs=20, batch_size=32,
          validation_data=(X_test, y_test),
          callbacks=[threshold_callback])

# Save the trained model to a file
model.save("stock_modelv2.h5")
print("Model saved as stock_modelv2.h5")

# 5. Make Predictions and Evaluate Metrics
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)  # Convert back to original scale
actual_prices = scaler.inverse_transform(y_test)

print("Predictions vs Actual Prices:")
print(np.hstack((predictions, actual_prices)))

def calculate_mape(y_true, y_pred):
    """Calculate Mean Absolute Percentage Error (MAPE)."""
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def calculate_threshold_accuracy(y_true, y_pred, threshold=0.05):
    """
    Calculate percentage of predictions that are within a given threshold.
    A prediction is 'accurate' if the relative error is less than the threshold.
    """
    accurate_count = np.sum(np.abs(y_true - y_pred) / y_true < threshold)
    return (accurate_count / len(y_true)) * 100

mape_val = calculate_mape(actual_prices, predictions)
threshold_accuracy_val = calculate_threshold_accuracy(actual_prices, predictions, threshold=0.05)

print("Mean Absolute Percentage Error (MAPE): {:.2f}%".format(mape_val))
print("Percentage of predictions within 5% of actual value: {:.2f}%".format(threshold_accuracy_val))

# 7. Plot Last Week's Predicted vs Actual Prices (Day-by-Day)

# Take the last 7 predictions and their corresponding actual prices from the test set:
week_predictions = predictions[-7:]
week_actual = actual_prices[-7:]
days = np.arange(7)

plt.figure(figsize=(10, 6))
# Plot actual values as a solid blue line with markers
plt.plot(days, week_actual, marker='o', linestyle='-', color='blue', label='Actual')
# Plot predicted values as a dashed red line with markers
plt.plot(days, week_predictions, marker='o', linestyle='--', color='red', label='Predicted')

plt.title("Predicted vs Actual Prices for the Last Week")
plt.xlabel("Day")
plt.ylabel("Stock Price")
plt.xticks(days, [f"Day {i+1}" for i in range(7)])
plt.legend(loc='upper left')
plt.grid(True)

# Create a table to display both the actual and predicted values below the graph.
table_data = []
for a, p in zip(week_actual, week_predictions):
    table_data.append([f"{a[0]:.2f}", f"{p[0]:.2f}"])

# Add the table below the plot.
the_table = plt.table(cellText=table_data, 
                      colLabels=["Actual", "Predicted"],
                      rowLabels=[f"Day {i+1}" for i in range(7)],
                      loc='bottom', cellLoc='center', bbox=[0, -0.35, 1, 0.3])
the_table.auto_set_font_size(False)
the_table.set_fontsize(10)

plt.subplots_adjust(left=0.15, bottom=0.4)
plt.show()
