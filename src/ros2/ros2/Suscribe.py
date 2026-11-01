"""ROS 2 subscriber node for the /topic string topic."""

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)

from std_msgs.msg import String


class Suscribe(Node):
    """Subscribe to string messages and log their contents."""

    def __init__(self):
        """Initialize the subscriber and its QoS profile."""
        super().__init__('suscribe')

        qos_self = QoSProfile(
            reliability=ReliabilityPolicy.BEST_AVAILABLE,
            history=HistoryPolicy.KEEP_LAST,
            durability=DurabilityPolicy.VOLATILE,
            depth=5,
        )

        self.subscription = self.create_subscription(
            String,
            '/topic',
            self.callback,
            qos_self,
        )

    def callback(self, msg):
        """Log the content of a received string message."""
        self.get_logger().info(
            f'data: {msg.data}'
        )


def main(args=None):
    """Run the subscriber node."""
    rclpy.init(args=args)
    node = Suscribe()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
