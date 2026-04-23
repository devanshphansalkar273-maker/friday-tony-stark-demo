# System tools init
__all__ = [
    'actions',
    'files',
    'pdf_solver',
    'pdf_reader',
    'equation_extractor',
    'solver',
    'doc_writer'
]

# Import main components for easy access
try:
    from friday.system.pdf_solver import PDFEquationSolver, solve_pdf
    from friday.system.pdf_reader import PDFReader
    from friday.system.equation_extractor import EquationExtractor
    from friday.system.solver import EquationSolver
    from friday.system.doc_writer import DocumentWriter
except ImportError:
    # Dependencies might not be installed yet
    pass

