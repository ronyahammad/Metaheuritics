import random
import time
import numpy as np
from scipy.stats import kruskal
from multiprocessing import Pool
import matplotlib.pyplot as plt


def load_cnf(file_path):
    with open(file_path, 'r') as file:
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
    return num_vars, num_clauses, clauses


def evaluate_fitness(solution, clauses):
    solution = np.array(solution)
    satisfied_clauses = sum(
        any((solution[abs(literal) - 1] if literal >
            0 else not solution[abs(literal) - 1]) for literal in clause)
        for clause in clauses
    )
    return satisfied_clauses


def evaluate_fitness_incremental(solution, clauses, tabu_list, best_fitness):
    best_neighbor = None
    best_neighbor_fitness = 0

    for i in range(len(solution)):
        neighbor = solution.copy()
        neighbor[i] = not neighbor[i]
        fitness = evaluate_fitness(neighbor, clauses)

        if tuple(neighbor) not in tabu_list or fitness > best_fitness:
            if fitness > best_neighbor_fitness:
                best_neighbor = neighbor
                best_neighbor_fitness = fitness

    return best_neighbor, best_neighbor_fitness


def tabu_search(num_vars, clauses, max_failures, allowable_failures, max_evaluations, sample_size=50):
    best_solution = None
    best_fitness = 0

    working_solution = [random.choice([True, False]) for _ in range(num_vars)]
    working_fitness = evaluate_fitness(working_solution, clauses)

    tabu_list = []
    tabu_tenure = 10
    num_failures = 0
    evaluation_count = 0

    fitness_over_time = []
    time_over_iterations = []

    while num_failures < max_failures and evaluation_count < max_evaluations:
        start_iteration_time = time.time()

        best_neighbor, best_neighbor_fitness = evaluate_fitness_incremental(
            working_solution, clauses, tabu_list, best_fitness
        )
        evaluation_count += len(working_solution)

        if best_neighbor is None:
            working_solution = [random.choice(
                [True, False]) for _ in range(num_vars)]
            working_fitness = evaluate_fitness(working_solution, clauses)
            num_failures += 1
            continue

        tabu_list.append(tuple(working_solution))
        if len(tabu_list) > tabu_tenure:
            tabu_list.pop(0)

        working_solution = best_neighbor
        working_fitness = best_neighbor_fitness

        if working_fitness > best_fitness:
            best_solution = working_solution
            best_fitness = working_fitness
            num_failures = 0
        else:
            num_failures += 1

        fitness_over_time.append(best_fitness)
        time_over_iterations.append(time.time() - start_iteration_time)

    return best_solution, best_fitness, fitness_over_time, np.cumsum(time_over_iterations)


def plot_results(fitness_over_time, time_over_iterations, parameter_effects):
    # Plot fitness over iterations
    plt.figure(figsize=(10, 6))
    plt.plot(fitness_over_time, label="Fitness over Iterations", marker="o")
    plt.xlabel("Iterations")
    plt.ylabel("Fitness")
    plt.title("Fitness vs Iterations")
    plt.legend()
    plt.grid()
    plt.show()

    # Plot time vs fitness
    plt.figure(figsize=(10, 6))
    plt.plot(time_over_iterations, fitness_over_time,
             label="Time vs Fitness", marker="x")
    plt.xlabel("Cumulative Time (s)")
    plt.ylabel("Fitness")
    plt.title("Time vs Fitness")
    plt.legend()
    plt.grid()
    plt.show()

    # Plot parameter effects
    plt.figure(figsize=(10, 6))
    for param, fitnesses in parameter_effects.items():
        plt.plot(fitnesses, label=f"{param}", marker="s")
    plt.xlabel("Parameter Setting")
    plt.ylabel("Average Fitness")
    plt.title("Effect of Parameters on Fitness")
    plt.legend()
    plt.grid()
    plt.show()


def run_msts_experiment(dimacs_file, max_failures=100, allowable_failures=10, max_evaluations=100000, num_runs=30, sample_size=50):
    num_vars, num_clauses, clauses = load_cnf(dimacs_file)

    results_list = []
    fitness_values = []
    fitness_over_time_runs = []
    time_over_iterations_runs = []

    for run in range(num_runs):
        random.seed(run)
        start_time = time.time()

        best_solution, best_fitness, fitness_over_time, time_over_iterations = tabu_search(
            num_vars, clauses, max_failures, allowable_failures, max_evaluations, sample_size=sample_size
        )

        end_time = time.time()
        results_list.append(best_fitness)
        fitness_values.append(best_fitness)
        fitness_over_time_runs.append(fitness_over_time)
        time_over_iterations_runs.append(time_over_iterations)

        print(f"Run {
              run + 1}: Best fitness = {best_fitness}, Time = {end_time - start_time:.4f} seconds")

    num_groups = 3
    group_size = num_runs // num_groups
    grouped_fitness_values = [
        fitness_values[i * group_size:(i + 1) * group_size] for i in range(num_groups)]

    if len(grouped_fitness_values) > 1:
        kw_stat, p_value = kruskal(*grouped_fitness_values)
        print("\nSummary of MSTS:")
        print(f"Average fitness: {np.mean(fitness_values):.2f}")
        print(f"Maximum fitness: {np.max(fitness_values)}")
        print(
            f"Kruskal-Wallis test: statistic = {kw_stat:.4f}, p-value = {p_value:.4f}")
    else:
        print("Not enough groups for Kruskal-Wallis test. Skipping test.")

    parameter_effects = {
        "Max Failures": [100, 200, 300],
        "Allowable Failures": [10, 20, 30],
        "Sample Size": [50, 100, 150]
    }
    parameter_results = {}

    for param_name, param_values in parameter_effects.items():
        avg_fitness_per_setting = []
        for value in param_values:
            _, _, fitness_over_time, _ = tabu_search(
                num_vars, clauses, max_failures=value, allowable_failures=allowable_failures, max_evaluations=max_evaluations, sample_size=sample_size)
            avg_fitness_per_setting.append(np.mean(fitness_over_time))
        parameter_results[param_name] = avg_fitness_per_setting

    # Plot results
    plot_results(
        fitness_over_time_runs[0], time_over_iterations_runs[0], parameter_results)


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
        dimacs_file = file_mapping[choice]
        run_msts_experiment(dimacs_file)
