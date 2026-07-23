# AirMind

> **AI-Powered Urban Air Quality Intelligence for Smarter City Interventions**

AirMind is an AI-driven environmental intelligence platform that transforms real-time air quality data into actionable insights for city authorities. By combining live monitoring, historical replay, hotspot detection, and machine learning-based forecasting, AirMind enables proactive decision-making instead of reactive pollution management.

---

# Demo Video

Watch a 4-minute walkthrough of AirMind here:

👉 https://drive.google.com/file/d/1jVggToJY6ViiLqf1pairEjZQkahnFdKr/view?usp=drive_link

---

## Overview

Air pollution remains one of the most pressing environmental challenges in rapidly growing urban areas. Although cities deploy Continuous Ambient Air Quality Monitoring Stations (CAAQMS) to measure pollutants such as PM2.5 and PM10, existing systems are primarily designed for monitoring rather than decision support. Authorities often receive historical or real-time measurements but lack predictive insights that help prioritize interventions before pollution reaches hazardous levels.

AirMind addresses this challenge by integrating real-time environmental monitoring with machine learning-based forecasting into a single intelligent dashboard. The platform provides historical replay, hotspot prioritization, pollution forecasting, and interactive geospatial visualization to assist city authorities in making informed, proactive decisions.

---

## Problem Statement

Current urban air quality monitoring systems face several limitations:

- Primarily reactive instead of predictive
- Limited support for operational decision-making
- No intelligent prioritization of high-risk monitoring stations
- Difficult to interpret pollution trends across multiple locations
- Fragmented visualization of environmental information

As a result, authorities often respond only after air quality has significantly deteriorated.

---

## Our Solution

AirMind provides an AI-powered environmental intelligence platform capable of:

- Monitoring multiple air quality stations simultaneously
- Replaying historical pollution conditions
- Forecasting future PM2.5 concentrations using machine learning
- Identifying high-risk pollution hotspots
- Presenting insights through an intuitive operational dashboard
- Supporting proactive urban environmental management

Instead of simply displaying measurements, AirMind helps decision-makers understand where pollution is likely to worsen and which locations require immediate attention.

---

# Features

- Real-time air quality monitoring
- Historical pollution replay
- PM2.5 forecasting using XGBoost
- Interactive GIS-based visualization
- Hotspot detection and prioritization
- AI-powered operational decision brief
- Responsive dashboard interface
- Clean, modern UI inspired by Apple and Linear

---

# System Architecture

```
                     OpenAQ API
                          │
                          ▼
                Data Collection Layer
                          │
                          ▼
             Data Cleaning & Preprocessing
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
 Historical Replay              XGBoost Forecasting
          │                               │
          └───────────────┬───────────────┘
                          ▼
                   FastAPI Backend
                          │
                    REST API Services
                          │
                          ▼
             Next.js + React Dashboard
                          │
                          ▼
      Interactive Leaflet Visualization
                          │
                          ▼
          AI Decision Support Dashboard
```

---

# Technology Stack

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- Framer Motion
- React Leaflet

## Backend

- FastAPI
- Python
- Pandas
- NumPy

## Machine Learning

- XGBoost
- Scikit-learn

## Data Source

- OpenAQ API
- CPCB Monitoring Stations
- TNPCB Monitoring Stations

---

# Dataset

AirMind uses publicly available air quality measurements obtained through the OpenAQ platform. Data is collected from Continuous Ambient Air Quality Monitoring Stations (CAAQMS) across Chennai.

Primary variables include:

- PM2.5
- PM10
- Temperature
- Relative Humidity
- Wind Speed
- Wind Direction

These variables are processed and used for forecasting future PM2.5 concentrations.

---

# Machine Learning Pipeline

1. Data Collection
2. Data Preprocessing
3. Feature Engineering
4. Model Training
5. PM2.5 Forecasting using XGBoost
6. Hotspot Ranking
7. Dashboard Visualization

---

# Installation

Clone the repository:

```bash
git clone https://github.com/your-username/AirMind.git

cd AirMind
```

---

## Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# Running the Application

Backend

```
http://localhost:8000
```

Frontend

```
http://localhost:3000
```

---

# Results

AirMind successfully demonstrates:

- Real-time environmental monitoring
- Historical pollution replay
- Machine learning-based PM2.5 forecasting
- Automated hotspot prioritization
- Interactive GIS visualization
- AI-assisted operational summaries

The platform enables authorities to move from reactive monitoring to proactive environmental management.

---

# Future Enhancements

- Multi-pollutant forecasting
- Satellite imagery integration
- Weather-aware forecasting
- Traffic data integration
- LLM-powered natural language querying
- Mobile application
- Automated alert notifications

---

# Project Report

👉 https://drive.google.com/file/d/1ofBJFUGi2mREsNk8AKklClTXs8OUlCQD/view?usp=sharing
