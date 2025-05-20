from pty import spawn

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from turtlesim.srv import SetPen
from turtlesim.srv import Spawn
from turtlesim.srv import Kill

class Turtle:
    def __init__(self, node, name):
        self.pose = Pose()
        self.future = 0
        self.node = node
        self.name = name


        self.pose_subscriber = self.node.create_subscription(
            Pose, f"/{self.name}/pose", self.pose_callback, 10)

        self.cmd_vel_pub_ = self.node.create_publisher(
            Twist, f"/{self.name}/cmd_vel", 10)

    def sends_velocity_command(self, msg: Twist):
        self.cmd_vel_pub_.publish(msg)

    def pose_callback(self, msg: Pose):
        self.pose = msg

    def get_pose(self):
        return self.pose

    def call_set_pen_service(self, r, g, b, width, off):
        client = self.node.create_client(SetPen, f"/{self.name}/set_pen")
        while not client.wait_for_service(1.0):
            self.node.get_logger().warn("Waiting for service...")

        request = SetPen.Request()
        request.r = r
        request.g = g
        request.b = b
        request.width = width
        request.off = off

        self.future = client.call_async(request)

    def call_kill_service(self):
        client = self.node.create_client(Kill, "/kill")

        while not client.wait_for_service(1.0):
            self.node.get_logger().warn("Waiting for /kill service...")

        request = Kill.Request()
        request.name = self.name

        self.future = client.call_async(request)

