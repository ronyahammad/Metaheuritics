import random
import itertools
import time

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
assert len(clauses) == num_clauses, f"Expected {num_clauses} clauses but got {len(clauses)}"


def evaluate_fitness(solution, clauses):
    satisfied_clauses = 0
    for clause in clauses:
        if any((literal > 0 and solution[abs(literal) - 1]) or (literal < 0 and not solution[abs(literal) - 1]) for literal in clause):
            satisfied_clauses += 1
    return satisfied_clauses


def generate_k_bit_neighbours(solution, k):
    neighbours = []
    indices = list(range(len(solution)))
    for bit_indices in itertools.combinations(indices, k):
        neighbour = list(solution)
        for i in bit_indices:
            neighbour[i] = 1 - neighbour[i]
        neighbours.append(neighbour)
    return neighbours

def multi_start_vna(max_iterations, max_evaluations):
    total_evaluations = 0
    best_global_solution = None
    best_global_fitness = 0

    while total_evaluations < max_evaluations:
        initial_solution = [random.choice([0, 1]) for _ in range(num_vars)]
        current_solution = initial_solution
        best_solution = current_solution
        best_fitness = evaluate_fitness(current_solution, clauses)

        evaluations = 0
        k = 1
        while k <= 3 and evaluations < max_iterations:
            neighbours = generate_k_bit_neighbours(current_solution, k)
            random.shuffle(neighbours)

            improvement_found = False
            for neighbour in neighbours:
                fitness = evaluate_fitness(neighbour, clauses)
                evaluations += 1
                total_evaluations += 1

                if fitness > best_fitness:
                    best_solution = neighbour
                    best_fitness = fitness
                    improvement_found = True
                    break

                if total_evaluations >= max_evaluations:
                    break

            if improvement_found:
                current_solution = best_solution
                k = 1
            else:
                k += 1

            if total_evaluations >= max_evaluations:
                break

        if best_fitness > best_global_fitness:
            best_global_solution = best_solution
            best_global_fitness = best_fitness

        if best_global_fitness == num_clauses:
            break

    return best_global_solution, total_evaluations


num_runs = 30
max_iterations = 10000
max_evaluations = 10_000_000

times = []
best_solutions = []
best_fitness_values = []
evaluations_list = []

for run in range(num_runs):
    start_time = time.time()

    best_solution, total_evaluations = multi_start_vna(
        max_iterations, max_evaluations)

    end_time = time.time()

    time_taken = end_time - start_time
    times.append(time_taken)

    best_fitness = evaluate_fitness(best_solution, clauses)
    best_solutions.append(best_solution)
    best_fitness_values.append(best_fitness)
    evaluations_list.append(total_evaluations)

    print(f"Run {run + 1}: Best solution satisfies {best_fitness}/{num_clauses} clauses, Time taken: {
          time_taken:.4f} seconds, Total evaluations: {total_evaluations}")

print("\nSummary of 30 runs:")
print(f"Average time: {sum(times) / num_runs:.4f} seconds")
print(f"Maximum clauses satisfied in any run: {max(best_fitness_values)}")
print(f"Average clauses satisfied: {sum(best_fitness_values) / num_runs}")
print(f"Average evaluations per run: {sum(evaluations_list) / num_runs}")
