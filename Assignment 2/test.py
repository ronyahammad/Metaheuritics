import random
import time
import numpy as np

print("Select a MAXSAT instance to run:")
print("1) uf20-01.cnf")
print("2) uf100-01.cnf")
print("3) uf250-01.cnf")

choice = input("Enter the number of the instance (1/2/3): ").strip()

file_mapping = {
    '1': 'uf20-01.cnf',
    '2': 'uf100-01.cnf',
    '3': 'uf250-01.cnf'
}

if choice not in file_mapping:
    print("Invalid choice. Please run the script again and select a valid option.")
    exit(1)

dimacs = file_mapping[choice]

with open(dimacs, 'r') as file:
    dimacs_content = file.readlines()

clauses = []
num_vars = None
num_clauses = None

for line in dimacs_content:
    line = line.strip()
    if line.startswith('c') or line == '' or line.startswith('%') or line.startswith('0'):
        continue
    if line.startswith('p'):
        _, _, num_vars, num_clauses = line.split()
        num_vars = int(num_vars)
        num_clauses = int(num_clauses)
        continue
    clause = list(map(int, line.split()[:-1]))
    clauses.append(clause)

assert len(clauses) == num_clauses, f"Expected {
    num_clauses} clauses but got {len(clauses)}"



def evaluate_fitness(solution):
    return np.sum(np.any(np.where(clause_matrix > 0, solution[np.abs(clause_matrix) - 1], ~solution[np.abs(clause_matrix) - 1]), axis=1))


def flip_bit(solution, index):
    return solution ^ (1 << index)


def next_ascent_hillclimbing(initial_solution, max_iterations):
    current_solution = initial_solution
    best_fitness = evaluate_fitness(current_solution)

    for _ in range(max_iterations):
        improved = False
        indices = list(range(num_vars))
        random.shuffle(indices)

        for i in indices:
            neighbor = flip_bit(current_solution, i)
            fitness = evaluate_fitness(neighbor)
            if fitness > best_fitness:
                current_solution = neighbor
                best_fitness = fitness
                improved = True
                break

        if not improved or best_fitness == num_clauses:
            break

    return current_solution, best_fitness


num_runs = 30
max_iterations = 10000

times = []
best_fitness_values = []

# Convert clauses to a numpy array for faster processing
clause_matrix = np.array(clauses)

for run in range(num_runs):
    initial_solution = random.getrandbits(num_vars)

    start_time = time.time()
    best_solution = next_ascent_hillclimbing(initial_solution, max_iterations)
    end_time = time.time()
    time_taken = end_time - start_time
    times.append(time_taken)
    best_fitness = evaluate_fitness(best_solution)
    best_fitness_values.append(best_fitness)

    print(f"Run {run + 1}: Best solution satisfies {best_fitness}/{
          num_clauses} clauses, Time taken: {time_taken:.4f} seconds")

print("\nSummary of 30 runs:")
print(f"Average time: {sum(times) / num_runs:.4f} seconds")
print(f"Maximum clauses satisfied in any run: {max(best_fitness_values)}")
print(f"Average clauses satisfied: {sum(best_fitness_values) / num_runs:.2f}")
