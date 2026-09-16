import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    my_desks = [
        # The Standard Desks (Offset 590)
        {'name': 'island1', 'mac': 'F2:24:44:57:7F:9A', 'offset': 620},
        {'name': 'island2', 'mac': 'D3:B5:D1:F4:0D:7D', 'offset': 620},
        {'name': 'island3', 'mac': 'E6:B6:5F:D7:71:EC', 'offset': 610},
        {'name': 'island4', 'mac': 'F8:2B:62:8A:2B:8A', 'offset': 630},
        {'name': 'stove', 'mac': 'F5:42:26:A5:2F:84', 'offset': 610},
        {'name': 'oven', 'mac': 'EA:01:40:0B:4D:0A', 'offset': 750},
        {'name': 'clothwasher', 'mac': 'F7:47:02:9A:85:5D', 'offset': 990},
        {'name': 'dishwasher', 'mac': 'E7:75:89:F7:6E:5E', 'offset': 990},
        #{'name': 'wall1', 'mac': 'E8:9D:29:FE:52:ED', 'offset': 620},
        #{'name': 'wall2', 'mac': 'E8:9D:29:FE:52:ED', 'offset': 620},
        #{'name': 'wall3', 'mac': 'E8:9D:29:FE:52:ED', 'offset': 620},
        {'name': 'window2', 'mac': 'E4:F7:BB:C7:07:64', 'offset': 620},
        {'name': 'window3', 'mac': 'D1:B9:0D:B3:19:3A', 'offset': 620}
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