# Jupyter Lab + PySpark 3.5.6 (Python 3.12, Java 17), zgodnie z maszyna z laboratoriow
FROM python:3.12-slim-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends openjdk-17-jre-headless procps \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
      pyspark==3.5.6 \
      jupyterlab \
      happybase \
      kafka-python \
      requests \
      pandas \
      pyarrow \
      matplotlib \
      plotly

WORKDIR /home/work
EXPOSE 8888 4040

# token wylaczony - port wystawiony tylko na localhost
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", \
     "--ServerApp.token=", "--ServerApp.root_dir=/home/work"]
