"""
PDF Equation Solver - Usage Examples and Tests

This file demonstrates how to use the PDF Equation Solver module
in various scenarios.
"""

import logging
from pathlib import Path

from friday.system.pdf_solver import PDFEquationSolver, solve_pdf
from friday.system.pdf_reader import PDFReader
from friday.system.equation_extractor import EquationExtractor
from friday.system.solver import EquationSolver


# Configure logging for examples
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_simple_usage():
    """
    Example 1: Simple one-liner usage for basic PDF solving.
    """
    print("\n" + "="*60)
    print("Example 1: Simple Usage")
    print("="*60)
    
    # Most basic usage - single function call
    result = solve_pdf(
        pdf_path="equations.pdf",
        output_path="solutions.docx"
    )
    
    print(f"Status: {result['status']}")
    print(f"Equations found: {result['equations_found']}")
    print(f"Equations solved: {result['equations_solved']}")
    print(f"Processing time: {result['processing_time']:.2f}s")


def example_2_detailed_usage():
    """
    Example 2: Detailed usage with custom configuration.
    """
    print("\n" + "="*60)
    print("Example 2: Detailed Usage with Configuration")
    print("="*60)
    
    # Create solver with custom settings
    solver = PDFEquationSolver(
        ollama_model="mistral",
        ollama_host="http://localhost:11434",
        log_level=logging.DEBUG
    )
    
    # Solve PDF
    result = solver.solve_pdf(
        pdf_path="equations.pdf",
        output_path="solutions.docx",
        include_context=True,
        solve_as_system=False
    )
    
    # Check result
    if result["status"] == "success":
        print(f"✓ Successfully processed PDF")
        print(f"  - Extracted: {result['equations_found']} equations")
        print(f"  - Solved: {result['equations_solved']} equations")
        print(f"  - Output: {result['output_file']}")
        
        # Print each solution
        for i, sol in enumerate(result['solutions'], 1):
            print(f"\n  Solution {i}:")
            print(f"    Original: {sol['original']}")
            print(f"    Status: {sol['status']}")
            if sol['solutions']:
                for var_sol in sol['solutions']:
                    print(f"    {var_sol}")
    else:
        print(f"✗ Error: {result['message']}")


def example_3_specific_pages():
    """
    Example 3: Solve equations from specific pages only.
    """
    print("\n" + "="*60)
    print("Example 3: Process Specific Pages")
    print("="*60)
    
    solver = PDFEquationSolver()
    
    # Only process pages 1-3 and 5
    result = solver.solve_pdf_pages(
        pdf_path="equations.pdf",
        page_numbers=[1, 2, 3, 5],
        output_path="solutions_pages_1_3_5.docx"
    )
    
    print(f"Processed pages: [1, 2, 3, 5]")
    print(f"Found: {result['equations_found']} equations")
    print(f"Solved: {result['equations_solved']} equations")


def example_4_extraction_only():
    """
    Example 4: Extract equations without solving.
    """
    print("\n" + "="*60)
    print("Example 4: Extract Equations Only")
    print("="*60)
    
    solver = PDFEquationSolver()
    
    result = solver.extract_equations_only("equations.pdf")
    
    if result['status'] == 'success':
        print(f"Found {result['count']} equations:\n")
        for i, eq in enumerate(result['equations'], 1):
            print(f"  {i}. {eq}")
    else:
        print(f"Error: {result['message']}")


def example_5_solve_list():
    """
    Example 5: Solve a list of equations directly.
    """
    print("\n" + "="*60)
    print("Example 5: Solve Equations List")
    print("="*60)
    
    solver = PDFEquationSolver()
    
    # List of equations to solve
    equations = [
        "x + 2 = 5",
        "2*x^2 - 3*x + 1 = 0",
        "x^2 + 4*x + 4 = 0",
        "3*y - 7 = 2",
    ]
    
    result = solver.solve_equations_list(
        equations=equations,
        output_path="solutions_list.docx"
    )
    
    print(f"Equations: {len(result['equations'])}")
    print(f"Solved: {result['equations_solved']}\n")
    
    for sol in result['solutions']:
        print(f"  {sol['original']}")
        if sol['solutions']:
            for var_sol in sol['solutions']:
                print(f"    → {var_sol}")
        else:
            print(f"    Error: {sol['message']}")


def example_6_component_usage():
    """
    Example 6: Use individual components separately.
    """
    print("\n" + "="*60)
    print("Example 6: Individual Component Usage")
    print("="*60)
    
    # Step 1: Read PDF
    print("\n1. Reading PDF...")
    reader = PDFReader()
    text = reader.read_pdf("equations.pdf")
    print(f"   ✓ Read {len(text)} characters")
    
    # Step 2: Extract equations
    print("\n2. Extracting equations...")
    extractor = EquationExtractor()
    equations = extractor.extract_equations(text)
    print(f"   ✓ Found {len(equations)} equations")
    for eq in equations[:5]:
        print(f"     - {eq}")
    
    # Step 3: Solve equations
    print("\n3. Solving equations...")
    solver = EquationSolver()
    for eq in equations[:3]:
        sol = solver.solve_equation(eq)
        print(f"   {eq}")
        if sol['status'] == 'success' and sol['solutions']:
            for s in sol['solutions']:
                print(f"     → {s}")


