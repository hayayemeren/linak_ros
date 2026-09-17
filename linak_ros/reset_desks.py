import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import time

class DeskResetter(Node):
    def __init__(self):
        super().__init__('desk_resetter')
        
        # The exact 6 desks from your wave setup
        desk_names = ['island1', 'oven', 'island2', 'island4', 'island3', 'stove']
        
        self.publishers_dict = {}
        for name in desk_names:
            topic = f'/{name}/set_height'
            self.publishers_dict[name] = self.create_publisher(Int32, topic, 10)
            
        self.target_height = 750

    def run_reset(self):
        self.get_logger().info(f"Broadcasting reset command ({self.target_height}mm) to all desks...")
        
        msg = Int32()
        msg.data = self.target_height
        
        # Publish multiple times over 2 seconds to guarantee delivery 
        # and bypass any temporary background move locks in the drivers.
        for _ in range(4):
            for name, pub in self.publishers_dict.items():
                pub.publish(msg)
            self.get_logger().info("Messages published. Waiting 0.5s...")
            time.sleep(0.5)
            
        self.get_logger().info("Reset sequence complete. Desks should now be returning to 75cm.")

def main(args=None):
    rclpy.init(args=args)
    node = DeskResetter()
    
    try:
        # Run the reset sequence once, then immediately exit
        node.run_reset()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()