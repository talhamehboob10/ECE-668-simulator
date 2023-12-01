import os
import tom_architecture
import tom_simulator


if __name__ == "__main__":
    if os.path.exists("simulation_log.txt"):
        os.remove("simulation_log.txt")
    processor = tom_architecture.TomasuloProcessor()
    simulator = tom_simulator.TomasuloSimulator(processor)
    simulator.run_simulation()

