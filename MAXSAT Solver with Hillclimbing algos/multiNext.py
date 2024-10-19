# 2) Multistart Next Ascent Hillclimbing (MSNAHC):
import random
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

# Load the CNF file
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


def generate_neighbours(solution):
    neighbours = []
    for i in range(len(solution)):
        neighbour = list(solution)
        neighbour[i] = 1 - neighbour[i]
        neighbours.append(neighbour)
    return neighbours


def msnahc(clauses, num_vars, max_evaluations=20000000):
    global_evaluations = 0
    best_solution = None
    best_fitness = -1
    best_eval_count = 0

    while global_evaluations < max_evaluations:

        current_solution = [random.choice([0, 1]) for _ in range(num_vars)]
        current_fitness = evaluate_fitness(current_solution, clauses)
        eval_count = 1

        while eval_count + global_evaluations < max_evaluations:
            neighbours = generate_neighbours(current_solution)
            random.shuffle(neighbours)
            local_best = False

            for neighbour in neighbours:
                neighbour_fitness = evaluate_fitness(neighbour, clauses)
                eval_count += 1

                if neighbour_fitness > current_fitness:
                    current_solution = neighbour
                    current_fitness = neighbour_fitness
                    local_best = True
                    break

            if not local_best:
                break

        global_evaluations += eval_count

        if current_fitness > best_fitness:
            best_solution = current_solution
            best_fitness = current_fitness
            best_eval_count = global_evaluations

        if best_fitness == len(clauses):
            break

    return best_solution, best_fitness, best_eval_count, global_evaluations


num_runs = 30
max_iterations = 10000
max_evaluations = 20000000


times = []
best_solutions = []
best_fitness_values = []
eval_counts = []

for run in range(num_runs):
    start_time = time.time()

    best_solution, best_fitness, eval_count, global_evaluations = msnahc(
        clauses, num_vars, max_evaluations)

    end_time = time.time()
    time_taken = end_time - start_time

    times.append(time_taken)
    best_solutions.append(best_solution)
    best_fitness_values.append(best_fitness)
    eval_counts.append(eval_count)

    print(f"Run {run + 1}: Best fitness = {best_fitness}, Evaluations = {
          eval_count}, Time = {time_taken:.4f} seconds")


print("\nSummary of MSNAHC after 30 runs:")
print(f"Average time: {sum(times) / num_runs:.4f} seconds")
print(f"Average evaluations: {sum(eval_counts) / num_runs}")
print(f"Maximum clauses satisfied in any run: {max(best_fitness_values)}")
print(f"Average clauses satisfied: {sum(best_fitness_values) / num_runs}")
