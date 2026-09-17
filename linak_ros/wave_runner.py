import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import math
import time

class WaveRunner(Node):
    def __init__(self):
        super().__init__('wave_runner')
        
        self.desks = {
            'island1': {'pub': self.create_publisher(Int32, '/island1/set_height', 10), 'phase': 0.0},
            'stove':   {'pub': self.create_publisher(Int32, '/stove/set_height', 10),   'phase': 0.0},
            
            'oven':    {'pub': self.create_publisher(Int32, '/oven/set_height', 10),    'phase': 2.094},
            'island3': {'pub': self.create_publisher(Int32, '/island3/set_height', 10), 'phase': 2.094},
            
            'island2': {'pub': self.create_publisher(Int32, '/island2/set_height', 10), 'phase': 4.188},
            'island4': {'pub': self.create_publisher(Int32, '/island4/set_height', 10), 'phase': 4.188},
        }
        
        # Pure Additive Wave Limits
        self.min_height = 752
        self.amplitude = 246  # Total range: [752, 998]
        self.speed = 0.3
        
        self.start_time = time.time()
        self.is_shutting_down = False
        
        self.timer = self.create_timer(2.0, self.timer_callback)
        self.get_logger().info("Additive Wave Started. Range strictly bounded: 752mm - 998mm.")

    def timer_callback(self):
        if self.is_shutting_down:
            return
            
        t = time.time() - self.start_time
        
        for name, data in self.desks.items():
            # The (1 - cos)/2 modifier strictly oscillates between 0.0 and 1.0
            wave_modifier = (1 - math.cos(self.speed * t - data['phase'])) / 2
            target = int(self.min_height + (self.amplitude * wave_modifier))
            
            msg = Int32()
            msg.data = target
            data['pub'].publish(msg)
            self.get_logger().info(f"{name} target: {target}mm")

    def reset_to_base(self):
        self.is_shutting_down = True
        self.get_logger().info("Session ending. Forcing reset to 752mm...")
        
        msg = Int32()
        msg.data = 752
        
        end_time = time.time() + 5.0
        while time.time() < end_time:
            for name, data in self.desks.items():
                data['pub'].publish(msg)
            time.sleep(0.5)
            
        self.get_logger().info("Reset successful. Shutting down.")

def main(args=None):
    rclpy.init(args=args)
    node = WaveRunner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.reset_to_base()
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()