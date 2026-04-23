# PDF Equation Solver Module

A complete, fully-local Python module that reads PDFs, extracts mathematical equations, solves them using SymPy, and saves results to Word documents.

## Features

✅ **Fully Local** - No external APIs, everything runs locally  
✅ **LLM-Powered Extraction** - Uses Ollama for intelligent equation recognition  
✅ **Symbolic Math** - Uses SymPy for accurate equation solving  
✅ **Word Document Output** - Results saved to professional .docx files  
✅ **Error Handling** - Comprehensive error handling and logging  
✅ **Modular Design** - Each component is independent and reusable  
✅ **Batch Processing** - Process multiple PDFs automatically  
✅ **System Solutions** - Solve systems of equations  

## Module Structure

```
friday/system/
├── pdf_reader.py          # Read PDF files
├── equation_extractor.py  # Extract equations using Ollama LLM
├── solver.py              # Solve equations with SymPy
├── doc_writer.py          # Write results to Word documents
└── pdf_solver.py          # Main orchestrator (pipeline)
```

## Installation

### 1. Install Dependencies

```bash
pip install PyPDF2 sympy python-docx ollama
```

Or use the project's pyproject.toml:

```bash
pip install -e .
```

### 2. Start Ollama Server

```bash
ollama serve
```

In another terminal, pull a model:

```bash
ollama pull mistral
```

## Usage

### Quick Start (One-Liner)

```python
from friday.system.pdf_solver import solve_pdf

result = solve_pdf("equations.pdf", "solutions.docx")
print(f"Found: {result['equations_found']} equations")
print(f"Solved: {result['equations_solved']} equations")
```

### Detailed Usage

```python
from friday.system.pdf_solver import PDFEquationSolver

# Create solver
solver = PDFEquationSolver(
    ollama_model="mistral",
    ollama_host="http://localhost:11434"
)

# Solve PDF
result = solver.solve_pdf(
    pdf_path="equations.pdf",
    output_path="solutions.docx",
    include_context=True
)

# Check results
if result["status"] == "success":
    print(f"✓ Processing complete")
    print(f"  Equations found: {result['equations_found']}")
    print(f"  Equations solved: {result['equations_solved']}")
    print(f"  Output: {result['output_file']}")
    print(f"  Time: {result['processing_time']:.2f}s")
else:
    print(f"✗ Error: {result['message']}")
```

### Extract Equations Only

```python
result = solver.extract_equations_only("equations.pdf")

for eq in result['equations']:
    print(f"Found: {eq}")
```

### Solve Specific Pages

```python
result = solver.solve_pdf_pages(
    pdf_path="equations.pdf",
    page_numbers=[1, 2, 3],  # Only pages 1-3
    output_path="solutions.docx"
)
```

### Solve List of Equations

```python
equations = [
    "x + 2 = 5",
    "2*x^2 - 3*x + 1 = 0",
    "y = 2*x + 3"
]

result = solver.solve_equations_list(
    equations=equations,
    output_path="solutions.docx"
)
```

### System of Equations

```python
equations = [
    "2*x + y = 5",
    "x - y = 1"
]

result = solver.solve_equations_list(equations, "solutions.docx")
```

## Component Usage

### 1. PDF Reader

```python
from friday.system.pdf_reader import PDFReader

reader = PDFReader()
text = reader.read_pdf("document.pdf")

# With metadata
result = reader.read_pdf_with_metadata("document.pdf")
print(f"Title: {result['title']}")
print(f"Pages: {result['num_pages']}")
```

### 2. Equation Extractor

```python
from friday.system.equation_extractor import EquationExtractor

extractor = EquationExtractor(model="mistral")
equations = extractor.extract_equations(text)

# With context
equations_with_context = extractor.extract_with_context(text)
for eq_data in equations_with_context:
    print(f"Equation: {eq_data['equation']}")
    print(f"Context: {eq_data['context']}")

# Validate equation
is_valid = extractor.validate_equation("x + 2 = 5")
```

