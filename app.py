from flask import Flask, request, render_template, send_file
import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date_str = request.form['date']
        tickers_str = request.form['tickers']
        tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]

        try:
            start_date = datetime.strptime(date_str, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
        except ValueError:
            return "  YYYY-MM-DD"

        output_files = []
        os.makedirs("data", exist_ok=True)

        for ticker in tickers:
            print(f" {ticker} ...")

            df = yf.download(ticker, start=start_date, end=end_date, interval="1m", prepost=False)

            if df.empty:
                print(f"{ticker} ")
                continue

            df[""] = df["Close"] * df["Volume"]
            df.index = df.index.tz_convert("America/New_York")
            df = df.between_time("09:30", "16:00")
            df.index = df.index.tz_localize(None)

            filename = f"{ticker}_{date_str}_1min.xlsx"
            df.to_excel(f"data/{filename}")
            output_files.append(filename)

        return render_template('result.html', files=output_files)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join('data', filename)
    return send_file(file_path, as_attachment=True)
PK