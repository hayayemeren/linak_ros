# Navigate to workspace
cd ~/ros2_ws
colcon build --packages-select linak_ros
source install/setup.bash

# Run the Node (Starts all desks defined in the launch file)
ros2 launch linak_ros servers.launch.py

# Topics (Monitoring)
# Note: Change 'desk1' to match whichever desk you are testing
ros2 topic echo /desk1/current_height
ros2 topic echo /desk1/is_moving

# Command the Desk
# Sends a target height in millimeters (e.g., 800 mm)
ros2 topic pub /desk1/set_height std_msgs/msg/Int32 "{data: 800}" -1
