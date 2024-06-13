#WELCOME TO TARIK AND DENIZ'S CAR MANUFACTURY SYSTEM SIMULATION
import simpy
import random
import pandas as pd
#helloo this is our second project 
# Set random seed for reproducibility
random.seed(42)
#here is the machine that is defined through the having processes and its features
class Machine:
    def __init__(self, env, name, process_time, fail_rate, repair_time):
        self.env = env
        self.name = name
        self.process_time = process_time
        self.fail_rate = fail_rate
        self.repair_time = repair_time
        self.machine = simpy.Resource(env, capacity=1)
        self.broken = False
#this definition is for the start and finish
    def process(self, part):
        with self.machine.request() as request:
            yield request
            print(f'{self.name} starts processing {part} at {self.env.now}')
            yield self.env.timeout(self.process_time)
            print(f'{self.name} finished processing {part} at {self.env.now}')

            if random.random() < self.fail_rate:
                self.broken = True
                print(f'{self.name} broke down at {self.env.now}')
                yield self.env.timeout(self.repair_time)
                self.broken = False
                print(f'{self.name} was repaired at {self.env.now}')
#this part is for whole manufacturing system features such as raw material, machining, assembly, quality and package
class ManufacturingSystem:
    def __init__(self, env):
        self.env = env
        self.raw_material_handling = Machine(env, 'Raw Material Handling', 5, 0.01, 10)
        self.machining = Machine(env, 'Machining', 10, 0.02, 15)
        self.assembly = Machine(env, 'Assembly', 7, 0.01, 5)
        self.quality_control = Machine(env, 'Quality Control', 3, 0.005, 3)
        self.packaging = Machine(env, 'Packaging', 4, 0.005, 2)
# here is the place all manufacturing system processes occur
    def process_part(self, part_id):
        yield self.env.process(self.raw_material_handling.process(part_id))
        yield self.env.process(self.machining.process(part_id))
        yield self.env.process(self.assembly.process(part_id))
        yield self.env.process(self.quality_control.process(part_id))
        yield self.env.process(self.packaging.process(part_id))
        print(f'Part {part_id} finished at {self.env.now}')
#this is to show how many times we did that process. Like a counter we called part
def part_generator(env, system, interarrival_time):
    part_id = 1
    while True:
        yield env.timeout(interarrival_time)
        env.process(system.process_part(part_id))
        part_id += 1
#here to run the simulation, there is simulation time and this simulation will be go untill it ends. 
def run_simulation(simulation_time, interarrival_time):
    env = simpy.Environment()
    system = ManufacturingSystem(env)
    env.process(part_generator(env, system, interarrival_time))
    env.run(until=simulation_time)

# we decided to have simulation of 100. Between arrivals, we decided 8. 
simulation_time = 100  # Total time to run the simulation
interarrival_time = 8  # Time between arrivals of new parts

#run the simulation 
run_simulation(simulation_time, interarrival_time)

#here is the experiments and analyzes that we decided.
def experiment_and_analyze(simulation_times, interarrival_times):
    results = []

    for sim_time in simulation_times:
        for interarrival in interarrival_times:
            env = simpy.Environment()
            system = ManufacturingSystem(env)
            env.process(part_generator(env, system, interarrival))
            env.run(until=sim_time)

            result = {
                'simulation_time': sim_time,
                'interarrival_time': interarrival,
                'completed_parts': system.completed_parts
            }
            results.append(result)

    df = pd.DataFrame(results)
    return df

# Example experiment parameters
simulation_times = [100, 200, 300]
interarrival_times = [6, 8, 10]
#resultss
results_df = experiment_and_analyze(simulation_times, interarrival_times)
print(results_df)
#this is the multi product machine class that works together
class MultiProductMachine(Machine):
    def __init__(self, env, name, process_times, fail_rate, repair_time):
        super().__init__(env, name, process_times[0], fail_rate, repair_time)
        self.process_times = process_times

    def process(self, part):
        product_type = part.split('_')[0]  # Assuming part names like '0_1', '1_2'
        process_time = self.process_times[int(product_type)]
        with self.machine.request() as request:
            yield request
            print(f'{self.name} starts processing {part} at {self.env.now}')
            yield self.env.timeout(process_time)
            print(f'{self.name} finished processing {part} at {self.env.now}')

            if random.random() < self.fail_rate:
                self.broken = True
                print(f'{self.name} broke down at {self.env.now}')
                yield self.env.timeout(self.repair_time)
                self.broken = False
                print(f'{self.name} was repaired at {self.env.now}')