def example_7_error_handling():
    """
    Example 7: Proper error handling.
    """
    print("\n" + "="*60)
    print("Example 7: Error Handling")
    print("="*60)
    
    solver = PDFEquationSolver()
    
    # Non-existent file
    print("\n1. Handling missing file...")
    result = solve_pdf(
        pdf_path="nonexistent.pdf",
        output_path="solutions.docx"
    )
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    
    # Empty PDF (if you have one)
    print("\n2. Handling PDF with no text...")
    # This would require an actual empty PDF file
    
    # Invalid equation
    print("\n3. Solving invalid equation...")
    result = solver.solve_equations_list(["this is not an equation"])
    print(f"   Found: {len(result['equations'])} valid equations")


def example_8_batch_processing():
    """
    Example 8: Process multiple PDF files.
    """
    print("\n" + "="*60)
    print("Example 8: Batch Processing")
    print("="*60)
    
    solver = PDFEquationSolver()
    
    # Find all PDF files in a directory
    pdf_dir = Path("equations_folder")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files\n")
    
    results = []
    for pdf_file in pdf_files:
        output_file = pdf_file.parent / f"{pdf_file.stem}_solutions.docx"
        
        result = solver.solve_pdf(
            pdf_path=str(pdf_file),
            output_path=str(output_file)
        )
        
        results.append({
            "file": pdf_file.name,
            "equations": result['equations_found'],
            "solved": result['equations_solved'],
            "time": result['processing_time']
        })
        
        print(f"✓ {pdf_file.name}")
        print(f"  Equations: {result['equations_found']} | Solved: {result['equations_solved']}")
    
    # Summary
    print(f"\n{'='*40}")
    print(f"Total processed: {len(results)} files")
    total_equations = sum(r['equations'] for r in results)
    total_solved = sum(r['solved'] for r in results)
    print(f"Total equations: {total_equations}")
    print(f"Total solved: {total_solved}")


def example_9_system_of_equations():
    """
    Example 9: Solve system of equations.
    """
    print("\n" + "="*60)
    print("Example 9: System of Equations")
    print("="*60)
    
    solver = PDFEquationSolver()
    
    # System of equations
    equations = [
        "2*x + y = 5",
        "x - y = 1",
    ]
    
    result = solver.solve_equations_list(
        equations=equations,
        output_path="solutions_system.docx"
    )
    
    print(f"System of equations:")
    for eq in equations:
        print(f"  {eq}")
    
    print(f"\nSolution:")
    for sol in result['solutions']:
        if sol['solutions']:
            for s in sol['solutions']:
                print(f"  {s}")


def example_10_advanced_features():
    """
    Example 10: Advanced features and options.
    """
    print("\n" + "="*60)
    print("Example 10: Advanced Features")
    print("="*60)
    
    solver = PDFEquationSolver(
        ollama_model="mistral",
        ollama_host="http://localhost:11434"
    )
    
    # Extract with context
    print("\n1. Extraction with context...")
    reader = PDFReader()
    text = reader.read_pdf("equations.pdf")
    
    extractor = EquationExtractor()
    equations_with_context = extractor.extract_with_context(text)
    
    for i, eq_data in enumerate(equations_with_context[:2], 1):
        print(f"\n   Equation {i}:")
        print(f"   {eq_data['equation']}")
        print(f"   Context: {eq_data['context'][:100]}...")
    
    # Validate equations
    print("\n2. Validating equations...")
    equations_to_validate = [
        "x + 2 = 5",
        "invalid equation",
        "y^2 = 16"
    ]
    for eq in equations_to_validate:
        is_valid = extractor.validate_equation(eq)
        print(f"   {eq:20} → {'Valid' if is_valid else 'Invalid'}")
    
    # Simplify solutions
    print("\n3. Simplifying solutions...")
    equation_solver = EquationSolver()
    solution = "(-1 + sqrt(5))/2"
    simplified = equation_solver.simplify_solution(solution)
    print(f"   Original:   {solution}")
    print(f"   Simplified: {simplified}")
    
    # Evaluate solution
    print("\n4. Verifying solutions...")
    eq = "x^2 - 5*x + 6 = 0"
    sol = equation_solver.solve_equation(eq)
    print(f"   Equation: {eq}")
    if sol['solutions']:
        for s in sol['solutions']:
            is_valid = equation_solver.evaluate_solution(eq, s)
            print(f"   Solution {s}: {'✓ Valid' if is_valid else '✗ Invalid'}")


# Main function to run all examples
def run_all_examples():
    """Run all examples."""
    print("\n" + "#"*60)
    print("# PDF Equation Solver - Usage Examples")
    print("#"*60)
    
    examples = [
        example_1_simple_usage,
        example_2_detailed_usage,
        example_3_specific_pages,
        example_4_extraction_only,
        example_5_solve_list,
        example_6_component_usage,
        example_7_error_handling,
        example_8_batch_processing,
        example_9_system_of_equations,
        example_10_advanced_features,
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            logger.error(f"Error in {example_func.__name__}: {e}")
            print(f"\n✗ Example failed: {e}\n")


if __name__ == "__main__":
    # Run a specific example or all
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        example_func = globals().get(f"example_{example_num}", None)
        if example_func:
            example_func()
        else:
            print(f"Example not found: example_{example_num}")
    else:
        print("Run specific example:")
        print("  python test_pdf_solver.py 1")
        print("  python test_pdf_solver.py 2")
        print("  ...")
        print("\nOr import and use in your code:")
        print("  from friday.system.pdf_solver import solve_pdf")
        print("  result = solve_pdf('input.pdf', 'output.docx')")
