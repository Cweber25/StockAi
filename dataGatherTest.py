import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense

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
model.compile(optimizer='adam', loss='mean_squared_error')

# 3. Train the Model
model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

# Save the trained model to a file
model.save("stock_model.h5")
print("Model saved as stock_model.h5")

# 4. Make Predictions
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)  # Convert back to original scale

# For comparison, convert actual prices back to original scale
actual_prices = scaler.inverse_transform(y_test)

print("Predictions vs Actual Prices:")
print(np.hstack((predictions, actual_prices)))

# Optional: Loading the saved model to verify it works
# loaded_model = load_model("stock_model.h5")
# loaded_predictions = loaded_model.predict(X_test)
