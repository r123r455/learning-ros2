
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32



class PublisherJarak(Node):
    def __init__(self):
        super().__init__('publisher_jarak')

        self.jarak = 1.0
        self.perubahan = -0.1
        

        self.publisher = self.create_publisher(
            Float32,
            '/jarak',
            10
        )

        self.timer = self.create_timer(
            0.5,
            self.kirim_jarak
        )


    def kirim_jarak(self):
        pesan = Float32()
        pesan.data = self.jarak

        self.publisher.publish(pesan)

        self.get_logger().info(
            f'Jarak: {pesan.data:.2f} m'
        )
        self.jarak += self.perubahan

        if self.jarak <= 0.1:
            self.perubahan = 0.1
        elif self.jarak >= 1.0:
            self.perubahan = -0.1


def main(args=None):
    rclpy.init(args=args)
    node = PublisherJarak()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
