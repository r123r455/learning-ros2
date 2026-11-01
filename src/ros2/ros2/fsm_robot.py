import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class RobotFSM(Node):

    def __init__(self):
        super().__init__('fsm_robot')

        # State awal robot
        self.state = 'IDLE'
        self.state_sebelumnya = self.state

        # Menerima event dari node lain
        self.subscription = self.create_subscription(
            String,
            '/robot_event',
            self.callback_event,
            10
        )

        # Mengirim state terbaru
        self.publisher_state = self.create_publisher(
            String,
            '/robot_state',
            10
        )

        self.get_logger().info(
            f'State awal robot: {self.state}'
        )

        self.publish_state()

    def callback_event(self, msg):
        event = msg.data

        # Memeriksa perpindahan state
        if self.state == 'IDLE':
            if event == 'START_COMMAND':
                self.state = 'SEARCH_OBJECT'

        elif self.state == 'SEARCH_OBJECT':
            if event == 'OBJECT_DETECTED':
                self.state = 'APPROACH_OBJECT'

        elif self.state == 'APPROACH_OBJECT':
            if event == 'OBJECT_REACHED':
                self.state = 'PICK_OBJECT'

        elif self.state == 'PICK_OBJECT':
            if event == 'OBJECT_PICKED':
                self.state = 'PLACE_OBJECT'

        elif self.state == 'PLACE_OBJECT':
            if event == 'OBJECT_PLACED':
                self.state = 'IDLE'

        # Tampilkan dan kirim state jika terjadi perubahan
        if self.state != self.state_sebelumnya:
            self.get_logger().info(
                f'Event: {event} | State: {self.state}'
            )
            self.publish_state()

        else:
            self.get_logger().info(
                f'Event: {event} | Tidak ada perubahan state'
            )

    def publish_state(self):
        pesan = String()
        pesan.data = self.state
        self.publisher_state.publish(pesan)


def main(args=None):
    rclpy.init(args=args)

    node = RobotFSM()


    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
