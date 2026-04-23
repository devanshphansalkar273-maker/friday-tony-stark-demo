"""
PDF Reader Module
Handles reading and extracting text from PDF files using PyPDF2.
"""

import logging
from pathlib import Path
from typing import Optional

try:
    import PyPDF2
except ImportError:
    raise ImportError("PyPDF2 is required. Install it with: pip install PyPDF2")


logger = logging.getLogger(__name__)


class PDFReader:
    """Extract text content from PDF files."""

    def __init__(self, log_level: int = logging.INFO):
        """
        Initialize PDFReader.
        
        Args:
            log_level: Logging level for the reader
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)

    def read_pdf(self, pdf_path: str) -> str:
        """
        Read and extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content from the PDF
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the PDF is encrypted or cannot be read
            Exception: For other PDF reading errors
        """
        pdf_file = Path(pdf_path)

        # Validate file exists
        if not pdf_file.exists():
            error_msg = f"PDF file not found: {pdf_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Validate file extension
        if pdf_file.suffix.lower() != ".pdf":
            error_msg = f"File must be a PDF. Got: {pdf_file.suffix}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            self.logger.info(f"Reading PDF: {pdf_path}")
            
            with open(pdf_file, "rb") as pdf_obj:
                pdf_reader = PyPDF2.PdfReader(pdf_obj)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    error_msg = "PDF is encrypted. Cannot extract text."
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)

                # Extract text from all pages
                text_content = []
                num_pages = len(pdf_reader.pages)
                
                self.logger.info(f"Extracting text from {num_pages} pages")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                            self.logger.debug(f"Extracted text from page {page_num}")
                    except Exception as e:
                        self.logger.warning(f"Error extracting text from page {page_num}: {e}")
                        # Continue with other pages instead of failing completely

            combined_text = "\n---PAGE BREAK---\n".join(text_content)
            self.logger.info(f"Successfully extracted text from PDF ({len(combined_text)} characters)")
            return combined_text

        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Error reading PDF: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg) from e

    def read_pdf_with_metadata(self, pdf_path: str) -> dict:
        """
        Read PDF and extract both text and metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing 'text', 'num_pages', 'title', 'author', etc.
        """
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            with open(pdf_file, "rb") as pdf_obj:
                pdf_reader = PyPDF2.PdfReader(pdf_obj)
                
                # Extract metadata
                metadata = pdf_reader.metadata
                
                result = {
                    "text": self.read_pdf(pdf_path),
                    "num_pages": len(pdf_reader.pages),
                    "title": metadata.title if metadata and metadata.title else "Unknown",
                    "author": metadata.author if metadata and metadata.author else "Unknown",
                    "subject": metadata.subject if metadata and metadata.subject else "",
                }
                
                self.logger.info(f"Extracted metadata: {result['num_pages']} pages, Title: {result['title']}")
                return result

        except Exception as e:
            error_msg = f"Error reading PDF with metadata: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg) from e

    def extract_specific_pages(self, pdf_path: str, page_numbers: list) -> str:
        """
        Extract text from specific pages only.
        
        Args:
            pdf_path: Path to the PDF file
            page_numbers: List of page numbers to extract (1-indexed)
            
        Returns:
            Combined text from specified pages
        """
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            with open(pdf_file, "rb") as pdf_obj:
                pdf_reader = PyPDF2.PdfReader(pdf_obj)
                text_content = []

                for page_num in page_numbers:
                    if 0 < page_num <= len(pdf_reader.pages):
                        page = pdf_reader.pages[page_num - 1]
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
                            self.logger.debug(f"Extracted text from page {page_num}")
                    else:
                        self.logger.warning(f"Page {page_num} out of range (1-{len(pdf_reader.pages)})")

            return "\n---PAGE BREAK---\n".join(text_content)

        except Exception as e:
            error_msg = f"Error extracting specific pages: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg) from e
