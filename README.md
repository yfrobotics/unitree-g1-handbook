# Unitree G1 Handbook

Everything about Unitree G1 for beginners. It could be both exciting and frustrating to use G1 as a first-time user. I write this handbook while myself is exploring the robot. This handbook will focus on the G1 EDU version, and in particular target for someone who do research and/or development with G1.

## Getting Started
### Unboxing G1

The first step is to unbox the robot. You need two people to do that as the robot is very heavy (35kg+) to get outside from the box. Make sure you assemble the crane first if it comes with the robot. If not, you may lay the robot down on the ground with its face up. Boot and start the robot following the manual that ships with G1. You can test some basic pre-built movements with the remote controller, and meanwhile record some very cool videos to show off to your friends.

## Connect to the robot

Now it is time to do some real development. You may find the [official development guide](https://support.unitree.com/home/en/G1_developer) useful but it somehow was made in a way that assumes you are already familiar with the robot, but to most of us this is likely to be our first time playing with a humanoid robot like G1. Personally I didn't understand it when I first read it.

There are two computers on G1:
- **a high-level computer** (using a Jetson Orin)
- **a low-level computer** (this is the motion controller)

Basically what you should do is to connect your PC to the high-level computer. You can directly connect the robot to your PC:
```
G1 <--(wired)--> PC
```

or with a router, which is easier for Unitree to access the Internet:
```
G1 <--(wired)--> Router <--(wired or wireless)--> PC
```

The IP address of G1 is `192.168.123.164`, you should make sure you are within the subdomain (`192.168.123.x`) of the robot. To test the connection, ping the robot `ping 192.168.123.164` with your PC/laptop. You should then be ready to connect to the robot with ssh:
```
ssh unitree@192.168.123.164`
``` 
when promoted, the default password is `123`.

## Download and compile the SDK

The robot is often shipped with the SDK, at least this is for my case. You can check with a `ls` within the home folder. If the SDK is missing, you should download it from the [official GitHub repo](https://github.com/unitreerobotics/unitree_sdk2). 

*(Work in progress)*
