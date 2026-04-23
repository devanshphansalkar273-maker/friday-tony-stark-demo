"""
PDF Equation Solver - Integration Guide for Friday AI

Shows how to integrate the PDF solver module into your Friday AI assistant.
"""

# ============================================================================
# 1. ADD TO FRIDAY'S TOOLS/CAPABILITIES
# ============================================================================

# File: friday/tools/tools.py (or your tools registry)

from friday.system.pdf_solver import PDFEquationSolver, solve_pdf


PDF_SOLVER_TOOLS = {
    "solve_pdf": {
        "description": "Read PDF file, extract mathematical equations, solve them, and save results to Word document",
        "function": solve_pdf,
        "parameters": {
            "pdf_path": "Path to PDF file containing equations",
            "output_path": "Path where to save the solutions Word document"
        }
    },
    "extract_equations": {
        "description": "Extract mathematical equations from a PDF without solving them",
        "function": lambda pdf: PDFEquationSolver().extract_equations_only(pdf),
        "parameters": {
            "pdf_path": "Path to PDF file"
        }
    }
}


# ============================================================================
# 2. CREATE COMMAND HANDLER
# ============================================================================

# File: friday/core/agent.py or friday/tools/system.py

import re
from pathlib import Path
from friday.system.pdf_solver import PDFEquationSolver


class PDFEquationToolHandler:
    """Handle PDF equation solving requests from AI assistant."""
    
    def __init__(self):
        self.solver = PDFEquationSolver(
            ollama_model="mistral",
            ollama_host="http://localhost:11434"
        )
    
    def handle_solve_pdf_command(self, user_input: str, pdf_file: str = None) -> str:
        """
        Handle user request like: "solve this PDF and save answers"
        
        Args:
            user_input: User's natural language request
            pdf_file: Path to PDF file (if not in request)
            
        Returns:
            Response message to user
        """
        # Extract PDF path from user input if not provided
        if not pdf_file:
            pdf_file = self._extract_pdf_path(user_input)
        
        if not pdf_file:
            return "I need a PDF file path to solve equations. Please provide the path to the PDF file."
        
        # Generate output path
        pdf_path = Path(pdf_file)
        output_path = pdf_path.parent / f"{pdf_path.stem}_solutions.docx"
        
        # Solve PDF
        result = self.solver.solve_pdf(str(pdf_path), str(output_path))
        
        # Format response
        if result["status"] == "success":
            response = (
                f"✓ Successfully processed the PDF!\n"
                f"📊 Found {result['equations_found']} equations\n"
                f"✓ Solved {result['equations_solved']} equations\n"
                f"💾 Saved results to: {result['output_file']}\n"
                f"⏱️ Processing time: {result['processing_time']:.2f} seconds"
            )
        else:
            response = f"❌ Error: {result['message']}"
        
        return response
    
    def handle_extract_only_command(self, pdf_file: str) -> str:
        """Just extract equations without solving."""
        result = self.solver.extract_equations_only(pdf_file)
        
        if result['status'] == 'success':
            equations = result['equations']
            response = f"Found {result['count']} equations:\n"
            for i, eq in enumerate(equations[:10], 1):  # Show first 10
                response += f"{i}. {eq}\n"
            
            if result['count'] > 10:
                response += f"... and {result['count'] - 10} more"
            
            return response
        else:
            return f"Error: {result.get('message', 'Unknown error')}"
    
    def _extract_pdf_path(self, user_input: str) -> str:
        """Extract file path from user input."""
        # Look for file paths with .pdf extension
        pdf_pattern = r'[\w\-./\\]+\.pdf'
        match = re.search(pdf_pattern, user_input)
        if match:
            return match.group(0)
        return None


# ============================================================================
# 3. ADD TO FRIDAY'S ROUTER
# ============================================================================

# File: friday/core/router.py

from friday.tools.pdf_handler import PDFEquationToolHandler


class FridayRouter:
    """Route user requests to appropriate handlers."""
    
    def __init__(self):
        self.pdf_handler = PDFEquationToolHandler()
    
    def route_request(self, user_input: str, **kwargs) -> str:
        """Route request based on user input."""
        
        # Check for PDF equation solving requests
        if any(word in user_input.lower() for word in ["solve", "pdf", "equation"]):
            if "equation" in user_input.lower() or "solve" in user_input.lower():
                if "pdf" in user_input.lower():
                    # Solve PDF request
                    return self.pdf_handler.handle_solve_pdf_command(user_input, kwargs.get("file"))
                elif "extract" in user_input.lower():
                    # Extract only
                    pdf_file = kwargs.get("file")
                    if pdf_file:
                        return self.pdf_handler.handle_extract_only_command(pdf_file)
        
        # Route to other handlers...
        return self._route_other_requests(user_input, **kwargs)


