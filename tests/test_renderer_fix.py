import sys
import os
from pathlib import Path

# Add root to path
sys.path.append(os.getcwd())

from reports.pdf_renderer import PDFRenderer
from datetime import datetime

def test_renderer_fallback():
    renderer = PDFRenderer()
    
    # Report without outlook_30_days
    report_data = {
        "report_title": "Test Renderer Report",
        "executive_summary": "Summary of events.",
        "key_developments": [],
        "competitive_comparison": {},
        "swot_summary": [],
        "weak_signals": [],
        "strategic_recommendations": [],
        "data_sources_count": 0,
        "companies_analyzed": ["Maaza"],
        "generated_at": datetime.utcnow().isoformat()
    }
    
    analyses = [{"company": "Maaza", "swot": {"strengths": ["Strong distribution"]}}]
    
    print("Rendering PDF...")
    try:
        path = renderer.render(report_data, analyses=analyses)
        print(f"PDF rendered successfully to: {path}")
        # Clean up
        if path.exists():
            print(f"Verified: PDF exists.")
            # os.remove(path) # Keep for manual inspection if needed
        else:
            print("FAILURE: PDF file was not created.")
            sys.exit(1)
    except Exception as e:
        print(f"FAILURE during render: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_renderer_fallback()
