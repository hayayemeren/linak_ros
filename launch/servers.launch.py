import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    # DEFINE YOUR 8 DESKS HERE
    my_desks = [
        # The Standard Desks (Offset 590)
        {'name': 'desk1', 'mac': 'E8:9D:29:FE:52:ED', 'offset': 590},
        # Add other desks here
    ]

    node_list = []

    for desk in my_desks:
        node = Node(
            package='linak_ros',
            executable='smart_desk',
            namespace=desk['name'],
            name='driver',
            output='screen',
            parameters=[
                {'mac': desk['mac']},
                {'offset_mm': desk['offset']},     # Passes the specific offset!
                {'scale_factor': 0.1}              # Usually 0.1 for all recent Linak desks
            ]
        )
        node_list.append(node)

    return LaunchDescription(node_list)