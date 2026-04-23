"""
Equation Solver Module
Converts extracted equations to SymPy format and solves them.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple

try:
    import sympy as sp
    from sympy import symbols, solve, parse_expr, Eq
    from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application
except ImportError:
    raise ImportError("sympy is required. Install it with: pip install sympy")


logger = logging.getLogger(__name__)


class EquationSolver:
    """Solve mathematical equations using SymPy."""

    def __init__(self, log_level: int = logging.INFO):
        """
        Initialize EquationSolver.
        
        Args:
            log_level: Logging level for the solver
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        self.transformations = (
            standard_transformations + (implicit_multiplication_application,)
        )

    def solve_equation(self, equation: str) -> Dict[str, Any]:
        """
        Solve a single equation and return solution details.
        
        Args:
            equation: Equation string (e.g., "x + 2 = 5")
            
        Returns:
            Dictionary with:
                - 'original': Original equation
                - 'solutions': List of solutions
                - 'variables': Variables found in equation
                - 'status': 'success' or 'error'
                - 'message': Error message if status is 'error'
        """
        result = {
            "original": equation,
            "solutions": [],
            "variables": [],
            "status": "success",
            "message": ""
        }

        try:
            self.logger.info(f"Solving equation: {equation}")
            
            # Clean and normalize equation
            cleaned_eq = self._clean_equation(equation)
            self.logger.debug(f"Cleaned equation: {cleaned_eq}")
            
            # Parse equation
            sympy_eq = self._parse_equation(cleaned_eq)
            
            # Extract variables
            variables = self._extract_variables(sympy_eq)
            result["variables"] = [str(var) for var in variables]
            
            # Solve equation
            solutions = solve(sympy_eq, variables)
            
            # Format solutions
            if solutions:
                result["solutions"] = self._format_solutions(solutions, variables)
                self.logger.info(f"Found {len(result['solutions'])} solution(s)")
            else:
                result["solutions"] = []
                result["message"] = "No solutions found (equation may be inconsistent)"
                self.logger.warning("No solutions found")
            
            return result

        except Exception as e:
            error_msg = f"Error solving equation: {str(e)}"
            self.logger.error(error_msg)
            result["status"] = "error"
            result["message"] = error_msg
            return result

    def solve_multiple_equations(self, equations: List[str]) -> List[Dict[str, Any]]:
        """
        Solve multiple equations.
        
        Args:
            equations: List of equation strings
            
        Returns:
            List of solution dictionaries
        """
        self.logger.info(f"Solving {len(equations)} equations")
        solutions = []
        
        for equation in equations:
            solution = self.solve_equation(equation)
            solutions.append(solution)
        
        return solutions

    def solve_system(self, equations: List[str]) -> Dict[str, Any]:
        """
        Solve a system of equations simultaneously.
        
        Args:
            equations: List of equation strings
            
        Returns:
            Dictionary with system solutions
        """
        result = {
            "equations": equations,
            "solutions": [],
            "status": "success",
            "message": ""
        }

        try:
            self.logger.info(f"Solving system of {len(equations)} equations")
            
            # Clean and parse all equations
            sympy_equations = []
            all_variables = set()
            
            for eq in equations:
                cleaned_eq = self._clean_equation(eq)
                sympy_eq = self._parse_equation(cleaned_eq)
                sympy_equations.append(sympy_eq)
                
                variables = self._extract_variables(sympy_eq)
                all_variables.update(variables)
            
            # Solve system
            all_variables = list(all_variables)
            solutions = solve(sympy_equations, all_variables)
            
            # Format solutions
            if solutions:
                if isinstance(solutions, dict):
                    # Single solution set
                    result["solutions"] = [solutions]
                elif isinstance(solutions, list):
                    # Multiple solution sets
                    result["solutions"] = solutions
                else:
                    result["solutions"] = [solutions]
                
                self.logger.info(f"Found system solutions: {result['solutions']}")
            else:
                result["solutions"] = []
                result["message"] = "No solutions found for this system"
                self.logger.warning("No system solutions found")
            
            return result

        except Exception as e:
            error_msg = f"Error solving system of equations: {str(e)}"
            self.logger.error(error_msg)
            result["status"] = "error"
            result["message"] = error_msg
            return result

    def _clean_equation(self, equation: str) -> str:
        """
        Clean and normalize equation string.
        
        Args:
            equation: Raw equation string
            
        Returns:
            Cleaned equation
        """
        # Remove extra whitespace
        equation = " ".join(equation.split())
        
        # Convert ^ to ** for exponentiation
        equation = equation.replace("^", "**")
        
        # Handle common notation variations
        equation = equation.replace(" / ", "/")
        equation = equation.replace("/ ", "/")
        equation = equation.replace(" /", "/")
        
        return equation

    def _parse_equation(self, equation: str) -> sp.Eq:
        """
        Parse string equation into SymPy equation object.
        
        Args:
            equation: Cleaned equation string
            
        Returns:
            SymPy Eq object
        """
        if "=" not in equation:
            raise ValueError(f"Invalid equation format: {equation}")
        
        left_str, right_str = equation.split("=", 1)
        
        try:
            left = parse_expr(
                left_str.strip(),
                transformations=self.transformations,
                local_dict=self._get_common_symbols()
            )
            right = parse_expr(
                right_str.strip(),
                transformations=self.transformations,
                local_dict=self._get_common_symbols()
            )
            
            return Eq(left, right)
        
        except Exception as e:
            raise ValueError(f"Could not parse equation: {equation}. Error: {str(e)}")

    def _extract_variables(self, expr: Any) -> List[sp.Symbol]:
        """
        Extract variables from SymPy expression.
        
        Args:
            expr: SymPy expression
            
        Returns:
            List of variable symbols
        """
        variables = list(expr.free_symbols)
        # Filter out pi, e, and other constants
        variables = [v for v in variables if not self._is_constant(v)]
        return sorted(variables, key=lambda x: str(x))

    def _is_constant(self, symbol: sp.Symbol) -> bool:
        """Check if symbol is a known constant."""
        constants = {"pi", "e", "i", "E", "I"}
        return str(symbol) in constants

    def _format_solutions(self, solutions: Any, variables: List[sp.Symbol]) -> List[Dict]:
        """
        Format solutions into readable format.
        
        Args:
            solutions: Solutions from SymPy solve()
            variables: List of variables
            
        Returns:
            List of formatted solution dicts
        """
        formatted = []
        
        # Handle different solution formats
        if isinstance(solutions, dict):
            # Single solution dict
            sol_dict = {}
            for var, val in solutions.items():
                sol_dict[str(var)] = str(val)
            formatted.append(sol_dict)
        
        elif isinstance(solutions, (list, tuple)):
            # List or tuple of solutions
            for sol in solutions:
                if isinstance(sol, dict):
                    sol_dict = {str(k): str(v) for k, v in sol.items()}
                    formatted.append(sol_dict)
                elif isinstance(sol, (tuple, list)):
                    # Tuple of values corresponding to variables
                    sol_dict = {}
                    for var, val in zip(variables, sol):
                        sol_dict[str(var)] = str(val)
                    formatted.append(sol_dict)
                else:
                    # Single value solution
                    if variables:
                        formatted.append({str(variables[0]): str(sol)})
        
        else:
            # Single value
            if variables:
                formatted.append({str(variables[0]): str(solutions)})
        
        return formatted

    def _get_common_symbols(self) -> Dict:
        """Get dictionary of commonly used symbols for parsing."""
        symbols_dict = {
            'x': sp.Symbol('x'),
            'y': sp.Symbol('y'),
            'z': sp.Symbol('z'),
            'a': sp.Symbol('a'),
            'b': sp.Symbol('b'),
            'c': sp.Symbol('c'),
            't': sp.Symbol('t'),
            'n': sp.Symbol('n'),
        }
        return symbols_dict

    def evaluate_solution(self, equation: str, solution: Dict[str, str]) -> bool:
        """
        Verify if solution is correct by substituting back into equation.
        
        Args:
            equation: Original equation string
            solution: Solution dictionary
            
        Returns:
            True if solution is correct
        """
        try:
            cleaned_eq = self._clean_equation(equation)
            sympy_eq = self._parse_equation(cleaned_eq)
            
            # Convert solution values to numeric/symbolic
            sol_dict = {}
            for var, val in solution.items():
                try:
                    sol_dict[sp.Symbol(var)] = parse_expr(val)
                except:
                    sol_dict[sp.Symbol(var)] = val
            
            # Evaluate both sides
            left_val = sympy_eq.lhs.subs(sol_dict)
            right_val = sympy_eq.rhs.subs(sol_dict)
            
            # Check if equal (with small tolerance for floating point)
            return sp.simplify(left_val - right_val) == 0
        
        except Exception as e:
            self.logger.warning(f"Could not verify solution: {e}")
            return False

    def simplify_solution(self, solution_str: str) -> str:
        """
        Simplify a solution expression.
        
        Args:
            solution_str: Solution as string
            
        Returns:
            Simplified solution as string
        """
        try:
            expr = parse_expr(
                solution_str,
                transformations=self.transformations,
                local_dict=self._get_common_symbols()
            )
            simplified = sp.simplify(expr)
            return str(simplified)
        except Exception as e:
            self.logger.warning(f"Could not simplify solution: {e}")
            return solution_str
