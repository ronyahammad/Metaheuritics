

## Tasks

1. **Randomized Neighborhood Visits**  
   Ensure the neighborhood of the current solution is always visited in a random order, rather than following a fixed sequence (e.g., left-to-right or another predefined order).

2. **Test with DIMACS Instances**  
   Evaluate the algorithm using three provided DIMACS MAXSAT problem instances.

3. **Independent Runs**  
   Perform 30 independent runs of the algorithm for each problem instance and report the results.

4. **Report Results**  
   For each problem instance, provide:
   - The best solution quality obtained.
   - The number of objective function evaluations needed to reach the best solution.
   - The CPU time required.

---

## Description

The purpose of this assignment is to implement and test **hill-climbing algorithms** on instances of the **MAXSAT problem**. The algorithms will be tested on the following DIMACS instances, available via the tutorial:

- **`uf20-01.cnf`**: 20 variables, 91 clauses  
- **`uf100-01.cnf`**: 100 variables, 430 clauses  
- **`uf250-01.cnf`**: 250 variables, 1065 clauses  

---

## Algorithms to Implement

1. **Next Ascent Hill Climbing (NAHC)**  
   Using a 1-bit Hamming Distance neighborhood.

2. **Multistart Next Ascent Hill Climbing (MSNAHC)**  
   Multiple independent runs of the Next Ascent Hill Climbing algorithm.

3. **Variable Neighborhood Ascent (VNA)**  
   Exploring neighborhoods up to a 3-bit Hamming Distance.

4. **Multistart Variable Neighborhood Ascent (MSVNA)**  
   Multiple independent runs of the Variable Neighborhood Ascent algorithm.

