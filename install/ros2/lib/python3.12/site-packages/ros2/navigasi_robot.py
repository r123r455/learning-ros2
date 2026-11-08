import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, String
import math


class NavigasiRobot(Node):

    def __init__(self):
        super().__init__('navigasi_robot')

        self.batas_aman = 0.5
        self.perintah_sebelumnya = None

        self.subscription = self.create_subscription(
            Float32MultiArray,
            '/data_lidar',
            self.callback_lidar,
            10
        )

        self.publisher_perintah = self.create_publisher(
            String,
            '/perintah_navigasi',
            10
        )

        self.get_logger().info('Navigasi robot siap')

    def callback_lidar(self, msg):

        if len(msg.data) < 3:
            perintah = 'BERHENTI'

        else:
            depan, kiri, kanan = msg.data[:3]

            if not all(
                math.isfinite(x)
                for x in [depan, kiri, kanan]
            ):
                perintah = 'BERHENTI'

            elif depan > self.batas_aman:
                perintah = 'MAJU'

            elif (
                kiri > kanan
                and kiri > self.batas_aman
            ):
                perintah = 'GESER_KIRI'

            elif kanan > self.batas_aman:
                perintah = 'GESER_KANAN'

            else:
                perintah = 'BERHENTI'

        pesan = String()
        pesan.data = perintah

        self.publisher_perintah.publish(pesan)

        if perintah != self.perintah_sebelumnya:

            self.get_logger().info(
                f'Navigasi: {perintah}'
            )

            self.perintah_sebelumnya = perintah


def main(args=None):

    rclpy.init(args=args)

    node = NavigasiRobot()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()