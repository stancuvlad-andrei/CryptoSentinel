# CryptoSentinel: Real-Time Asset Monitoring & Audit System

## 1. Executive Summary
**CryptoSentinel** is a distributed financial telemetry system designed for high-frequency asset tracking.

In an environment where market data latency and compliance are critical, CryptoSentinel offers a hybrid solution: a **low-latency TCP socket architecture** for real-time trader dashboards, coupled with an **asynchronous cloud audit trail** for regulatory compliance. This ensures that while traders get instant price updates, every critical data point is immutably logged in the cloud.

---

## 2. System Architecture

The solution is built as a distributed system comprising three decoupled components:

### A. The Core Engine (Data Aggregator)
* **Role:** The central hub connecting the public internet to the internal network.
* **Function:** Connects to the **CoinGecko API** to fetch live Bitcoin prices. It uses multi-threading to ensure non-blocking performance while serving multiple clients simultaneously.
* **Location:** `core_server/main.py`

### B. The Trader Dashboard (Client App)
* **Role:** The end-user visualization tool.
* **Function:** A dedicated GUI application (Tkinter) that connects to the Core Engine via raw **TCP Sockets**. It receives push updates instantly, bypassing the overhead of HTTP browsers for maximum speed.
* **Location:** `desktop_client/gui.py`

### C. The Cloud Audit Vault
* **Role:** The remote compliance logger.
* **Function:** A Flask microservice hosted on **Render.com**. The Core Engine automatically uploads audit logs to this service via HTTPS POST requests to ensure data integrity.
* **Location:** `cloud_service/app.py` (Deployed to Cloud)

---

## 3. Technical Specifications

| Feature | Specification |
| :--- | :--- |
| **Language** | Python 3.9+ |
| **Ingestion Protocol** | REST API (HTTPS) |
| **Distribution Protocol** | TCP/IP Sockets (Port 5000) |
| **GUI Framework** | Tkinter (Standard Library) |
| **Cloud Framework** | Flask + Gunicorn |
| **Concurrency** | `threading` (Python Standard Library) |

---

## 4. Installation & Deployment Guide

### Prerequisites
* Python 3.x installed.
* Internet connection (for CoinGecko API and Cloud Logging).

### Step 1: Environment Setup
Clone the repository and set up the virtual environment to isolate dependencies.

```bash
# 1. Initialize Virtual Environment
python -m venv venv

# 2. Activate Environment
# Windows:
.\venv\Scripts\Activate
# Mac/Linux:
source venv/bin/activate

# 3. Install Dependencies
pip install -r requirements.txt