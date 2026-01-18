"""
File Upload Handler for Learning Agent Web App

Handles file uploads from users, stores them temporarily, and processes them
for learning material extraction.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)

class FileUploadHandler:
    """Handle file uploads for the learning agent web app."""
    
    def __init__(self):
        """Initialize file upload handler."""
        from .document_processor import get_document_processor
        self.doc_processor = get_document_processor()
        self.upload_dir = self.doc_processor.temp_dir
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        self.allowed_extensions = {'.pdf', '.docx', '.md', '.txt'}
    
    def validate_file(self, file_path: str, file_size: int = None) -> Dict[str, any]:
        """
        Validate uploaded file.
        
        Args:
            file_path: Path to uploaded file
            file_size: Size of file in bytes (optional)
            
        Returns:
            Validation result with status and message
        """
        file_path = Path(file_path)
        
        # Check extension
        if file_path.suffix.lower() not in self.allowed_extensions:
            return {
                "valid": False,
                "error": f"Unsupported file type: {file_path.suffix}. "
                        f"Allowed: {', '.join(self.allowed_extensions)}"
            }
        
        # Check file exists
        if not file_path.exists():
            return {
                "valid": False,
                "error": "File does not exist"
            }
        
        # Check file size
        if file_size is None:
            file_size = file_path.stat().st_size
        
        if file_size > self.max_file_size:
            return {
                "valid": False,
                "error": f"File too large: {file_size / (1024*1024):.1f}MB. "
                        f"Maximum: {self.max_file_size / (1024*1024):.0f}MB"
            }
        
        if file_size == 0:
            return {
                "valid": False,
                "error": "File is empty"
            }
        
        return {
            "valid": True,
            "file_type": file_path.suffix[1:],  # Remove dot
            "file_size": file_size,
            "file_name": file_path.name
        }
    
    def handle_upload(self, file_path: str = None, file_content: bytes = None, 
                     file_name: str = None) -> Dict:
        """
        Handle file upload and return processed result.
        
        Args:
            file_path: Path to existing file (if already saved)
            file_content: Raw file content bytes (if uploading)
            file_name: Original filename (if uploading)
            
        Returns:
            Upload result with processed content
        """
        try:
            # Case 1: File already saved locally
            if file_path:
                validation = self.validate_file(file_path)
                if not validation['valid']:
                    return {
                        "success": False,
                        "error": validation['error']
                    }
                
                saved_path = file_path
            
            # Case 2: Upload new file
            elif file_content and file_name:
                # Validate size
                file_size = len(file_content)
                if file_size > self.max_file_size:
                    return {
                        "success": False,
                        "error": f"File too large: {file_size / (1024*1024):.1f}MB"
                    }
                
                # Save file
                saved_path = self.doc_processor.save_uploaded_file(file_content, file_name)
                
                # Validate saved file
                validation = self.validate_file(saved_path, file_size)
                if not validation['valid']:
                    return {
                        "success": False,
                        "error": validation['error']
                    }
            
            else:
                return {
                    "success": False,
                    "error": "Must provide either file_path or (file_content + file_name)"
                }
            
            # Process document
            logger.info(f"📄 Processing uploaded file: {Path(saved_path).name}")
            result = self.doc_processor.process_document(saved_path)
            
            if result['success']:
                return {
                    "success": True,
                    "file_path": saved_path,
                    "file_name": result['file_name'],
                    "file_type": result['file_type'],
                    "content": result['content'],
                    "content_length": result['content_length'],
                    "message": f"Successfully processed {result['file_name']}"
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Failed to process document')
                }
                
        except Exception as e:
            logger.error(f"❌ Error handling upload: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_multiple_uploads(self, files: List[Dict]) -> Dict:
        """
        Handle multiple file uploads.
        
        Args:
            files: List of file dicts with either 'path' or ('content', 'name')
            
        Returns:
            Summary of upload results
        """
        results = []
        successful = 0
        failed = 0
        
        for file_data in files:
            if 'path' in file_data:
                result = self.handle_upload(file_path=file_data['path'])
            else:
                result = self.handle_upload(
                    file_content=file_data.get('content'),
                    file_name=file_data.get('name')
                )
            
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
        
        return {
            "total": len(files),
            "successful": successful,
            "failed": failed,
            "results": results,
            "uploaded_paths": [r['file_path'] for r in results if r.get('success')]
        }
    
    def get_upload_instructions(self) -> str:
        """Get user-friendly upload instructions."""
        return f"""
📎 FILE UPLOAD INSTRUCTIONS

Supported Formats:
  • PDF (.pdf) - Portable Document Format
  • Word (.docx) - Microsoft Word documents
  • Markdown (.md) - Markdown files
  • Text (.txt) - Plain text files

File Limits:
  • Maximum size: {self.max_file_size / (1024*1024):.0f}MB per file
  • Multiple files allowed

Tips:
  • Ensure files contain relevant learning materials
  • Clear, well-formatted content works best
  • Files are stored temporarily and auto-deleted after 24 hours
"""

    def prompt_for_file_upload(self) -> Optional[List[str]]:
        """
        Interactive prompt for file upload (CLI version).
        
        Returns:
            List of uploaded file paths or None
        """
        print("\n" + "="*70)
        print("📎 UPLOAD LEARNING MATERIALS (OPTIONAL)")
        print("="*70)
        print(self.get_upload_instructions())
        
        while True:
            choice = input("\nDo you have learning materials to upload? (y/n): ").strip().lower()
            
            if choice == 'n':
                logger.info("User chose not to upload materials")
                return None
            
            if choice == 'y':
                break
            
            print("❌ Please enter 'y' for yes or 'n' for no")
        
        # Get file paths
        print("\n📁 Enter file paths (one per line, empty line to finish):")
        file_paths = []
        
        while True:
            path = input(f"File {len(file_paths) + 1}: ").strip()
            
            if not path:
                break
            
            # Validate path exists
            if not Path(path).exists():
                print(f"❌ File not found: {path}")
                continue
            
            # Validate file
            validation = self.validate_file(path)
            if not validation['valid']:
                print(f"❌ {validation['error']}")
                continue
            
            file_paths.append(path)
            print(f"✅ Added: {Path(path).name}")
        
        if file_paths:
            logger.info(f"📎 User provided {len(file_paths)} files")
            return file_paths
        else:
            logger.info("No files uploaded")
            return None

# Global instance
_upload_handler = None

def get_upload_handler() -> FileUploadHandler:
    """Get or create global upload handler instance."""
    global _upload_handler
    if _upload_handler is None:
        _upload_handler = FileUploadHandler()
    return _upload_handler
