import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class DrawCircleNode(Node):
    def __init__(self):
        super().__init__("draw_circle")
        self.get_logger().info("Draw circle node has been started")
        self.timer = self.create_timer(0.5, self.sends_velocity_command)
        self.cmd_vel_pub_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)


    def sends_velocity_command(self):
        msg = Twist()
        msg.linear.x = 2.0
        msg.angular.z = 1.0
        self.cmd_vel_pub_.publish(msg)

def main(args = None):
    rclpy.init(args = args)

    node = DrawCircleNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()