# Real-Time Application Metrics Dashboard

## Overview

This project demonstrates a real-time interactive dashboard for mimicking application metric data, leveraging powerful big data tools such as Apache Kafka and Apache Spark. It serves as an end-to-end template for building data engineering projects that utilize Apache Kafka, Apache Spark, and PostgreSQL database, all containerized with Docker.

## Features

- **Real-Time Data Processing**: Uses Apache Kafka for message queuing and Apache Spark for stream processing.
- **Interactive Dashboard**: Utilizes Plotly Dash to create dynamic and real-time visualizations of the processed data.
- **Modular Design**: The project is structured to be easily extensible for various use cases involving real-time data streams.
- **Ease of Setup**: Can be launched with a simple Docker Compose command.

## Architecture

This project integrates several technologies into a cohesive pipeline:

- **Apache Kafka**: Handles incoming data streams and acts as a buffer for log data.
- **Apache Spark**: Processes the data in real-time, performing computations and aggregations.
- **PostgreSQL**: Stores the processed data for persistence and visualization.
- **Plotly Dash**: Provides a web-based dashboard for displaying interactive visualizations of the data metrics.

## Getting Started

### Prerequisites

Ensure you have Docker and Docker Compose installed on your machine. These tools are required to create the containerized environment for running the services.

### Installation

1. **Clone the Repository**

   Start by cloning this repository to your local machine using ssh:

   ```bash
   git clone git@github.com:firefly-cmd/data-engineering-template.git
   cd data-engineering-template

2. **Launch the services**

    Start the services with docker compose

   ```bash
    docker-compose up --build


3. **Checkout the dashboard**

    You can now go to the localhost:8050 to view the dashboard.

### Customization

    You can customize this template for your own projects by modifying the source code to adjust the data processing logic, the types of metrics displayed, or the visual appearance of the dashboard.