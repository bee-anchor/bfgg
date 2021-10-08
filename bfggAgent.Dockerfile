FROM python:3.9

WORKDIR /opt/bfgg

# Add all requirements for running tests with gatling
RUN wget -O gatling.zip https://repo1.maven.org/maven2/io/gatling/highcharts/gatling-charts-highcharts-bundle/3.6.0/gatling-charts-highcharts-bundle-3.6.0-bundle.zip && \
    unzip gatling.zip && \
    mv gatling-charts-highcharts-bundle-3.6.0 gatling
RUN wget https://repo1.maven.org/maven2/com/lihaoyi/ujson_2.13/1.3.15/ujson_2.13-1.3.15.jar && \
    mv ujson_2.13-1.3.15.jar gatling/lib/ujson_2.13-1.3.15.jar
RUN wget https://repo1.maven.org/maven2/com/lihaoyi/requests_2.13/0.6.9/requests_2.13-0.6.9.jar && \
    mv requests_2.13-0.6.9.jar gatling/lib/requests_2.13-0.6.9.jar
RUN wget https://repo1.maven.org/maven2/com/lihaoyi/geny_2.13/0.6.10/geny_2.13-0.6.10.jar && \
    mv geny_2.13-0.6.10.jar gatling/lib/geny_2.13-0.6.10.jar
RUN wget https://repo1.maven.org/maven2/com/lihaoyi/upickle-core_2.13/1.3.15/upickle-core_2.13-1.3.15.jar && \
    mv upickle-core_2.13-1.3.15.jar gatling/lib/upickle-core_2.13-1.3.15.jar

# Install OpenJDK-11
RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean;

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./bfgg ./bfgg
COPY run_agent.py .
COPY run_controller.py .
RUN mkdir ~/.ssh
RUN echo "-----BEGIN OPENSSH PRIVATE KEY-----\n"\
"-----END OPENSSH PRIVATE KEY-----" > ~/.ssh/id_ed25519
RUN chmod 600 ~/.ssh/id_ed25519
RUN echo "github.com,140.82.121.3 ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==\n"\
"140.82.121.4 ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==" > ~/.ssh/known_hosts
