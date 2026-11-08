# AGENTS.md

## Project: KRAI 2027 Autonomous Robot

This repository contains the ROS 2 software for an autonomous KRAI 2027
robot.

The project is being developed on:

- Raspberry Pi 5
- Ubuntu 24.04
- ROS 2 Jazzy
- Python
- ESP32-WROOM-32
- 4 × BTS7960 motor drivers
- 4 × 6 V DC motors
- 4 mecanum wheels
- LiDAR
- USB serial communication between Raspberry Pi and ESP32

The robot is intended to eventually perform autonomous navigation,
object detection/pickup, and object placement.

---

# 1. IMPORTANT DEVELOPMENT RULES

## 1.1 Do not redesign the project without permission

Do NOT:

- rename the ROS package
- rename existing nodes
- create a new package unnecessarily
- delete working files
- replace the current architecture
- introduce a large framework
- rewrite working code just for style
- add Gazebo/simulation code unless explicitly requested
- replace Python with another language unless explicitly requested

Before making architectural changes, explain why the change is necessary
and ask for confirmation.

The current architecture is intentionally simple because the developer is
still learning ROS 2.

---

# 2. CURRENT ROS 2 ARCHITECTURE

Current data flow:

LiDAR
  ↓
pembaca_lidar
  ↓
/data_lidar
  ↓
navigasi_robot
  ↓
/perintah_navigasi
  ↓
node_motor
  ↓
USB Serial
  ↓
ESP32
  ↓
BTS7960
  ↓
DC Motors
  ↓
Mecanum Wheels

The three main ROS 2 nodes are:

1. pembaca_lidar
2. navigasi_robot
3. node_motor

Keep each node responsible for one main job.

---

# 3. CURRENT PACKAGE

ROS 2 package name:

ros2

Expected executables:

- pembaca_lidar
- navigasi_robot
- node_motor

Do not change these executable names unless explicitly requested.

---

# 4. CURRENT ACTIVE FILES

The active ROS Python files are:

ros2/
├── pembaca_lidar.py
├── navigasi_robot.py
└── node_motor.py

Other old learning files may exist in an archive.

Do not automatically delete old files.

---

# 5. CURRENT WORKSPACE

The project is currently being developed on a Raspberry Pi.

Current workspace:

~/learningros2/learning-ros2

Do not assume the old WSL workspace is still being used.

The old workspace locations such as ~/ros2_ws are historical and should
not be used unless the developer explicitly provides a new path.

Before running destructive or workspace-wide commands, inspect the current
directory first.

---

# 6. NODE: pembaca_lidar

File:

ros2/pembaca_lidar.py

Purpose:

Read LaserScan data and convert raw LiDAR measurements into simple sector
measurements.

Subscribed topic:

/scan

Message:

sensor_msgs/msg/LaserScan

Published topic:

/data_lidar

Message:

std_msgs/msg/Float32MultiArray

Data format:

[
    depan,
    kiri,
    kanan
]

Current sectors:

- depan: 0° ±15°
- kiri: +90° ±15°
- kanan: -90° ±15°

The node searches for valid LiDAR measurements inside each sector and uses
the minimum valid distance.

Invalid or unavailable measurements are represented by NaN.

Do not change the message format without explicit approval.

---

# 7. NODE: navigasi_robot

File:

ros2/navigasi_robot.py

Purpose:

Convert LiDAR information into high-level movement commands.

Subscribed topic:

/data_lidar

Message:

std_msgs/msg/Float32MultiArray

Published topic:

/perintah_navigasi

Message:

std_msgs/msg/String

Current commands:

- MAJU
- MUNDUR
- GESER_KIRI
- GESER_KANAN
- BELOK_KIRI
- BELOK_KANAN
- BERHENTI

Current safety distance:

0.5 meters

Basic behavior:

If the front is clear:

    MAJU

If front is blocked and the left side is safer:

    GESER_KIRI

