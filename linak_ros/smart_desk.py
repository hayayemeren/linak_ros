import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, Bool
import asyncio
import threading
import traceback

from bleak import BleakClient
from linak_controller.desk import Desk

class HeightCommand:
    def __init__(self, value):
        self.value = value

class SmartDeskDriver(Node):
    def __init__(self):
        super().__init__('smart_desk_driver')

        self.declare_parameter('mac', 'XX:XX:XX:XX:XX:XX')
        self.declare_parameter('offset_mm', 590)
        self.declare_parameter('scale_factor', 0.1)

        self.mac_address = self.get_parameter('mac').value
        self.OFFSET_MM = self.get_parameter('offset_mm').value
        self.SCALE_FACTOR = self.get_parameter('scale_factor').value

        self.height_pub = self.create_publisher(Int32, 'current_height', 10)
        self.moving_pub = self.create_publisher(Bool, 'is_moving', 10)

        self.subscription = self.create_subscription(
            Int32, 'set_height', self.command_callback, 10
        )

        self.target_height = None
        self.current_height_mm = 0
        self.is_moving = False
        self.move_task = None  # To track the background move task
        
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.start_async_loop, daemon=True)
        self.thread.start()

        self.get_logger().info(f"Non-Blocking Driver Started: {self.mac_address}")

    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.run_desk_logic())

    async def run_desk_logic(self):
        while rclpy.ok():
            try:
                self.get_logger().info(f"Connecting to {self.mac_address}...")
                
                async with BleakClient(self.mac_address, timeout=20.0) as client:
                    if not client.is_connected:
                        await asyncio.sleep(5.0)
                        continue

                    self.get_logger().info("Connected!")
                    desk = Desk(self.mac_address, client)
                    
                    desk.config = {
                        "mac_address": self.mac_address,
                        "base_height": 0, 
                        "adapter_height": 0, 
                        "max_height": 10000, 
                        "min_height": 0,
                        "move_command_period": 0.05,
                    }
                    
                    await desk.initialise(desk.config, client)
                    self.get_logger().info("Desk Ready! Polling...")

                    while rclpy.ok() and client.is_connected:
                        try:
                            # 1. READ RAW DATA
                            data = await desk.get_height_speed()
                            
                            # Parse Height
                            raw_height = data.height if hasattr(data, 'height') else (data[0] if isinstance(data, tuple) else data)
                            h_int = int(raw_height.value) if hasattr(raw_height, 'value') else int(raw_height)
                            self.current_height_mm = int((h_int * self.SCALE_FACTOR) + self.OFFSET_MM)

                            # Parse Speed
                            raw_speed = 0
                            if hasattr(data, 'speed'):
                                raw_speed = data.speed
                            elif isinstance(data, tuple) and len(data) > 1:
                                raw_speed = data[1]
                            
                            s_int = int(raw_speed.value) if hasattr(raw_speed, 'value') else int(raw_speed)
                            
                            # DEBUG: Uncomment this if you suspect speed is always 0
                            # self.get_logger().info(f"Raw Speed: {s_int}")

                            # 2. UPDATE STATUS
                            self.is_moving = (s_int != 0)
                            
                            self.height_pub.publish(Int32(data=self.current_height_mm))
                            self.moving_pub.publish(Bool(data=self.is_moving))

                            # 3. MOVE LOGIC (BACKGROUND TASK)
                            if self.target_height is not None:
                                diff = self.target_height - self.current_height_mm
                                
                                # If we need to move AND we are not already running a move command
                                if abs(diff) > 10:
                                    if self.move_task is None or self.move_task.done():
                                        self.get_logger().info(f"Starting Move -> {self.target_height}")
                                        
                                        target_raw = int((self.target_height - self.OFFSET_MM) / self.SCALE_FACTOR)
                                        cmd = HeightCommand(target_raw)
                                        
                                        # CRITICAL FIX: Run move_to in background!
                                        self.move_task = asyncio.create_task(desk.move_to(cmd))
                                else:
                                    self.target_height = None
                                    self.get_logger().info("Target Reached.")

                        except Exception:
                            pass
                        
                        await asyncio.sleep(0.1)

            except Exception as e:
                self.get_logger().error(f"Connection Error: {e}")
                await asyncio.sleep(5.0)

    def command_callback(self, msg):
        self.target_height = msg.data
        self.get_logger().info(f"Received Command: {self.target_height}")

def main(args=None):
    rclpy.init(args=args)
    node = SmartDeskDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()