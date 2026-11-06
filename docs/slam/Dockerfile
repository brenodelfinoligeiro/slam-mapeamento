FROM robo-movel/simulacao:jazzy
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ros-jazzy-slam-toolbox ros-jazzy-nav2-map-server && apt-get clean
ENV ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST PYTHONUNBUFFERED=1
# XTest é usado somente para confirmar o modal do RViz no Xvfb privado.
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends libxtst6 && apt-get clean