class TurtleMaster(Node):
    def __init__(self):
        self.turtle_state = [0, 0, 0, 0, 0, 0]
        self.service_flag = [0, 0, 0, 0, 0, 0]

        self.future = 0

        self.previous = 0
        self.previous2 = 0
        self.final_y = 1.0

        super().__init__("turtle_master")

        self.call_spawn_service("circle", 5.3, 7.0)
        self.call_spawn_service("left", 5.6, 6.4)
        self.call_spawn_service("up", 8.1, 8.1)
        self.call_spawn_service("right_window", 6.0, 6.0)
        self.call_spawn_service("left_window", 5.0, 6.0)

        self.turtle = [Turtle(self, "turtle1"),
                         Turtle(self, "circle"),
                         Turtle(self, "left"),
                         Turtle(self, "up"),
                         Turtle(self, "right_window"),
                         Turtle(self, "left_window")]

        self.timer = self.create_timer(0.01, self.update_motors)

    def update_motors(self):
        self.motor_turtle1()
        self.motor_turtle2()
        self.motor_turtle3()
        self.motor_turtle4()
        self.motor_turtle5()
        self.motor_turtle6()

    def call_spawn_service(self, name, x, y):
        client = self.create_client(Spawn, "/spawn")
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("Esperando servicio /spawn...")

        request = Spawn.Request()
        request.name = name
        request.x = x
        request.y = y
        request.theta = 0.0

        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            self.get_logger().info(f"Tortuga '{name}' creada con éxito.")
        else:
            self.get_logger().error(f"Error al crear tortuga '{name}': {future.exception()}")

    def motor_turtle1(self):
        i = 0
        if self.turtle_state[i] == 0:
            if self.service_flag[i] == 0:
                self.turtle[i].call_set_pen_service(0, 0, 0, 10, 255)
                self.service_flag[i] = 1
            elif self.turtle[i].future.done():
                if self.turtle[i].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[i] = 0
                    self.turtle_state[i] +=1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[i] = -1
                    self.service_flag[i] += 1

        elif self.turtle_state[i] == 1:
            pub = Twist()
            pub.linear.x = 0.0
            pub.linear.y = 1.0
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.y >= 6.28:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] += 1

        if self.turtle_state[i] == 2:
            if self.service_flag[i] == 0:
                self.turtle[i].call_set_pen_service(0, 0, 0, 6, 0)
                self.service_flag[i] = 1
            elif self.turtle[i].future.done():
                if self.turtle[i].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[i] = 0
                    self.turtle_state[i] +=1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[i] = -1
                    self.service_flag[i] += 1

        elif self.turtle_state[i] == 3:
            pub = Twist()
            pub.linear.x = 0.0
            pub.linear.y = -1.0
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.y <= 0.0:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 4:

            msg = Twist()
            msg.linear.y = 1.0
            msg.linear.x = 1.5
            self.turtle[i].sends_velocity_command(msg)

            pose = self.turtle[i].get_pose()

            if pose.x >= 8.0:
                msg.linear.y = 0.0
                msg.linear.x = 0.0
                self.turtle[i].sends_velocity_command(msg)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 5:
            msg = Twist()
            msg.linear.y = 1.0
            msg.linear.x = 0.0
            self.turtle[i].sends_velocity_command(msg)

            pose = self.turtle[i].get_pose()

            if pose.y >= 8.0:
                msg.linear.y = 0.0
                msg.linear.x = 0.0
                self.turtle[i].sends_velocity_command(msg)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 6:
            msg = Twist()
            msg.linear.y = -1.0
            msg.linear.x = -1.5
            self.turtle[i].sends_velocity_command(msg)

            pose = self.turtle[i].get_pose()

            if pose.x <= 6.1:
                msg.linear.y = 0.0
                msg.linear.x = 0.0
                self.turtle[i].sends_velocity_command(msg)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 7:
            msg = Twist()
            msg.linear.y = -0.1
            msg.linear.x = -0.15
            self.turtle[i].sends_velocity_command(msg)

            pose = self.turtle[i].get_pose()

            if pose.x <= 5.6 and pose.y <= 6.4:
                msg.linear.y = 0.0
                msg.linear.x = 0.0
                self.turtle[i].sends_velocity_command(msg)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 8:
            if self.service_flag[i] == 0:
                self.turtle[i].call_kill_service()
                self.service_flag[i] = 1
            elif self.turtle[i].future.done():
                if self.turtle[i].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[i] = 0
                    self.turtle_state[i] +=1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[i] = -1
                    self.service_flag[i] += 1


    def motor_turtle2(self):
        i = 1
        if self.turtle_state[i] == 0:
            if self.service_flag[i] == 0:
                self.turtle[i].call_set_pen_service(150, 150, 0, 10, 0)
                self.service_flag[i] = 1
            elif self.turtle[i].future.done():
                if self.turtle[i].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[i] = 0
                    self.turtle_state[i] +=1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[i] += 1
                    self.service_flag[i] += 1

        elif self.turtle_state[i] == 1:
            if self.service_flag[i] == 0:
                pub = Twist()
                pub.linear.x = 1.0
                pub.angular.z = 1.0
                self.turtle[i].sends_velocity_command(pub)
                pose = self.turtle[i].get_pose()

                if pose.theta >= 6.2:
                    pub.linear.x = 0.0
                    pub.angular.z = 0.0
                    self.turtle_state[i] += 1

    def motor_turtle3(self):
        i = 2
        if self.turtle_state[i] == 0:
            if self.service_flag[i] == 0:
                self.turtle[i].call_set_pen_service(0, 0, 0, 6, 0)
                self.service_flag[i] = 1
            elif self.turtle[i].future.done():
                if self.turtle[i].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[i] = 0
                    self.turtle_state[i] +=1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[i] = -1
                    self.service_flag[i] += 1

        elif self.turtle_state[i] == 1:
            pub = Twist()
            pub.linear.x = -1.0
            pub.linear.y = 0.5
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.x <= 2.75:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 2:
            pub = Twist()
            pub.linear.x = 0.0
            pub.linear.y = -1.0
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.y <= 1.5:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 3:

            msg = Twist()
            msg.linear.y = -0.5
            msg.linear.x = 1.0
            self.turtle[i].sends_velocity_command(msg)

            pose = self.turtle[i].get_pose()

            if pose.y <= 0.0:
                msg.linear.y = 0.0
                msg.linear.x = 0.0
                self.turtle[i].sends_velocity_command(msg)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 4:
            if self.service_flag[i] == 0:
                self.turtle[i].call_kill_service()
                self.service_flag[i] = 1
            elif self.turtle[i].future.done():
                if self.turtle[i].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[i] = 0
                    self.turtle_state[i] +=1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[i] = -1
                    self.service_flag[i] += 1
        elif self.turtle_state[i] == 5:
            if self.service_flag[1] == 0:
                self.turtle[1].call_kill_service()
                self.service_flag[1] = 1
            elif self.turtle[1].future.done():
                if self.turtle[1].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[1] = 1
                    self.turtle_state[1] += 1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[1] = -1
                    self.service_flag[1] += 1

    def motor_turtle4(self):
        i = 3
        if self.turtle_state[i] == 0:
            if self.service_flag[i] == 0:
                self.turtle[i].call_set_pen_service(0, 0, 0, 6, 0)
                self.service_flag[i] = 1
            elif self.turtle[i].future.done():
                if self.turtle[i].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[i] = 0
                    self.turtle_state[i] +=1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[i] = -1
                    self.service_flag[i] += 1

        elif self.turtle_state[i] == 1:
            pub = Twist()
            pub.linear.x = -1.0
            pub.linear.y = 0.5
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.x <= 5.2:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 2:
            pub = Twist()
            pub.linear.x = -1.5
            pub.linear.y = -1.0
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.x <= 2.75:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 3:
            if self.service_flag[i] == 0:
                self.turtle[i].call_kill_service()
                self.service_flag[i] = 1
            elif self.turtle[i].future.done():
                if self.turtle[i].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[i] = 0
                    self.turtle_state[i] +=1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[i] = -1
                    self.service_flag[i] += 1


    def motor_turtle5(self):
        i = 4
        if self.turtle_state[i] == 0:
            if self.service_flag[i] == 0:
                self.turtle[i].call_set_pen_service(0, 0, 255, 2, 0)
                self.service_flag[i] = 1
            elif self.turtle[i].future.done():
                if self.turtle[i].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[i] = 0
                    self.turtle_state[i] +=1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[i] = -1
                    self.service_flag[i] += 1

        elif self.turtle_state[i] == 1:
            pub = Twist()
            pub.linear.x = 1.5
            pub.linear.y = 1.0
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.x >= 7.7:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.previous = pose.y
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 2:
            pub = Twist()
            pub.linear.x = 0.0
            pub.linear.y = -0.5
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.y - self.final_y <= 0.0:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] = 5
            elif self.previous - pose.y >= 0.5:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 3:
            pub = Twist()
            pub.linear.x = -1.5
            pub.linear.y = -1.0
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.x <= 6.0:

                self.previous = pose.y
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 4:
            pub = Twist()
            pub.linear.x = 0.0
            pub.linear.y = -0.5
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.y - self.final_y <= 0.0:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] = 5
            elif self.previous - pose.y >= 0.5:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.previous = pose.y
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] = 1

        elif self.turtle_state[i] == 5:
            if self.service_flag[i] == 0:
                self.turtle[i].call_kill_service()
                self.service_flag[i] = 1
            elif self.turtle[i].future.done():
                if self.turtle[i].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[i] = 0
                    self.turtle_state[i] +=1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[i] = -1
                    self.service_flag[i] += 1

    def motor_turtle6(self):
        i = 5
        if self.turtle_state[i] == 0:
            if self.service_flag[i] == 0:
                self.turtle[i].call_set_pen_service(0, 0, 255, 2, 0)
                self.service_flag[i] = 1
            elif self.turtle[i].future.done():
                if self.turtle[i].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[i] = 0
                    self.turtle_state[i] +=1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[i] = -1
                    self.service_flag[i] += 1

        elif self.turtle_state[i] == 1:
            pub = Twist()
            pub.linear.x = -1.0
            pub.linear.y = 0.5
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.x <= 3.2:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.previous2 = pose.y
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 2:
            pub = Twist()
            pub.linear.x = 0.0
            pub.linear.y = -0.5
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.y - self.final_y <= 0.0:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] = 5
            elif self.previous2 - pose.y >= 0.5:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 3:
            pub = Twist()
            pub.linear.x = 1.0
            pub.linear.y = -0.5
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.x >= 5.0:

                self.previous2 = pose.y
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] += 1

        elif self.turtle_state[i] == 4:
            pub = Twist()
            pub.linear.x = 0.0
            pub.linear.y = -0.5
            self.turtle[i].sends_velocity_command(pub)
            pose = self.turtle[i].get_pose()
            if pose.y - self.final_y <= 0.0:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] = 5
            elif self.previous2 - pose.y >= 0.5:
                pub.linear.x = 0.0
                pub.linear.y = 0.0
                self.previous2 = pose.y
                self.turtle[i].sends_velocity_command(pub)
                self.turtle_state[i] = 1

        elif self.turtle_state[i] == 5:
            if self.service_flag[i] == 0:
                self.turtle[i].call_kill_service()
                self.service_flag[i] = 1
            elif self.turtle[i].future.done():
                if self.turtle[i].future.exception() is None:
                    self.get_logger().info("SetPen completado correctamente.")
                    self.service_flag[i] = 0
                    self.turtle_state[i] +=1
                else:
                    self.get_logger().error(f"Error en SetPen: {self.turtle[i].future.exception()}")
                    self.turtle_state[i] = -1
                    self.service_flag[i] += 1

def main(args = None):
    rclpy.init(args = args)
    node = TurtleMaster()
    rclpy.spin(node)
    rclpy.shutdown()