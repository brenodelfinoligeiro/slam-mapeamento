FROM robo-movel/validacao-descricao:jazzy-r05
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ros-jazzy-robot-localization python3-numpy && apt-get clean
ENV ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST PYTHONUNBUFFERED=1
