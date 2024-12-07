import time
from copy import deepcopy
from random import randint, seed, choices
from scipy.stats import kruskal
import matplotlib.pyplot as plt

def read_cnf(cnf_file):
   
    clauses = []
    num_vars = 0
    with open(cnf_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith('p'):
                _, _, num_vars, _ = line.split()
                num_vars = int(num_vars)
            elif line and not line.startswith(('c', '%', '0')):
                clause = list(map(int, line.split()[:-1]))
                clauses.append(clause)
    return clauses, num_vars

def check_all(clauses, state):
   
    unsatisfied_clauses = deepcopy(clauses)
    for literal in state:
        i = 0
        while i < len(unsatisfied_clauses):
            if literal in unsatisfied_clauses[i]:
                unsatisfied_clauses.remove(unsatisfied_clauses[i])
            else:
                i += 1
    return len(unsatisfied_clauses)

def random_solution(num_vars):
   
    return [x if randint(0, 1) else -x for x in range(1, num_vars + 1)]

def genetic_algorithm(clauses, num_vars, population_size, max_evaluations, mutation_rate):
   
    evaluation_count = 0
    population = [random_solution(num_vars) for _ in range(population_size)]

    best_solution = None
    best_fitness = 0

    while evaluation_count < max_evaluations:
        fitness_scores = [check_all(clauses, individual) for individual in population]
        evaluation_count += len(population)

        population = [x for _, x in sorted(zip(fitness_scores, population), key=lambda pair: pair[0])]

        current_best_fitness = len(clauses) - fitness_scores[0]
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_solution = population[0]

        cloned_population = clone_population(clauses, population, population_size)
        new_population = population_crossover(cloned_population, population_size)
        mutate_population(new_population, mutation_rate)

        population = population[:int(population_size * 0.15)] + new_population[:int(population_size * 0.85)]

    return best_solution, best_fitness / len(clauses)

def clone_population(clauses, population, size):
   
    fitness_scores = [check_all(clauses, individual) for individual in population]
    weights = [len(clauses) - score for score in fitness_scores]
    new_population = choices(population, weights=weights, k=size)
    return new_population

def population_crossover(population, size):
   
    new_population = []
    num_vars = len(population[0])
    for _ in range(size):
        limit = randint(1, num_vars - 1)
        parent1 = population[randint(0, size - 1)]
        parent2 = population[randint(0, size - 1)]
        new_population.append(parent1[:limit] + parent2[limit:])
    return new_population

def mutate_population(population, mutation_rate):
   
    num_vars = len(population[0])
    num_to_mutate = int(len(population) * mutation_rate)
    for _ in range(num_to_mutate):
        individual = population[randint(0, len(population) - 1)]
        index = randint(0, num_vars - 1)
        individual[index] = -individual[index]


def run_experiment(cnf_file):
    clauses, num_vars = read_cnf(cnf_file)
    
    seeds = [randint(0, int(1e6)) for _ in range(30)]
    max_evaluations = 1000
    population_size = 10
    mutation_rate = 0.1

    fitness_over_runs = []
    times = []

    for run_id, seed_value in enumerate(seeds):
        print(f"Run {run_id + 1} with seed {seed_value}")
        seed(seed_value)
        start_time = time.time()

        _, best_fitness = genetic_algorithm(
            clauses, num_vars, population_size, max_evaluations, mutation_rate
        )

        elapsed_time = time.time() - start_time
        fitness_over_runs.append(best_fitness)
        times.append(elapsed_time)
    num_groups = 3  
    group_size = len(fitness_over_runs) // num_groups
    groups = [fitness_over_runs[i *
                                group_size:(i + 1) * group_size] for i in range(num_groups)]

    if len(groups) > 1:
        stat, p_value = kruskal(*groups)
        print(
            f"Kruskal-Wallis test: H-statistic = {stat:.4f}, p-value = {p_value:.4e}")
    else:
        print("Not enough groups to perform Kruskal-Wallis test.")

    # Plot fitness over iterations
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, 31), fitness_over_runs, marker='o', label="Fitness")
    plt.xlabel("Run")
    plt.ylabel("Best Fitness")
    plt.title("Fitness vs Independent Runs")
    plt.legend()
    plt.grid()
    plt.show()

    # Plot time vs fitness
    plt.figure(figsize=(10, 6))
    plt.scatter(times, fitness_over_runs, color='blue', label="Runs")
    plt.xlabel("Time (s)")
    plt.ylabel("Best Fitness")
    plt.title("Time vs Fitness")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
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
    else:
        cnf_file = file_mapping[choice]
        run_experiment(cnf_file)
