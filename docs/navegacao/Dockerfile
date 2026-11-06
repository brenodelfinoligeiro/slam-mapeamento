FROM robo-movel/slam:jazzy
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ros-jazzy-nav2-planner ros-jazzy-nav2-controller ros-jazzy-nav2-bt-navigator ros-jazzy-nav2-behaviors ros-jazzy-nav2-lifecycle-manager ros-jazzy-nav2-navfn-planner ros-jazzy-dwb-core ros-jazzy-dwb-critics ros-jazzy-dwb-plugins ros-jazzy-nav2-rviz-plugins ros-jazzy-nav2-regulated-pure-pursuit-controller && apt-get clean
ENV ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST PYTHONUNBUFFERED=1
