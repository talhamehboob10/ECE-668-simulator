import tom_architecture as ta  # Assuming the previous TomasuloProcessor code is in "tom_architecture.py"

class TomasuloSimulator:
    def __init__(self, processor):
        self.processor = ta.TomasuloProcessor()
        self.instruction_count = 0
        self.instructions = self.read_instructions("instructions.txt")
        self.global_clock_cycle = 1
        self.current_instruction = 0
        self.rs_name = None
        self.functional_completion = {}

    # Outputs a list of the instructions
    def read_instructions(self, filename):
        with open(filename, 'r') as file:
            self.instructions = file.readlines()
            self.instruction_count += 1
        return self.instructions

    # The main Tomasulo simulator
    def run_simulation(self):
        vj, vk, destination = None, None, None
        while True:
            # Head of next log entry
            log_entry = f"#--------------------------------------------------------#\n"
            log_entry += f"# Clock Cycle: {self.global_clock_cycle}\n"

            # Parse the instruction and issue it if we have not yet done so
            if self.current_instruction < self.instruction_count:
                # Get the parts of the instruction that we need
                parts = self.instructions[self.current_instruction].split()
                op = parts[0].strip(',')
                destination = parts[1].strip(',')
                vj = parts[2].strip(',')
                vk = parts[3].strip(',')
                # Issue stage, get the name of the reservation station
                self.rs_name = self.processor.issue(op, vj, vk)
                log_entry += f"Issued: {self.rs_name}\n"

            # Get the functional unit name for execution
            executing_fu = self.processor.execute()

            # Add this instruction to the execution dictionary and set the value for its completion time
            if executing_fu is not None:
                log_entry += f"Now Executing: {executing_fu} instruction\n"
                self.functional_completion[executing_fu] = getattr(self.processor, f"{executing_fu.lower()}_fu").remaining_cycles + self.global_clock_cycle

            # Check the dictionary for any execution completions
            for instruction in list(self.functional_completion.keys()):
                if self.functional_completion[instruction] == self.global_clock_cycle:
                    result = f"{vj}+{vk}"  # Replace with the actual result of the operation
                    self.processor.write_result(result)
                    log_entry += f"Execution done for: {instruction} instruction\n"
                    log_entry += f"Write Back: {result} to {destination}\n"
                    # Instruction done executing, remove from list
                    self.functional_completion.pop(instruction)
                else:
                    log_entry += f"Still Executing: {instruction} instruction\n"

            # Increment the clock cycle and instruction
            self.global_clock_cycle += 1
            self.current_instruction += 1

            # Write to the log
            with open("simulation_log.txt", "a") as file:
                log_entry += "\n"
                file.write(log_entry)

            # Done?
            if len(self.functional_completion) == 0 and self.current_instruction >= self.instruction_count:
                break
