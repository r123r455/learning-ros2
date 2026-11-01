
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class NodeMotor(Node):
    def __init__(self):
        super().__init__('node_motor')

        self.subscription = self.create_subscription(
            String,
            '/perintah_motor',
            self.callback_perintah,
            10
        )

    def callback_perintah(self, msg):
        if msg.data == 'MAJU':
            self.get_logger().info('Motor diperintahkan MAJU')

        elif msg.data == 'BERHENTI':
            self.get_logger().info('Motor diperintahkan BERHENTI')

        else:
            self.get_logger().warning(
                f'Perintah tidak dikenal: {msg.data}'
            )


def main(args=None):
    rclpy.init(args=args)
    node = NodeMotor()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
