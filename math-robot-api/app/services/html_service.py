import logging
import os
from pathlib import Path
from fastapi import HTTPException
from app.models.file_model import File
from app.schemas.pipeline_schema import ProblemResult
from app.config import config

logger = logging.getLogger(__name__)

class HtmlService:
    """
    Service for generating and saving HTML files with images and results.
    """

    @staticmethod
    async def save_problem(file: File, problem_results: list[ProblemResult]) -> File:
        """
        Generate and save an HTML file with the original image and problem results.
        Overwrites index.html on each request.
        
        Args:
            file: Original image file
            problem_results: List of problem recognition results
            
        Returns:
            The original file (unchanged)
        """
        try:
            # Create public directory if it doesn't exist
            public_path = Path(config.PUBLIC_FOLDER_PATH)
            public_path.mkdir(parents=True, exist_ok=True)
            
            # Save the original image to public folder
            image_bytes = await file.to_bytes()
            image_filename = "problem_image.png"
            image_path = public_path / image_filename
            
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            logger.info(f"Saved image to: {image_path}")
            
            # Generate HTML content
            html_content = HtmlService._generate_html(
                image_filename=image_filename,
                problem_results=problem_results
            )
            
            # Save HTML file
            html_path = public_path / "index.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Saved HTML to: {html_path}")
            
            return file
            
        except Exception as e:
            logger.error(f"HTML saving error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"HTML saving error: {str(e)}")
    
    @staticmethod
    def _generate_html(image_filename: str, problem_results: list[ProblemResult]) -> str:
        """
        Generate HTML content with image and results.
        
        Args:
            image_filename: Name of the saved image file
            problem_results: List of problem results
            
        Returns:
            HTML string
        """
        # Build results section
        results_html = ""
        for result in problem_results:
            results_html += f"""
            <div class="result-card">
                <div class="result-header">
                    <h3>Problem {result.problem_id}</h3>
                    <span class="status {'success' if result.success else 'error'}">
                        {'✓' if result.success else '✗'}
                    </span>
                </div>
                
                <div class="result-content">
                    <div class="result-row">
                        <span class="label">Original LaTeX:</span>
                        <code>{result.latex_raw or 'N/A'}</code>
                    </div>
                    
                    <div class="result-row">
                        <span class="label">Filtered LaTeX:</span>
                        <code>{result.latex_filtered or 'N/A'}</code>
                    </div>
                    
                    <div class="result-row">
                        <span class="label">Wolfram Result:</span>
                        <span>{result.result_wolfram or 'N/A'}</span>
                    </div>
                    
                    <div class="result-row">
                        <span class="label">Final Result:</span>
                        <span class="final-result">{result.result_filtered or 'N/A'}</span>
                    </div>
                    
                    {f'<div class="error-message">Error: {result.error}</div>' if result.error else ''}
                </div>
            </div>
            """
        
        # If no results, show a message
        if not results_html:
            results_html = """
            <div class="no-results">
                <p>No problems were detected or processed.</p>
            </div>
            """
        
        # Complete HTML template
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Math Problem Recognition Results</title>
            <style>
                /* Reset and base styles */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f5f5f5;
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                
                .container {{
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    padding: 30px;
                    margin-top: 20px;
                }}
                
                header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #eaeaea;
                }}
                
                h1 {{
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                
                .subtitle {{
                    color: #7f8c8d;
                    font-size: 1.1em;
                }}
                
                .image-section {{
                    margin-bottom: 40px;
                }}
                
                .image-container {{
                    background-color: #f8f9fa;
                    border: 1px solid #eaeaea;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                }}
                
                .image-container img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 6px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                }}
                
                .image-caption {{
                    margin-top: 10px;
                    color: #7f8c8d;
                    font-style: italic;
                }}
                
                .results-section {{
                    margin-top: 30px;
                }}
                
                .section-title {{
                    color: #2c3e50;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #eaeaea;
                }}
                
                .result-card {{
                    background-color: #f8f9fa;
                    border: 1px solid #eaeaea;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    transition: transform 0.2s, box-shadow 0.2s;
                }}
                
                .result-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                }}
                
                .result-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #eaeaea;
                }}
                
                .result-header h3 {{
                    color: #2c3e50;
                    font-size: 1.2em;
                }}
                
                .status {{
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                }}
                
                .status.success {{
                    background-color: #d4edda;
                    color: #155724;
                }}
                
                .status.error {{
                    background-color: #f8d7da;
                    color: #721c24;
                }}
                
                .result-content {{
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }}
                
                .result-row {{
                    display: flex;
                    flex-wrap: wrap;
                    align-items: flex-start;
                    gap: 10px;
                    padding: 8px 0;
                    border-bottom: 1px dashed #eaeaea;
                }}
                
                .result-row:last-child {{
                    border-bottom: none;
                }}
                
                .label {{
                    font-weight: 600;
                    color: #495057;
                    min-width: 150px;
                }}
                
                .result-row code {{
                    background-color: #e9ecef;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                    color: #c7254e;
                    flex: 1;
                    overflow-wrap: break-word;
                }}
                
                .final-result {{
                    font-weight: bold;
                    color: #28a745;
                    font-size: 1.1em;
                }}
                
                .error-message {{
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 10px;
                    border-radius: 4px;
                    margin-top: 10px;
                    border-left: 4px solid #dc3545;
                }}
                
                .no-results {{
                    text-align: center;
                    padding: 40px;
                    background-color: #f8f9fa;
                    border: 2px dashed #dee2e6;
                    border-radius: 8px;
                    color: #6c757d;
                }}
                
                footer {{
                    margin-top: 40px;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 0.9em;
                    padding-top: 20px;
                    border-top: 1px solid #eaeaea;
                }}
                
                /* Responsive design */
                @media (max-width: 768px) {{
                    .container {{
                        padding: 15px;
                    }}
                    
                    .result-row {{
                        flex-direction: column;
                        gap: 5px;
                    }}
                    
                    .label {{
                        min-width: auto;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>Math Problem Recognition Results</h1>
                    <p class="subtitle">Image analysis and LaTeX conversion results</p>
                </header>

                <section class="results-section">
                    <h2 class="section-title">Recognition Results</h2>
                    <div class="results-container">
                        {results_html}
                    </div>
                </section>
                
                <section class="image-section">
                    <h2 class="section-title">Original Image</h2>
                    <div class="image-container">
                        <img src="{image_filename}" alt="Uploaded math problem">
                        <p class="image-caption">Uploaded image containing mathematical expressions</p>
                    </div>
                </section>
                
                <footer>
                    <p>Generated by Math Problem Recognition Pipeline</p>
                    <p>Results are generated through OCR, LaTeX conversion, and computational verification</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        return html