#we define all multiple product manufacturing system tools, processes (all raw material, machining, assembly, quality and packaging.)
class MultiProductManufacturingSystem:
    def __init__(self, env):
        self.env = env
        self.raw_material_handling = MultiProductMachine(env, 'Raw Material Handling', [5, 6], 0.01, 10)
        self.machining = MultiProductMachine(env, 'Machining', [10, 12], 0.02, 15)
        self.assembly = MultiProductMachine(env, 'Assembly', [7, 8], 0.01, 5)
        self.quality_control = MultiProductMachine(env, 'Quality Control', [3, 4], 0.005, 3)
        self.packaging = MultiProductMachine(env, 'Packaging', [4, 5], 0.005, 2)

    def process_part(self, part_id):
        yield self.env.process(self.raw_material_handling.process(part_id))
        yield self.env.process(self.machining.process(part_id))
        yield self.env.process(self.assembly.process(part_id))
        yield self.env.process(self.quality_control.process(part_id))
        yield self.env.process(self.packaging.process(part_id))
        print(f'Part {part_id} finished at {self.env.now}')
#here is the counting that is called part generator, it choosee random processes and add 1 more to the generator

def multi_product_part_generator(env, system, interarrival_time, product_types):
    part_id = 1
    while True:
        yield env.timeout(interarrival_time)
        product_type = random.choice(product_types)
        part_name = f'{product_type}_{part_id}'
        env.process(system.process_part(part_name))
        part_id += 1
# here is the running simulation that for the multiple machines. 
def run_multi_product_simulation(simulation_time, interarrival_time, product_types):
    env = simpy.Environment()
    system = MultiProductManufacturingSystem(env)
    env.process(multi_product_part_generator(env, system, interarrival_time, product_types))
    env.run(until=simulation_time)

# Parameters for multi-product simulation
simulation_time = 100  # Total time to run the simulation
interarrival_time = 8  # Time between arrivals of new parts
product_types = [0, 1]  # Product types 0 and 1
#runn the simulation 
run_multi_product_simulation(simulation_time, interarrival_time, product_types)

#we had fun during the simulation of the products manufacturing. I hope that it fits what we get and imagined. 

            if random.random() < self.fail_rate:
                self.broken = True
                print(f'{self.name} broke down at {self.env.now}')
                yield self.env.timeout(self.repair_time)
                self.broken = False
                print(f'{self.name} was repaired at {self.env.now}')
#we define all multiple product manufacturing system tools, processes (all raw material, machining, assembly, quality and packaging.)
class MultiProductManufacturingSystem:
    def __init__(self, env):
        self.env = env
        self.raw_material_handling = MultiProductMachine(env, 'Raw Material Handling', [5, 6], 0.01, 10)
        self.machining = MultiProductMachine(env, 'Machining', [10, 12], 0.02, 15)
        self.assembly = MultiProductMachine(env, 'Assembly', [7, 8], 0.01, 5)
        self.quality_control = MultiProductMachine(env, 'Quality Control', [3, 4], 0.005, 3)
        self.packaging = MultiProductMachine(env, 'Packaging', [4, 5], 0.005, 2)

    def process_part(self, part_id):
        yield self.env.process(self.raw_material_handling.process(part_id))
        yield self.env.process(self.machining.process(part_id))
        yield self.env.process(self.assembly.process(part_id))
        yield self.env.process(self.quality_control.process(part_id))
        yield self.env.process(self.packaging.process(part_id))
        print(f'Part {part_id} finished at {self.env.now}')
#here is the counting that is called part generator, it choosee random processes and add 1 more to the generator

def multi_product_part_generator(env, system, interarrival_time, product_types):
    part_id = 1
    while True:
        yield env.timeout(interarrival_time)
        product_type = random.choice(product_types)
        part_name = f'{product_type}_{part_id}'
        env.process(system.process_part(part_name))
        part_id += 1
# here is the running simulation that for the multiple machines. 
def run_multi_product_simulation(simulation_time, interarrival_time, product_types):
    env = simpy.Environment()
    system = MultiProductManufacturingSystem(env)
    env.process(multi_product_part_generator(env, system, interarrival_time, product_types))
    env.run(until=simulation_time)

# Parameters for multi-product simulation
simulation_time = 100  # Total time to run the simulation
interarrival_time = 8  # Time between arrivals of new parts
product_types = [0, 1]  # Product types 0 and 1
#runn the simulation 
run_multi_product_simulation(simulation_time, interarrival_time, product_types)

#we had fun during the simulation of the products manufacturing. I hope that it fits what we get and imagined. 
