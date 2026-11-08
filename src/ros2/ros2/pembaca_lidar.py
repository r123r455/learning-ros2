import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32MultiArray
import math


class PembacaLidar(Node):

    def __init__(self):
        super().__init__('pembaca_lidar')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.callback_lidar,
            10
        )

        self.publisher_lidar = self.create_publisher(
            Float32MultiArray,
            '/data_lidar',
            10
        )

        self.get_logger().info('Pembaca LiDAR siap')

    def cari_jarak_sektor(self, msg, sudut_tujuan):

        jarak_valid = []
        setengah_sektor = math.radians(15)

        for indeks, jarak in enumerate(msg.ranges):

            sudut = (
                msg.angle_min
                + indeks * msg.angle_increment
            )

            selisih = math.atan2(
                math.sin(sudut - sudut_tujuan),
                math.cos(sudut - sudut_tujuan)
            )

            if abs(selisih) <= setengah_sektor:

                if (
                    math.isfinite(jarak)
                    and msg.range_min <= jarak <= msg.range_max
                ):
                    jarak_valid.append(jarak)

        if not jarak_valid:
            return float('nan')

        return min(jarak_valid)

    def callback_lidar(self, msg):

        depan = self.cari_jarak_sektor(
            msg, math.radians(0)
        )

        kiri = self.cari_jarak_sektor(
            msg, math.radians(90)
        )

        kanan = self.cari_jarak_sektor(
            msg, math.radians(-90)
        )

        pesan = Float32MultiArray()
        pesan.data = [depan, kiri, kanan]

        self.publisher_lidar.publish(pesan)

        self.get_logger().info(
            f'Depan: {depan:.2f} | '
            f'Kiri: {kiri:.2f} | '
            f'Kanan: {kanan:.2f}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = PembacaLidar()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()