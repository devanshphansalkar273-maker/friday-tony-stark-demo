"""
QUICK START - PDF Equation Solver
Most common usage patterns
"""

# ============================================================================
# 1. SIMPLEST USAGE - ONE LINE
# ============================================================================

from friday.system.pdf_solver import solve_pdf

result = solve_pdf("equations.pdf", "solutions.docx")


# ============================================================================
# 2. CHECK RESULTS
# ============================================================================

if result["status"] == "success":
    print(f"✓ Found {result['equations_found']} equations")
    print(f"✓ Solved {result['equations_solved']} equations")
    print(f"✓ Saved to: {result['output_file']}")
else:
    print(f"✗ Error: {result['message']}")


# ============================================================================
# 3. USE IN AI ASSISTANT - Handle User Request
# ============================================================================

def ai_solve_pdf_command(user_request: str, pdf_file: str):
    """User says: 'solve this PDF and save answers'"""
    
    from friday.system.pdf_solver import solve_pdf
    
    output_file = pdf_file.replace('.pdf', '_solutions.docx')
    result = solve_pdf(pdf_file, output_file)
    
    if result["status"] == "success":
        response = (
            f"I found {result['equations_found']} equations in the PDF. "
            f"I solved {result['equations_solved']} of them. "
            f"The solutions have been saved to: {result['output_file']}"
        )
    else:
        response = f"I couldn't process the PDF: {result['message']}"
    
    return response


# ============================================================================
# 4. PROCESS MULTIPLE FILES
# ============================================================================

from pathlib import Path
from friday.system.pdf_solver import PDFEquationSolver

solver = PDFEquationSolver()

# Process all PDFs in a folder
pdf_folder = Path("my_equations")
for pdf_file in pdf_folder.glob("*.pdf"):
    output = pdf_file.parent / f"{pdf_file.stem}_solutions.docx"
    result = solver.solve_pdf(str(pdf_file), str(output))
    
    status_icon = "✓" if result["status"] == "success" else "✗"
    print(f"{status_icon} {pdf_file.name}: {result['equations_solved']} solved")


# ============================================================================
# 5. EXTRACT EQUATIONS FIRST (without solving)
# ============================================================================

from friday.system.pdf_solver import PDFEquationSolver

solver = PDFEquationSolver()
result = solver.extract_equations_only("equations.pdf")

print(f"Found {result['count']} equations:")
for eq in result['equations']:
    print(f"  • {eq}")


# ============================================================================
# 6. SOLVE SPECIFIC PAGES ONLY
# ============================================================================

result = solver.solve_pdf_pages(
    pdf_path="equations.pdf",
    page_numbers=[1, 2, 3],  # Only pages 1-3
    output_path="solutions_pages_1_3.docx"
)


# ============================================================================
# 7. SOLVE A LIST OF EQUATIONS DIRECTLY
# ============================================================================

equations = [
    "x + 2 = 5",
    "2*x^2 - 3*x + 1 = 0",
    "y = 3*x + 7"
]

result = solver.solve_equations_list(equations, "solutions.docx")


# ============================================================================
# 8. SOLVE SYSTEM OF EQUATIONS
# ============================================================================

system = [
    "2*x + y = 5",
    "x - y = 1"
]

result = solver.solve_equations_list(system, "system_solution.docx")


# ============================================================================
# 9. CONFIGURE LOGGING TO SEE WHAT'S HAPPENING
# ============================================================================

import logging

# Turn on debug logging
solver = PDFEquationSolver(log_level=logging.DEBUG)
result = solver.solve_pdf("equations.pdf", "solutions.docx")


# ============================================================================
# 10. USE INDIVIDUAL COMPONENTS
# ============================================================================

from friday.system.pdf_reader import PDFReader
from friday.system.equation_extractor import EquationExtractor
from friday.system.solver import EquationSolver
from friday.system.doc_writer import DocumentWriter

# Step 1: Read PDF
reader = PDFReader()
text = reader.read_pdf("equations.pdf")

# Step 2: Extract equations
extractor = EquationExtractor()
equations = extractor.extract_equations(text)

# Step 3: Solve equations
equation_solver = EquationSolver()
solutions = equation_solver.solve_multiple_equations(equations)

# Step 4: Save results
writer = DocumentWriter()
writer.create_solution_document(
    "solutions.docx",
    equations,
    solutions,
    pdf_source="equations.pdf"
)


# ============================================================================
# REQUIREMENTS BEFORE STARTING
# ============================================================================

"""
1. Install dependencies:
   pip install PyPDF2 sympy python-docx ollama

2. Start Ollama server:
   ollama serve

3. Download a model (in another terminal):
   ollama pull mistral

4. Verify setup:
   curl http://localhost:11434/api/tags
"""


# ============================================================================
# SUPPORTED EQUATION FORMATS
# ============================================================================

supported = [
    "x + 2 = 5",                    # Linear
    "2*x - 3 = 7",                  # Linear with coefficient
    "x^2 - 5*x + 6 = 0",            # Quadratic
    "2*x**2 + 3*x - 1 = 0",         # Alternative power syntax
    "sqrt(x) = 3",                  # With function
    "x^2 + y^2 = 25",               # Multiple variables
    "2*x + 3*y = 7",                # System compatible
    "x - y = 1",                    # System compatible
    "sin(x) = 0.5",                 # Trigonometric
    "log(x) = 2",                   # Logarithmic
]

unsupported = [
    "find the value",              # Natural language
    "x**2 + y = [image]",          # Embedded images
    "what is x?",                  # Questions
]


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Problem: "Failed to connect to Ollama"
Solution: Make sure Ollama is running:
          ollama serve

Problem: "Model 'mistral' not found"
Solution: Pull the model:
          ollama pull mistral

Problem: "No equations found"
Solution: - Check PDF is text-based (not scanned)
          - Try a different Ollama model
          - Use extract_equations_only() to debug

Problem: "Solver returns no solutions"
Solution: - Equation might be unsolvable
          - Check equation format
          - Try solver.solve_equation() with debug logging
"""


# ============================================================================
# NEXT STEPS
# ============================================================================

"""
For more advanced usage:
- Read PDF_SOLVER_README.md for full documentation
- Check test_pdf_solver.py for 10 detailed examples
- Review individual module docstrings:
  - friday.system.pdf_reader.PDFReader
  - friday.system.equation_extractor.EquationExtractor
  - friday.system.solver.EquationSolver
  - friday.system.doc_writer.DocumentWriter
  - friday.system.pdf_solver.PDFEquationSolver
"""
