"""ROS 2 publisher node for the /topic string topic."""

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)

from std_msgs.msg import String


class Publisher(Node):
    """Publish string messages to the /topic topic."""

    def __init__(self):
        """Initialize the publisher and its timer."""
        super().__init__('publisher')

        qos_self = QoSProfile(
            reliability=ReliabilityPolicy.BEST_AVAILABLE,
            history=HistoryPolicy.KEEP_LAST,
            durability=DurabilityPolicy.VOLATILE,
            depth=5,
        )

        self.publisher = self.create_publisher(
            String,
            '/topic',
            qos_self,
        )

        self.timer = self.create_timer(0.5, self.timer_callback)

    def timer_callback(self):
        """Publish a string message."""
        msg = String()
        msg.data = 'robot'
        self.publisher.publish(msg)


def main(args=None):
    """Run the publisher node."""
    rclpy.init(args=args)
    node = Publisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
