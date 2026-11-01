import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ActionRobot(Node):

    def __init__(self):
        super().__init__('action_robot')

        # Menerima state dari FSM
        self.subscription = self.create_subscription(
            String,
            '/robot_state',
            self.callback_state,
            10
        )

        # Mengirim event kembali ke FSM
        self.publisher_event = self.create_publisher(
            String,
            '/robot_event',
            10
        )

        self.timer_aksi = None
        self.event_pending = None

        self.get_logger().info('Action Robot siap')

    def callback_state(self, msg):
        state = msg.data

        # IDLE tidak membutuhkan aksi
        if state == 'IDLE':
            self.get_logger().info('ROBOT: Menunggu perintah')
            return

        # Menentukan event yang dikirim setelah aksi selesai
        daftar_aksi = {
            'SEARCH_OBJECT': (
                'Mencari objek',
                'OBJECT_DETECTED'
            ),
            'APPROACH_OBJECT': (
                'Mendekati objek',
                'OBJECT_REACHED'
            ),
            'PICK_OBJECT': (
                'Mengambil objek',
                'OBJECT_PICKED'
            ),
            'PLACE_OBJECT': (
                'Meletakkan objek',
                'OBJECT_PLACED'
            )
        }

        if state not in daftar_aksi:
            self.get_logger().warning(
                f'State tidak dikenal: {state}'
            )
            return

        # Ambil nama aksi dan event penyelesaiannya
        nama_aksi, event = daftar_aksi[state]

        self.get_logger().info(
            f'ROBOT: {nama_aksi}'
        )

        self.event_pending = event

        # Simulasi waktu pengerjaan aksi selama 2 detik
        if self.timer_aksi is not None:
            self.timer_aksi.cancel()

        self.timer_aksi = self.create_timer(
            2.0,
            self.selesaikan_aksi
        )

    def selesaikan_aksi(self):
        # Hentikan timer agar event tidak dikirim berulang
        self.timer_aksi.cancel()
        self.timer_aksi = None

        # Kirim event penyelesaian ke FSM
        pesan = String()
        pesan.data = self.event_pending

        self.publisher_event.publish(pesan)

        self.get_logger().info(
            f'Aksi selesai, mengirim event: {pesan.data}'
        )

        self.event_pending = None


def main(args=None):
    rclpy.init(args=args)

    node = ActionRobot()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()