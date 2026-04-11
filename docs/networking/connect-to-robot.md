# Connect to the Robot

You may find the [official development guide](https://support.unitree.com/home/en/G1_developer) useful but it somehow was made in a way that assumes you are already familiar with the robot, but to most of us this is likely to be our first time playing with a humanoid robot like G1.

## Computers on G1

There are two computers on G1:

- **A high-level computer** (using a Jetson Orin)
- **A low-level computer** (this is the motion controller)

Basically what you should do is to connect your PC to the high-level computer.

## Connection Options

You can directly connect the robot to your PC:

```
G1 <--(wired)--> PC
```

Or with a router, which is easier for G1 to access the Internet:

```
G1 <--(wired)--> Router <--(wired or wireless)--> PC
```

## Network Configuration

The IP address of G1 is `192.168.123.164`. You should make sure you are within the subdomain (`192.168.123.x`) of the robot.

To test the connection, ping the robot:

```bash
ping 192.168.123.164
```

You should then be ready to connect to the robot with SSH:

```bash
ssh unitree@192.168.123.164
```

When prompted, the default password is `123`.
