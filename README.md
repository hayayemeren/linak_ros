# Navigate to workspace
cd ~/ros2_ws

colcon build --packages-select linak_ros

source install/setup.bash

# Run the Node 
ros2 launch linak_ros servers.launch.py

# Note: Change 'desk1' to match whichever desk you are testing
ros2 topic echo /island1/current_height

ros2 topic echo /island1/is_moving

# Sends a target height in millimeters (e.g., 800 mm)
ros2 topic pub /island1/set_height std_msgs/msg/Int32 "{data: 800}" -1

# Calibration data send
ros2 topic pub --once /island1/set_current_height std_msgs/msg/Int32 "{data: 610}"

# Wave runner
ros2 run linak_ros wave_runner

# Reset Desks
ros2 run linak_ros reset_desks