### 3. Equation Solver

```python
from friday.system.solver import EquationSolver

solver = EquationSolver()

# Single equation
result = solver.solve_equation("x^2 - 5*x + 6 = 0")
print(f"Status: {result['status']}")
print(f"Solutions: {result['solutions']}")

# Multiple equations
solutions = solver.solve_multiple_equations([
    "x + 2 = 5",
    "y^2 = 16"
])

# System of equations
system_result = solver.solve_system([
    "2*x + y = 5",
    "x - y = 1"
])

# Simplify solution
simplified = solver.simplify_solution("(-1 + sqrt(5))/2")

# Verify solution
is_valid = solver.evaluate_solution("x + 2 = 5", {"x": "3"})
```

### 4. Document Writer

```python
from friday.system.doc_writer import DocumentWriter

writer = DocumentWriter()

# Create document with solutions
writer.create_solution_document(
    output_path="solutions.docx",
    equations=["x + 2 = 5", "y^2 = 16"],
    solutions=solution_list,
    pdf_source="original.pdf",
    title="Equation Solutions"
)

# Append to existing document
writer.append_to_document(
    doc_path="solutions.docx",
    equations=["z = 10"],
    solutions=more_solutions,
    section_title="Additional Equations"
)

# Create summary
writer.create_summary_document(
    output_path="summary.docx",
    summary_data={
        "equations_extracted": 10,
        "equations_solved": 8,
        "solutions": solution_list
    }
)
```

## Result Format

### Solve PDF Response

```python
{
    "status": "success",
    "message": "Process completed",
    "equations_found": 5,
    "equations_solved": 4,
    "solutions": [
        {
            "original": "x + 2 = 5",
            "solutions": [{"x": "3"}],
            "variables": ["x"],
            "status": "success",
            "message": ""
        },
        ...
    ],
    "processing_time": 2.45,
    "output_file": "solutions.docx"
}
```

### Equation Solution Response

```python
{
    "original": "x^2 - 5*x + 6 = 0",
    "solutions": [
        {"x": "2"},
        {"x": "3"}
    ],
    "variables": ["x"],
    "status": "success",
    "message": ""
}
```

## Configuration

### Ollama Models

Available models:
- `mistral` - Fast, good for equation extraction
- `neural-chat` - Alternative option
- `llama2` - Larger model, more accurate

Pull a model:
```bash
ollama pull mistral
```

List available models:
```bash
ollama list
```

### Logging

```python
import logging

# Set logging level
solver = PDFEquationSolver(log_level=logging.DEBUG)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Examples

See `test_pdf_solver.py` for 10 comprehensive examples:

1. Simple usage
2. Detailed configuration
3. Specific pages
4. Extraction only
5. Solve equation list
6. Component usage
7. Error handling
8. Batch processing
9. System of equations
10. Advanced features

Run examples:
```bash
python test_pdf_solver.py 1
python test_pdf_solver.py 2
# ... etc
```

## Limitations & Notes

### Equation Format

Supported formats:
- ✅ `x + 2 = 5`
- ✅ `2*x^2 - 3*x + 1 = 0`
- ✅ `x**2 + 4*x + 4 = 0`
- ✅ `sqrt(x) = 5`
- ❌ Images/embedded equations (PDFs only)

### Ollama Requirements

- Ollama must be running and accessible
- Default: `http://localhost:11434`
- Requires internet for first model download
- Models cached locally after first use

### Performance

- Equation extraction: ~1-2s per page (depends on model)
- Solving: Instant to a few seconds (depends on complexity)
- Document writing: <1s

### PDF Support

- Text-based PDFs: ✅ Full support
- Scanned PDFs: ❌ Not supported (no OCR)
- Encrypted PDFs: ❌ Detected and skipped
- Complex layouts: ⚠️ Best effort extraction

## Troubleshooting

### Ollama Connection Error

```
Error: Failed to connect to Ollama at http://localhost:11434
```

