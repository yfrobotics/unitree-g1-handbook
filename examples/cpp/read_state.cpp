// Read-only G1 state monitor: no publisher and no mode switching.
#include <unitree/idl/hg/LowState_.hpp>
#include <unitree/robot/channel/channel_subscriber.hpp>
#include <chrono>
#include <cmath>
#include <iostream>
#include <mutex>
#include <thread>

int run(int argc, char** argv) {
  if (argc < 3 || argc > 4 || (argc == 4 && std::string(argv[3]) != "arrival" && std::string(argv[3]) != "tick")) {
    std::cerr << "Usage: read_state INTERFACE DOMAIN [arrival|tick] (slot 0, 10 s)\n";
    return 1;
  }
  int domain;
  try {
    size_t consumed;
    domain = std::stoi(argv[2], &consumed);
    if (consumed != std::string(argv[2]).size() || domain < 0 || domain > 232)
      throw std::invalid_argument("domain");
  } catch (const std::exception&) {
    std::cerr << "DOMAIN must be an integer in 0..232\n";
    return 1;
  }
  using Clock = std::chrono::steady_clock;
  using State = unitree_hg::msg::dds_::LowState_;
  std::mutex mutex;
  State latest;
  auto start = Clock::now(), arrival = start, progress = start;
  unsigned long count = 0;
  bool failed = false;
  unitree::robot::ChannelFactory::Instance()->Init(domain, argv[1]);
  unitree::robot::ChannelSubscriber<State> sub("rt/lowstate");
  sub.InitChannel([&](const void* data) {
    std::lock_guard<std::mutex> guard(mutex);
    const auto& state = *static_cast<const State*>(data);
    arrival = Clock::now();
    if (count == 0 || state.tick() != latest.tick()) progress = arrival;
    latest = state;
    ++count;
  }, 1);
  while (Clock::now() - start < std::chrono::seconds(10)) {
    std::this_thread::sleep_for(std::chrono::milliseconds(250));
    std::lock_guard<std::mutex> guard(mutex);
    auto now = Clock::now();
    const char* status = "OK";
    if (count == 0) status = now - start > std::chrono::seconds(1) ? "NO_MESSAGES" : "WAITING";
    else if (now - arrival > std::chrono::seconds(1)) status = "NO_MESSAGES";
    else if ((argc == 3 || std::string(argv[3]) == "tick") && now - progress > std::chrono::seconds(1)) status = "FROZEN_TICK";
    else {
      bool valid = std::isfinite(latest.motor_state()[0].q()) && std::isfinite(latest.motor_state()[0].dq());
      for (auto v : latest.imu_state().quaternion()) valid &= std::isfinite(v);
      if (!valid) status = "NONFINITE";
    }
    failed |= std::string(status) != "OK" && std::string(status) != "WAITING";
    std::cout << status << " received=" << count;
    if (count) {
      std::cout << " tick=" << latest.tick() << " q=" << latest.motor_state()[0].q()
                << " dq=" << latest.motor_state()[0].dq() << " quat_wxyz=";
      for (auto v : latest.imu_state().quaternion()) std::cout << v << ' ';
    }
    std::cout << std::endl;
  }
  sub.CloseChannel();
  return failed || count == 0 ? 2 : 0;
}

int main(int argc, char** argv) {
  try {
    return run(argc, argv);
  } catch (const std::exception& error) {
    std::cerr << "DDS initialization/monitor error: " << error.what() << '\n';
    return 3;
  }
}
