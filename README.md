# my_restaurant.ai
# Restaurant Sales Forecasting Tool

This project provides a lightweight forecasting system designed to help restaurant operations predict short-term sales using historical data. The tool analyzes daily net sales by store and generates a 7-day forecast to support labor scheduling, food preparation, and inventory planning.

## Project Overview

The primary forecasting method uses a trimmed mean approach based on the previous six occurrences of the same weekday. By removing the highest and lowest values and averaging the remaining days, the model produces stable baseline forecasts that reduce the impact of outliers.

An optional PyTorch version is also included for future machine learning experimentation.

## Business Use Case

Restaurant managers often rely on experience or manual estimates to forecast daily demand. This project demonstrates how historical sales data can be used to create a more consistent, data-driven forecasting process.

Potential business benefits include:

- Better labor planning
- Improved prep levels
- Reduced food waste
- More consistent operational forecasting across stores

## Features

- Store-level daily sales forecasting
- 7-day forecast generation
- Outlier-resistant trimmed mean logic
- Optional multipliers for events or promotions
- Optional PyTorch-based forecasting model
- Simple CSV input and output workflow

## Repository Structure

```text
restaurant-sales-forecasting/
│
├── data/
│   ├── sample_sales_data.csv
│   └── README.md
│
├── scripts/
│   ├── forecast_trimmed_mean.py
│   └── forecast_pytorch.py
│
├── output/
│   └── forecast_example.csv
│
├── docs/
│   └── architecture_overview.png
│
├── .gitignore
├── requirements.txt
└── README.md
