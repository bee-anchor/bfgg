FROM python:3.9

WORKDIR /opt/bfgg

# Install OpenJDK-11
RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean;

# Install Gatling for report gen
RUN wget -O gatling.zip https://repo1.maven.org/maven2/io/gatling/highcharts/gatling-charts-highcharts-bundle/3.6.0/gatling-charts-highcharts-bundle-3.6.0-bundle.zip && \
    unzip gatling.zip && \
    mv gatling-charts-highcharts-bundle-3.6.0 gatling

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./bfgg ./bfgg
COPY run_controller.py .