# ============================================================================
# 4. FRIDAY'S MAIN INTERACTION LOOP
# ============================================================================

# File: friday/main.py or agent_friday.py

from friday.core.router import FridayRouter
from friday.system.pdf_solver import solve_pdf


class FridayAssistant:
    """Main Friday AI Assistant."""
    
    def __init__(self):
        self.router = FridayRouter()
    
    def process_user_command(self, user_input: str, **context) -> str:
        """
        Process user commands including PDF equation solving.
        
        Examples:
            "Solve this PDF and save answers" → solve_pdf()
            "Extract equations from this file" → extract_equations_only()
            "What are the solutions to equations.pdf?" → solve_pdf()
        """
        
        # Check if this is a PDF equation task
        pdf_keywords = {"solve", "equation", "pdf", "extract", "equations"}
        user_words = set(user_input.lower().split())
        
        if len(pdf_keywords & user_words) >= 2:  # At least 2 matching keywords
            return self.router.route_request(user_input, **context)
        
        # Handle other requests...
        return self._process_other_commands(user_input, **context)


# ============================================================================
# 5. COMMAND-LINE INTERFACE
# ============================================================================

# File: friday/cli.py or main command interface

import argparse
from friday.system.pdf_solver import PDFEquationSolver


def create_pdf_solver_cli():
    """Create CLI for PDF equation solver."""
    
    parser = argparse.ArgumentParser(
        description="Solve mathematical equations from PDF files"
    )
    
    parser.add_argument(
        "pdf_file",
        help="Path to PDF file containing equations"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output Word document path (default: <pdf_name>_solutions.docx)",
        default=None
    )
    
    parser.add_argument(
        "-p", "--pages",
        help="Specific pages to process (e.g., 1,2,3)",
        default=None
    )
    
    parser.add_argument(
        "-e", "--extract-only",
        action="store_true",
        help="Extract equations without solving"
    )
    
    parser.add_argument(
        "-m", "--model",
        default="mistral",
        help="Ollama model to use (default: mistral)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Run solver
    solver = PDFEquationSolver(ollama_model=args.model)
    
    if args.extract_only:
        result = solver.extract_equations_only(args.pdf_file)
        print(f"Found {result['count']} equations")
        for eq in result['equations']:
            print(f"  • {eq}")
    
    else:
        output = args.output or f"{Path(args.pdf_file).stem}_solutions.docx"
        
        if args.pages:
            pages = [int(p.strip()) for p in args.pages.split(",")]
            result = solver.solve_pdf_pages(args.pdf_file, pages, output)
        else:
            result = solver.solve_pdf(args.pdf_file, output)
        
        print(f"Status: {result['status']}")
        print(f"Equations found: {result['equations_found']}")
        print(f"Equations solved: {result['equations_solved']}")
        if result['output_file']:
            print(f"Output: {result['output_file']}")


# ============================================================================
# 6. VOICE INTERFACE (IF USING VOICE)
# ============================================================================

# File: friday/voice/handler.py

class VoiceCommandHandler:
    """Handle voice commands including PDF solving."""
    
    def process_voice_command(self, command_text: str, audio_context: dict) -> str:
        """
        Process voice commands.
        
        Example:
            "Solve equations.pdf"
            "Extract equations from the PDF"
            "What equations are in this document?"
        """
        
        assistant = FridayAssistant()
        response = assistant.process_user_command(
            command_text,
            **audio_context
        )
        
        return response


# ============================================================================
# 7. MEMORY/CONTEXT INTEGRATION
# ============================================================================

# File: friday/memory/store.py (example integration)

class MemoryStore:
    """Store and retrieve PDF processing history."""
    
    def store_pdf_result(self, pdf_path: str, result: dict):
        """Store PDF solving result in memory."""
        
        memory_entry = {
            "type": "pdf_equation_solve",
            "pdf_file": pdf_path,
            "equations_found": result['equations_found'],
            "equations_solved": result['equations_solved'],
            "output_file": result['output_file'],
            "timestamp": datetime.now().isoformat(),
            "processing_time": result['processing_time']
        }
        
        # Store in vector DB or file storage
        self.store(memory_entry)
    
    def get_pdf_history(self):
        """Get history of solved PDFs."""
        return self.retrieve({"type": "pdf_equation_solve"})


# ============================================================================
# 8. CONFIGURATION
# ============================================================================

# File: friday/config.py (add these settings)

class PDFSolverConfig:
    """Configuration for PDF equation solver."""
    
    # Ollama settings
    OLLAMA_HOST = "http://localhost:11434"
    OLLAMA_MODEL = "mistral"
    
    # Timeouts
    EXTRACTION_TIMEOUT = 30  # seconds
    SOLVING_TIMEOUT = 60  # seconds
    
    # Output settings
    OUTPUT_DIR = "solutions/"
    KEEP_TEMP_FILES = False
    
    # Logging
    LOG_LEVEL = "INFO"


# ============================================================================
# 9. ERROR RECOVERY
# ============================================================================

# File: friday/tools/error_handler.py

from friday.system.pdf_solver import PDFEquationSolver


class PDFSolverErrorHandler:
    """Handle errors in PDF equation solving."""
    
    @staticmethod
    def handle_extraction_error(error: Exception) -> str:
        """Handle extraction errors gracefully."""
        if "Ollama" in str(error):
            return (
                "I tried to extract equations but couldn't connect to "
                "the equation analysis service. Make sure Ollama is running.\n"
                "Try: `ollama serve`"
            )
        elif "PDF" in str(error):
            return (
                "The PDF file seems to have a problem. "
                "Try opening it with a PDF reader first to verify it's valid."
            )
        else:
            return f"An error occurred: {str(error)}"
    
    @staticmethod
    def retry_with_fallback(pdf_path: str) -> dict:
        """Retry solving with fallback options."""
        solver = PDFEquationSolver()
        
        try:
            # Try primary method
            return solver.solve_pdf(pdf_path, f"{Path(pdf_path).stem}_solutions.docx")
        except Exception as e:
            try:
                # Fallback: extract only
                print(f"Primary method failed: {e}")
                print("Falling back to equation extraction only...")
                return solver.extract_equations_only(pdf_path)
            except Exception as e2:
                print(f"Both methods failed: {e2}")
                return {"status": "error", "message": str(e2)}


# ============================================================================
# 10. EXAMPLE USAGE IN FRIDAY
# ============================================================================

# Example: User says "Solve this PDF"
# 
# Flow:
# 1. User: "Solve equations.pdf"
# 2. Friday router detects PDF + solve keywords
# 3. Router calls: pdf_handler.handle_solve_pdf_command()
# 4. Handler calls: PDFEquationSolver.solve_pdf()
# 5. Pipeline:
#    - PDFReader.read_pdf() → Extract text
#    - EquationExtractor.extract_equations() → Find equations
#    - EquationSolver.solve_*() → Solve them
#    - DocumentWriter.create_solution_document() → Save Word doc
# 6. Handler formats result: "Found 5 equations, solved 4. Saved to solutions.docx"
# 7. Friday responds to user with status


# ============================================================================
# QUICK INTEGRATION CHECKLIST
# ============================================================================

"""
□ Install dependencies:
  pip install PyPDF2 sympy python-docx ollama

□ Start Ollama:
  ollama serve

□ Pull Ollama model:
  ollama pull mistral

□ Verify connection:
  curl http://localhost:11434/api/tags

□ Add PDF solver to Friday's tools registry

□ Create command handler for PDF requests

□ Update router to route PDF requests

□ Test with sample PDF:
  python -c "from friday.system.pdf_solver import solve_pdf; solve_pdf('test.pdf', 'out.docx')"

□ Integrate into voice/chat interface

□ Add error handling

□ Test end-to-end with user request

□ Add to memory/logging if needed

□ Document the feature for users
"""


if __name__ == "__main__":
    # Test integration
    print("PDF Equation Solver - Integration Ready")
    print("\nTo use in Friday:")
    print("1. User: 'Solve equations.pdf'")
    print("2. Friday routes to PDF handler")
    print("3. Results saved to Word document")
    print("4. User receives status update")
    
    # Run CLI
    create_pdf_solver_cli()