If front is blocked and the right side is safer:

    GESER_KANAN

Otherwise:

    BERHENTI

The navigation node publishes commands continuously because the motor node
uses a communication watchdog.

---

# 8. LIDAR SAFETY

The navigation system must have a LiDAR communication timeout.

If LiDAR data stops arriving for approximately 0.5 seconds:

    BERHENTI

must be published.

The node should log a warning similar to:

"Data LiDAR terputus! Robot dihentikan."

Do not remove this safety mechanism unless explicitly requested.

---

# 9. NODE: node_motor

File:

ros2/node_motor.py

Purpose:

Receive high-level navigation commands and convert them into mecanum wheel
commands.

Subscribed topic:

/perintah_navigasi

Message:

std_msgs/msg/String

Serial device:

/dev/ttyUSB0

Baud rate:

115200

Communication:

Raspberry Pi → USB Serial → ESP32

---

# 10. MECANUM CONTROL

Current function:

gerak_mecanum(vx, vy, omega)

Current equations:

FL = vx - vy - omega
FR = vx + vy + omega
RL = vx + vy - omega
RR = vx - vy + omega

The implementation normalizes wheel values so the maximum PWM does not
exceed the configured limit.

Current PWM limit:

150

Current command mapping:

MAJU:
    gerak_mecanum(150, 0, 0)

MUNDUR:
    gerak_mecanum(-150, 0, 0)

GESER_KANAN:
    gerak_mecanum(0, 150, 0)

GESER_KIRI:
    gerak_mecanum(0, -150, 0)

BELOK_KIRI:
    gerak_mecanum(0, 0, 150)

BELOK_KANAN:
    gerak_mecanum(0, 0, -150)

BERHENTI:
    0, 0, 0, 0

Physical wheel direction may require sign calibration because motor polarity
and wheel installation determine the actual direction.

Do not assume the current signs are universally correct.

---

# 11. MOTOR SAFETY WATCHDOG

node_motor has a communication watchdog.

If no valid navigation command is received for approximately 0.5 seconds:

    send 0,0,0,0

and stop the motors.

Do not remove or weaken this watchdog.

---

# 12. ESP32

ESP32 firmware receives commands in this format:

FL,FR,RL,RR

Example:

150,150,150,150

Each value is signed PWM:

-255 ... +255

Positive:

RPWM active

Negative:

LPWM active

Zero:

motor stopped

ESP32 also has its own approximately 500 ms watchdog.

Therefore the safety chain is:

LiDAR timeout
    ↓
navigation stop
    ↓
ROS command timeout
    ↓
ESP32 watchdog
    ↓
motors stop

Do not remove these safety layers.

---

# 13. ESP32 GPIO MAPPING

ESP32-WROOM-32 motor mapping:

FL:
    RPWM = 25
    LPWM = 26
    ENABLE = 13

FR:
    RPWM = 27
    LPWM = 14
    ENABLE = 21

RL:
    RPWM = 32
    LPWM = 33
    ENABLE = 23

RR:
    RPWM = 18
    LPWM = 19
    ENABLE = 22

GPIO 12 is intentionally avoided because of boot/strap considerations.

Do not change GPIO assignments unless explicitly requested.

---

# 14. HARDWARE SAFETY

This is a real physical robot.

Before testing motor movement:

- keep wheels lifted from the floor during initial tests
- have a physical motor power cutoff/emergency stop available
- never power motors directly from ESP32 5V
- use the appropriate external motor supply
- maintain a common ground between the ESP32 control system and motor drivers
- never assume the software stop alone is sufficient for an emergency

Do not automatically execute commands that could unexpectedly move the robot.

When proposing movement tests, explicitly mention physical safety when
appropriate.

---

# 15. NO ENCODERS YET

The robot currently does not have wheel encoders.

Therefore:

- do not claim accurate wheel odometry
- do not implement precise closed-loop wheel speed control
- do not claim precise distance traveled from motor PWM alone
- do not assume exact robot position

