"""
PDF Equation Solver - Main Orchestrator
Coordinates the full pipeline: Read PDF → Extract Equations → Solve → Write Document
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from friday.system.pdf_reader import PDFReader
from friday.system.equation_extractor import EquationExtractor
from friday.system.solver import EquationSolver
from friday.system.doc_writer import DocumentWriter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFEquationSolver:
    """
    Main coordinator for the PDF equation solving pipeline.
    
    Usage:
        solver = PDFEquationSolver()
        result = solver.solve_pdf("equations.pdf", "output.docx")
    """

    def __init__(
        self,
        ollama_model: str = "mistral",
        ollama_host: str = "http://localhost:11434",
        log_level: int = logging.INFO
    ):
        """
        Initialize PDF Equation Solver.
        
        Args:
            ollama_model: Ollama LLM model to use
            ollama_host: Ollama server host
            log_level: Logging level
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        
        # Initialize components
        self.pdf_reader = PDFReader(log_level=log_level)
        self.equation_extractor = EquationExtractor(
            model=ollama_model,
            host=ollama_host,
            log_level=log_level
        )
        self.solver = EquationSolver(log_level=log_level)
        self.doc_writer = DocumentWriter(log_level=log_level)
        
        self.logger.info("PDFEquationSolver initialized successfully")

    def solve_pdf(
        self,
        pdf_path: str,
        output_path: str,
        include_context: bool = False,
        solve_as_system: bool = False
    ) -> Dict[str, Any]:
        """
        Main entry point: Solve all equations in a PDF and save to document.
        
        Args:
            pdf_path: Path to input PDF file
            output_path: Path to output DOCX file
            include_context: Whether to include equation context in output
            solve_as_system: If True, solve equations as a system instead of individually
            
        Returns:
            Dictionary with:
                - 'status': 'success' or 'error'
                - 'message': Status message
                - 'equations_found': Number of equations extracted
                - 'equations_solved': Number of equations solved
                - 'solutions': List of solutions
                - 'processing_time': Time taken in seconds
                - 'output_file': Path to output document (if successful)
        """
        start_time = time.time()
        
        result = {
            "status": "success",
            "message": "Process completed",
            "equations_found": 0,
            "equations_solved": 0,
            "solutions": [],
            "processing_time": 0,
            "output_file": None
        }

        try:
            self.logger.info(f"Starting PDF equation solving pipeline")
            self.logger.info(f"Input: {pdf_path}")
            self.logger.info(f"Output: {output_path}")
            
            # Step 1: Read PDF
            self.logger.info("Step 1/4: Reading PDF...")
            pdf_text = self.pdf_reader.read_pdf(pdf_path)
            
            if not pdf_text or not pdf_text.strip():
                result["status"] = "error"
                result["message"] = "PDF contains no readable text"
                self.logger.error("PDF is empty or unreadable")
                return result
            
            self.logger.info(f"✓ PDF read successfully ({len(pdf_text)} characters)")
            
            # Step 2: Extract equations
            self.logger.info("Step 2/4: Extracting equations...")
            
            if include_context:
                equations_data = self.equation_extractor.extract_with_context(pdf_text)
                equations = [eq_data["equation"] for eq_data in equations_data]
            else:
                equations = self.equation_extractor.extract_equations(pdf_text)
            
            # Filter out invalid equations
            equations = [eq for eq in equations if self.equation_extractor.validate_equation(eq)]
            
            if not equations:
                result["status"] = "warning"
                result["message"] = "No valid equations found in PDF"
                result["equations_found"] = 0
                self.logger.warning("No valid equations found")
                
                # Still create output document with message
                self.doc_writer.create_solution_document(
                    output_path,
                    [],
                    [],
                    pdf_source=Path(pdf_path).name,
                    title="PDF Equation Solutions"
                )
                result["output_file"] = output_path
                return result
            
            result["equations_found"] = len(equations)
            self.logger.info(f"✓ Extracted {len(equations)} equations")
            
            # Step 3: Solve equations
            self.logger.info("Step 3/4: Solving equations...")
            
            if solve_as_system and len(equations) > 1:
                solutions = self._solve_as_system(equations)
                result["equations_solved"] = 1
                result["solutions"] = solutions
            else:
                solutions = self.solver.solve_multiple_equations(equations)
                solved_count = sum(1 for sol in solutions if sol["status"] == "success" and sol["solutions"])
                result["equations_solved"] = solved_count
                result["solutions"] = solutions
            
            self.logger.info(f"✓ Solved {result['equations_solved']} equation(s)")
            
            # Step 4: Write document
            self.logger.info("Step 4/4: Writing output document...")
            
            success = self.doc_writer.create_solution_document(
                output_path,
                equations,
                solutions if not solve_as_system or len(equations) == 1 else self._wrap_system_solutions(solutions, equations),
                pdf_source=Path(pdf_path).name,
                title="PDF Equation Solutions"
            )
            
            if not success:
                result["status"] = "error"
                result["message"] = "Failed to write output document"
                self.logger.error("Failed to create output document")
                return result
            
            result["output_file"] = output_path
            self.logger.info(f"✓ Document created: {output_path}")
            
            # Calculate processing time
            result["processing_time"] = time.time() - start_time
            
            # Final summary
            self.logger.info("=" * 50)
            self.logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            self.logger.info(f"  Equations extracted: {result['equations_found']}")
            self.logger.info(f"  Equations solved: {result['equations_solved']}")
            self.logger.info(f"  Processing time: {result['processing_time']:.2f}s")
            self.logger.info(f"  Output: {output_path}")
            self.logger.info("=" * 50)
            
            return result

        except FileNotFoundError as e:
            result["status"] = "error"
            result["message"] = f"File not found: {str(e)}"
            self.logger.error(f"File error: {str(e)}")
            return result

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Unexpected error: {str(e)}"
            self.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return result

        finally:
            result["processing_time"] = time.time() - start_time

    def solve_pdf_pages(
        self,
        pdf_path: str,
        page_numbers: List[int],
        output_path: str
    ) -> Dict[str, Any]:
        """
        Solve equations from specific pages only.
        
        Args:
            pdf_path: Path to PDF file
            page_numbers: List of page numbers to process (1-indexed)
            output_path: Path to output document
            
        Returns:
            Result dictionary
        """
        start_time = time.time()
        
        result = {
            "status": "success",
            "message": "Specific pages processed",
            "equations_found": 0,
            "equations_solved": 0,
            "solutions": [],
            "processing_time": 0,
            "output_file": None
        }

        try:
            self.logger.info(f"Processing pages: {page_numbers}")
            
            # Extract text from specific pages
            pdf_text = self.pdf_reader.extract_specific_pages(pdf_path, page_numbers)
            
            if not pdf_text:
                result["status"] = "error"
                result["message"] = "No text found on specified pages"
                return result
            
            # Extract and solve equations
            equations = self.equation_extractor.extract_equations(pdf_text)
            equations = [eq for eq in equations if self.equation_extractor.validate_equation(eq)]
            
            result["equations_found"] = len(equations)
            
            if equations:
                solutions = self.solver.solve_multiple_equations(equations)
                result["equations_solved"] = sum(1 for sol in solutions if sol["status"] == "success")
                result["solutions"] = solutions
                
                # Write document
                self.doc_writer.create_solution_document(
                    output_path,
                    equations,
                    solutions,
                    pdf_source=Path(pdf_path).name,
                    title=f"Equations from Pages {page_numbers}"
                )
                result["output_file"] = output_path
            
            result["processing_time"] = time.time() - start_time
            return result

        except Exception as e:
            result["status"] = "error"
            result["message"] = str(e)
            result["processing_time"] = time.time() - start_time
            self.logger.error(f"Error processing specific pages: {str(e)}")
            return result

    def extract_equations_only(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract equations from PDF without solving.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with 'equations' list and 'count'
        """
        try:
            self.logger.info(f"Extracting equations from: {pdf_path}")
            
            pdf_text = self.pdf_reader.read_pdf(pdf_path)
            equations = self.equation_extractor.extract_equations(pdf_text)
            equations = [eq for eq in equations if self.equation_extractor.validate_equation(eq)]
            
            self.logger.info(f"Extracted {len(equations)} equations")
            
            return {
                "status": "success",
                "equations": equations,
                "count": len(equations)
            }

        except Exception as e:
            self.logger.error(f"Error extracting equations: {str(e)}")
            return {
                "status": "error",
                "equations": [],
                "count": 0,
                "message": str(e)
            }

    def solve_equations_list(
        self,
        equations: List[str],
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Solve a list of equations (without PDF input).
        
        Args:
            equations: List of equation strings
            output_path: Optional path to save results to document
            
        Returns:
            Result dictionary
        """
        try:
            self.logger.info(f"Solving {len(equations)} equations")
            
            # Filter valid equations
            valid_equations = [
                eq for eq in equations
                if self.equation_extractor.validate_equation(eq)
            ]
            
            # Solve
            solutions = self.solver.solve_multiple_equations(valid_equations)
            
            result = {
                "status": "success",
                "equations": valid_equations,
                "solutions": solutions,
                "equations_solved": sum(1 for sol in solutions if sol["status"] == "success")
            }
            
            # Save to document if path provided
            if output_path:
                self.doc_writer.create_solution_document(
                    output_path,
                    valid_equations,
                    solutions,
                    title="Equation Solutions"
                )
                result["output_file"] = output_path
            
            return result

        except Exception as e:
            self.logger.error(f"Error solving equations: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "equations": [],
                "solutions": []
            }

    def _solve_as_system(self, equations: List[str]) -> Dict[str, Any]:
        """
        Solve equations as a system.
        
        Args:
            equations: List of equations
            
        Returns:
            System solution dictionary
        """
        return self.solver.solve_system(equations)

    def _wrap_system_solutions(
        self,
        system_solution: Dict[str, Any],
        equations: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Wrap system solution in format compatible with document writer.
        
        Args:
            system_solution: System solution dictionary
            equations: Original equations
            
        Returns:
            List of wrapped solutions
        """
        wrapped = []
        solutions = system_solution.get("solutions", [])
        
        if solutions:
            for sol in solutions:
                if isinstance(sol, dict):
                    wrapped.append({
                        "original": "System of Equations",
                        "solutions": [sol],
                        "status": "success",
                        "message": "",
                        "variables": list(sol.keys())
                    })
                else:
                    wrapped.append({
                        "original": "System of Equations",
                        "solutions": [str(sol)],
                        "status": "success",
                        "message": "",
                        "variables": []
                    })
        else:
            wrapped.append({
                "original": "System of Equations",
                "solutions": [],
                "status": "error",
                "message": system_solution.get("message", "No solutions found"),
                "variables": []
            })
        
        return wrapped


# Convenience function for simple usage
def solve_pdf(pdf_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
    """
    Simple function to solve equations from a PDF file.
    
    Args:
        pdf_path: Path to PDF file
        output_path: Path to output DOCX file
        **kwargs: Additional arguments for PDFEquationSolver
        
    Returns:
        Result dictionary
        
    Example:
        result = solve_pdf("equations.pdf", "solutions.docx")
        if result["status"] == "success":
            print(f"Found {result['equations_found']} equations")
            print(f"Solved {result['equations_solved']} equations")
    """
    solver = PDFEquationSolver(**kwargs)
    return solver.solve_pdf(pdf_path, output_path)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python pdf_solver.py <input.pdf> <output.docx>")
        print("\nExample:")
        print("  python pdf_solver.py equations.pdf solutions.docx")
        sys.exit(1)
    
    pdf_input = sys.argv[1]
    docx_output = sys.argv[2]
    
    result = solve_pdf(pdf_input, docx_output)
    
    print(f"\nResult: {result['status'].upper()}")
    print(f"Equations found: {result['equations_found']}")
    print(f"Equations solved: {result['equations_solved']}")
    print(f"Processing time: {result['processing_time']:.2f}s")
    
    if result['output_file']:
        print(f"Output saved to: {result['output_file']}")
    
    if result['message']:
        print(f"Message: {result['message']}")