**Solution:**
```bash
# Start Ollama
ollama serve

# In another terminal, verify:
curl http://localhost:11434/api/tags
```

### Model Not Found

```
Model 'mistral' not found
```

**Solution:**
```bash
ollama pull mistral
```

### No Equations Found

- Ensure PDF contains readable text (not scanned)
- Try extracting with different regex patterns
- Check PDF with another tool first

### Solver Returns No Solutions

- Equation may be unsolvable
- Check equation format
- Try simplifying manually

## Integration with Friday AI

Use in your AI assistant:

```python
from friday.system.pdf_solver import solve_pdf

# User says: "Solve this PDF and save answers"
def handle_solve_pdf_request(pdf_file, output_file):
    result = solve_pdf(pdf_file, output_file)
    
    if result["status"] == "success":
        message = f"Found and solved {result['equations_solved']} equations. Results saved to {result['output_file']}"
    else:
        message = f"Error: {result['message']}"
    
    return message
```

## Performance Optimization

### Batch Processing
```python
from pathlib import Path

pdf_dir = Path("pdfs")
for pdf_file in pdf_dir.glob("*.pdf"):
    output_file = pdf_file.parent / f"{pdf_file.stem}_solutions.docx"
    solve_pdf(str(pdf_file), str(output_file))
```

### Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor

def process_pdf(pdf_path):
    output = f"{Path(pdf_path).stem}_solutions.docx"
    return solve_pdf(pdf_path, output)

with ThreadPoolExecutor(max_workers=4) as executor:
    pdf_files = list(Path("pdfs").glob("*.pdf"))
    results = executor.map(process_pdf, pdf_files)
```

### Memory Optimization
```python
# Process specific pages instead of entire PDF
result = solver.solve_pdf_pages(
    pdf_path="large_file.pdf",
    page_numbers=[1, 2, 3],  # Only first 3 pages
    output_path="solutions.docx"
)
```

## API Reference

### PDFEquationSolver

**Main class for the pipeline**

```python
PDFEquationSolver(
    model: str = "mistral",
    ollama_host: str = "http://localhost:11434",
    log_level: int = logging.INFO
)
```

**Methods:**
- `solve_pdf(pdf_path, output_path, include_context=False, solve_as_system=False)` → Dict
- `solve_pdf_pages(pdf_path, page_numbers, output_path)` → Dict
- `extract_equations_only(pdf_path)` → Dict
- `solve_equations_list(equations, output_path=None)` → Dict

### PDFReader

```python
PDFReader(log_level=logging.INFO)
```

**Methods:**
- `read_pdf(pdf_path)` → str
- `read_pdf_with_metadata(pdf_path)` → Dict
- `extract_specific_pages(pdf_path, page_numbers)` → str

### EquationExtractor

```python
EquationExtractor(model="mistral", host="http://localhost:11434", log_level=logging.INFO)
```

**Methods:**
- `extract_equations(text)` → List[str]
- `extract_with_context(text)` → List[Dict]
- `validate_equation(equation)` → bool

### EquationSolver

```python
EquationSolver(log_level=logging.INFO)
```

**Methods:**
- `solve_equation(equation)` → Dict
- `solve_multiple_equations(equations)` → List[Dict]
- `solve_system(equations)` → Dict
- `evaluate_solution(equation, solution)` → bool
- `simplify_solution(solution_str)` → str

### DocumentWriter

```python
DocumentWriter(log_level=logging.INFO)
```

**Methods:**
- `create_solution_document(output_path, equations, solutions, pdf_source=None, title="...")` → bool
- `create_system_solution_document(output_path, system_equations, system_solutions, pdf_source=None)` → bool
- `append_to_document(doc_path, equations, solutions, section_title="...")` → bool
- `create_summary_document(output_path, summary_data, pdf_source=None)` → bool

## License

Part of Friday AI Assistant project

## Support

For issues or questions:
1. Check the examples in `test_pdf_solver.py`
2. Review error messages and logging output
3. Verify Ollama is running: `ollama serve`
4. Test with simple equations first
