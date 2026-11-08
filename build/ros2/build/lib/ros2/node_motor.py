import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial
import time


class NodeMotor(Node):

    def __init__(self):
        super().__init__('node_motor')

        # ==============================
        # KONEKSI SERIAL
        # ==============================

        self.serial_port = '/dev/ttyUSB0'
        self.baudrate = 115200

        try:
            self.esp32 = serial.Serial(
                self.serial_port,
                self.baudrate,
                timeout=1
            )

            time.sleep(2)

            self.get_logger().info(
                'ESP32 berhasil terhubung'
            )

        except serial.SerialException as e:

            self.esp32 = None

            self.get_logger().error(
                f'Gagal membuka ESP32: {e}'
            )

        # ==============================
        # SUBSCRIBER
        # ==============================

        self.subscription = self.create_subscription(
            String,
            '/perintah_navigasi',
            self.callback_perintah,
            10
        )

        # ==============================
        # WATCHDOG
        # ==============================

        self.waktu_perintah = None
        self.status_timeout = False

        self.timer = self.create_timer(
            0.1,
            self.periksa_komunikasi
        )

        self.get_logger().info(
            'Node Motor siap'
        )

    # ==================================
    # MENGIRIM DATA KE ESP32
    # ==================================

    def kirim_motor(self, fl, fr, rl, rr):

        data = f'{fl},{fr},{rl},{rr}\n'

        if self.esp32 is not None:

            try:
                self.esp32.write(
                    data.encode()
                )

                self.get_logger().info(
                    f'ESP32 <- {data.strip()}'
                )

            except serial.SerialException as e:

                self.get_logger().error(
                    f'Gagal mengirim ke ESP32: {e}'
                )

    # ==================================
    # MENERIMA PERINTAH ROS
    # ==================================
    def gerak_mecanum(self, vx, vy, omega):
        # Menghitung kecepatan setiap roda
        fl = vx - vy - omega
        fr = vx + vy + omega
        rl = vx + vy - omega
        rr = vx - vy + omega

        # Membatasi kecepatan maksimum PWM
        kecepatan = [fl, fr, rl, rr]

        nilai_maksimum = max(
            abs(nilai) for nilai in kecepatan
        )

        batas_pwm = 150

        if nilai_maksimum > batas_pwm:
            faktor = batas_pwm / nilai_maksimum
            kecepatan = [
                nilai * faktor for nilai in kecepatan
            ]

        # Mengubah hasil menjadi integer
        fl, fr, rl, rr = [
            int(round(nilai)) for nilai in kecepatan
        ]

        # Mengirim ke ESP32
        self.kirim_motor(fl, fr, rl, rr)

    def callback_perintah(self, msg):
        perintah = msg.data

        if perintah == 'MAJU':
            self.gerak_mecanum(150, 0, 0)

        elif perintah == 'MUNDUR':
            self.gerak_mecanum(-150, 0, 0)

        elif perintah == 'GESER_KANAN':
            self.gerak_mecanum(0, 150, 0)

        elif perintah == 'GESER_KIRI':
            self.gerak_mecanum(0, -150, 0)

        elif perintah == 'BELOK_KIRI':
            self.gerak_mecanum(0, 0, 150)

        elif perintah == 'BELOK_KANAN':
            self.gerak_mecanum(0, 0, -150)

        elif perintah == 'BERHENTI':
            self.kirim_motor(0, 0, 0, 0)

        else:
            self.get_logger().warning(
                f'Perintah tidak dikenal: {perintah}'
            )
            return

        self.waktu_perintah = time.monotonic()
        self.status_timeout = False

        # ==================================
        # WATCHDOG
        # ==================================

    def periksa_komunikasi(self):

        if self.waktu_perintah is None:
            return

        selisih = (
            time.monotonic()
            - self.waktu_perintah
        )

        if selisih > 0.5:

            if not self.status_timeout:

                self.get_logger().warning(
                    'Perintah ROS terputus! '
                    'Motor dihentikan.'
                )

                self.kirim_motor(
                    0, 0, 0, 0
                )

                self.status_timeout = True

    # ==================================
    # SHUTDOWN
    # ==================================

    def destroy_node(self):

        if self.esp32 is not None:

            try:
                self.esp32.write(
                    b'0,0,0,0\n'
                )

                self.esp32.close()

            except Exception:
                pass

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = NodeMotor()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()