Future encoder integration may be added later.

---

# 16. GAZEBO

Gazebo is NOT currently part of the active development workflow.

Do not add Gazebo-related files, launch files, bridges, worlds, or simulation
dependencies unless explicitly requested.

Current priority is real robot programming.

---

# 17. CODING STYLE

The developer is still learning Python and ROS 2.

Prefer:

- simple Python
- clear variable names
- explicit code
- small functions
- comments explaining important logic
- one responsibility per function
- one responsibility per node

Avoid unnecessary:

- decorators
- advanced Python features
- metaclasses
- complex inheritance
- asynchronous patterns unless necessary
- excessive abstraction
- unnecessary external libraries

Do not optimize code prematurely.

Readable code is more important than clever code.

---

# 18. ROS 2 LEARNING STYLE

When modifying code, explain:

1. what changed
2. why it changed
3. where it changed
4. how to test it

The developer prefers understanding the logic rather than blindly copying
code.

When a change touches multiple places, provide the complete file instead of
forcing the developer to patch many small fragments.

---

# 19. TESTING WORKFLOW

Prefer small incremental tests.

Do not make many unrelated changes at once.

Typical build:

cd ~/learningros2/learning-ros2
colcon build --packages-select ros2
source install/setup.bash

Typical nodes:

ros2 run ros2 pembaca_lidar

ros2 run ros2 navigasi_robot

ros2 run ros2 node_motor

Useful topic inspection:

ros2 topic echo /data_lidar

ros2 topic echo /perintah_navigasi

Before motor tests, wheels should be lifted from the floor.

---

# 20. ERROR HANDLING

When an error occurs:

1. read the exact error
2. identify which node/file caused it
3. explain the cause
4. make the smallest necessary fix
5. rebuild only what is necessary
6. test again

Do not rewrite the entire project because of a small error.

Do not hide errors with broad exception handling.

---

# 21. DO NOT BREAK WORKING CODE

Before editing a file:

- inspect the current file
- understand how it connects to other nodes
- preserve working behavior
- modify only what is necessary

Do not replace working code with a completely different implementation
unless there is a clear reason.

If the current implementation works, prefer incremental improvement.

---

# 22. COMMUNICATION STYLE

The developer prefers Indonesian explanations.

When communicating with the developer:

- use Indonesian
- explain step-by-step
- keep instructions concise
- avoid giving too many steps at once
- preferably give no more than 3 immediate actions
- wait for the test result before moving to the next stage

Do not overwhelm the developer with a complete robotics architecture when
only one small problem is being solved.

---

# 23. CURRENT DEVELOPMENT PRIORITY

Development should proceed approximately in this order:

1. LiDAR reading
2. LiDAR sector processing
3. obstacle avoidance
4. navigation safety
5. motor command interface
6. mecanum movement
7. encoder integration
8. odometry
9. camera / YOLO
10. object approach
11. arm/gripper control
12. object pickup
13. object placement
14. complete autonomous task behavior

Do not jump several stages ahead unless explicitly requested.

---

# 24. ARCHITECTURE PRINCIPLE

Keep the separation:

LiDAR node
    =
sensor processing

Navigation node
    =
decision making

Motor node
    =
motor control

ESP32
    =
low-level motor execution and safety watchdog

Do not combine all responsibilities into one large ROS node.

---

# 25. IMPORTANT RULE FOR AGENT ACTIONS

Before modifying multiple files:

- explain which files will change
- explain why
- make sure the change is necessary

Before deleting files:

- ask for explicit confirmation

Before changing hardware mappings:

- ask for explicit confirmation

Before changing ROS topics/messages:

- ask for explicit confirmation

Before introducing new dependencies:

- explain why the dependency is needed

Before running commands that may move the robot:

- warn the developer and require the physical safety setup

The goal is a stable, understandable, incremental KRAI robot software stack.