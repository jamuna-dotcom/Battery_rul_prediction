# BESS Enterprise Battery Analytics & Management System

## 📌 Overview

The **BESS Enterprise Battery Analytics & Management System** is a Flask-based web application designed for monitoring and analyzing Battery Energy Storage Systems (BESS). The system provides battery health analytics, Remaining Useful Life (RUL) prediction, real-time telemetry, user authentication, and REST API services for integration with external SCADA systems and hardware controllers.

## 🚀 Key Features

* 🔐 **User Authentication**

  * User registration and login
  * Secure password hashing using Scrypt
  * Session-based authentication
  * Logout functionality

* 🔋 **Battery Health Monitoring**

  * State of Health (SOH) calculation
  * Battery capacity monitoring
  * Temperature monitoring
  * Battery severity classification

* 📊 **RUL Prediction**

  * Physics-informed power-law based RUL estimation
  * Predicts remaining battery life in cycles
  * Supports different model-engine configurations

* ⚡ **Real-Time Telemetry**

  * Server-Sent Events (SSE) for continuous telemetry updates
  * Simulated battery capacity and temperature data
  * Real-time SOH and RUL calculations

* 🌐 **REST API**

  * JSON-based battery prediction endpoint
  * External controller and SCADA integration
  * OpenAPI 3.0 specification
  * Swagger UI API documentation

* 🗄️ **Database**

  * SQLite database
  * SQLAlchemy ORM
  * User profile and configuration storage

## 🛠️ Technologies Used

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Login
* SQLite
* REST API
* OpenAPI 3.0
* Swagger UI
* Server-Sent Events (SSE)
* JSON
* HTML/CSS/JavaScript

## 🔄 System Workflow

1. User registers or logs into the application.
2. The authenticated user accesses the BESS dashboard.
3. Battery parameters such as capacity and temperature are received.
4. The system calculates the battery **State of Health (SOH)**.
5. The system estimates **Remaining Useful Life (RUL)** in cycles.
6. Battery conditions are classified as **Nominal, Warning, or Critical**.
7. Real-time telemetry can be streamed through SSE.
8. External systems can access battery predictions through the REST API.
9. API functionality can be explored through Swagger documentation.

## 📡 API Endpoints

### Battery Prediction

`POST /api/v1/predict`

The endpoint accepts battery parameters such as:

* Battery ID
* Capacity
* Average temperature
* Internal resistance
* Cycle number
* Peak voltage
* Model engine

The API returns:

* SOH percentage
* Predicted RUL cycles
* System status
* Inference latency

The project includes an OpenAPI 3.0 specification and Swagger UI documentation for the API.

## 📈 Battery Status Classification

The system classifies battery conditions based on temperature and SOH:

* **Nominal** – Battery operating within normal conditions
* **Warning** – Battery parameters indicate an abnormal condition
* **Critical** – Battery temperature or SOH reaches a critical threshold

## 📂 Project Structure

```text
BESS-Enterprise-BMS/
│
├── app.py
├── templates/
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
│
├── bess_saas.db
├── requirements.txt
└── README.md
```

## ▶️ Running the Project

Install the required dependencies:

```bash
pip install flask flask-sqlalchemy flask-login werkzeug
```

Run the Flask application:

```bash
python app.py
```

The application runs on:

```text
http://localhost:5000
```

Swagger API documentation is available at:

```text
http://localhost:5000/docs
```

## 🎯 Project Objective

The objective of this project is to provide a software platform for **battery health monitoring, predictive maintenance, real-time telemetry, and external system integration** within Battery Energy Storage Systems.

## 🔮 Future Enhancements

* Integration with real BMS hardware
* Machine-learning-based RUL prediction
* Battery degradation forecasting
* Interactive analytics dashboards
* Cloud-based telemetry storage
* Multi-battery fleet monitoring
* Advanced anomaly detection
* Role-based access control
* Production-grade API authentication
* Deployment using Docker and cloud infrastructure

## 📄 License

This project can be used for educational and research purposes. Add an appropriate open-source license before public distribution.
