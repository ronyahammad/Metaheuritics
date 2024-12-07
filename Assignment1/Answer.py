import itertools
import time

def read_dimacs_file(filename):
    """Reads a DIMACS file and returns the number of variables, clauses, and clause list.

    Args:
        filename: The name of the DIMACS file.

    Returns:
        A tuple containing the number of variables, number of clauses, and a list of clauses.
    """

    with open(filename, 'r') as file:
        dimacs_content = file.readlines()

    clauses = []
    num_vars = None
    num_clauses = None

    for line in dimacs_content:
        line = line.strip()

        # Skip comments, empty lines, '%' or '0'
        if line.startswith('c') or line == '' or line.startswith('%') or line.startswith('0'):
            continue

        # Parse 'p' line to get number of variables and clauses
        if line.startswith('p'):
            _, _, num_vars, num_clauses = line.split()
            num_vars = int(num_vars)
            num_clauses = int(num_clauses)
            continue

        # Parse the clause and append to the clauses list
        clause = list(map(int, line.split()[:-1]))
        clauses.append(clause)

    assert len(clauses) == num_clauses, f"Expected {num_clauses} clauses but got {len(clauses)}"

    return num_vars, num_clauses, clauses

def find_satisfying_assignments(num_vars, clauses):
    """Finds all satisfying assignments for a given set of clauses.

    Args:
        num_vars: The number of variables.
        clauses: A list of clauses.

    Returns:
        A list of satisfying assignments.
    """

    best_assignments = []
    satisfied_assignment_count = 0

    # Generate all possible truth assignments for the variables
    for assignment in itertools.product([False, True], repeat=num_vars):
        satisfied_clauses = 0

        # Evaluate the current assignment
        for clause in clauses:
            satisfied = False
            for literal in clause:
                var = abs(literal)
                is_true = assignment[var - 1]

                if (literal > 0 and is_true) or (literal < 0 and not is_true):
                    satisfied = True
                    break

            if satisfied:
                satisfied_clauses += 1
            else:
                break

        # If all clauses are satisfied by this assignment
        if satisfied_clauses == len(clauses):
            satisfied_assignment_count += 1
            best_assignments.append(assignment)

    return best_assignments, satisfied_assignment_count

def main():
    filename = 'hoos.cnf'
    num_vars, num_clauses, clauses = read_dimacs_file(filename)

    start_time = time.time()
    best_assignments, satisfied_assignment_count = find_satisfying_assignments(num_vars, clauses)
    end_time = time.time()

    execution_time = end_time - start_time

    print(f"Number of variables: {num_vars}")
    print(f"Number of clauses: {num_clauses}")
    print(f"Number of satisfying assignments: {satisfied_assignment_count}")

    if satisfied_assignment_count > 0:
        print("Best assignments:")
        for i, assignment in enumerate(best_assignments, start=1):
            print(f"No {i} best assignment: {', '.join(map(str, assignment))}")
    else:
        print("No satisfying assignment found.")

    print(f"Execution time: {execution_time:.6f} seconds")

if __name__ == "__main__":
    main()