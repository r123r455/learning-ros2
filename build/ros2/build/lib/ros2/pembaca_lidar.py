
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String
import time


class KontrolRobot(Node):
    def __init__(self):
        super().__init__('kontrol_robot')

        self.jarak = None
        self.waktu_data_terakhir = None

        # Menerima data jarak
        self.subscription = self.create_subscription(
            Float32,
            '/jarak',
            self.callback_jarak,
            10
        )

        # Mengirim perintah ke node motor
        self.publisher_motor = self.create_publisher(
            String,
            '/perintah_motor',
            10
        )

        # Memeriksa kondisi setiap 0,1 detik
        self.timer = self.create_timer(
            0.1,
            self.cek_rintangan
        )
        

    def callback_jarak(self, msg):
        self.jarak = msg.data
        self.waktu_data_terakhir = time.monotonic()

    def cek_rintangan(self):
        pesan = String()

        # Periksa apakah data pernah diterima
        if self.waktu_data_terakhir is None :
            pesan.data = 'BERHENTI'

        else:
            # Hitung umur data sensor
            waktu_sekarang = time.monotonic()

            selisih_waktu = (
                waktu_sekarang - self.waktu_data_terakhir
            )

            # Periksa apakah data sudah kedaluwarsa
            if selisih_waktu > 1.5:
                pesan.data = 'BERHENTI'

            # Data masih baru, periksa jarak
            elif self.jarak < 0.5:
                pesan.data = 'BERHENTI'

            else:
                pesan.data = 'MAJU'

        # Kirim perintah ke node motor
        self.publisher_motor.publish(pesan)

        self.get_logger().info(
            f'Jarak: {self.jarak} | '
            f'Perintah: {pesan.data}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = KontrolRobot()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
