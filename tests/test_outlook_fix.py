import sys
import os
import traceback
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add root to path
sys.path.append(os.getcwd())

# Mock ChatMistralAI BEFORE importing SynthesizerAgent if possible, 
# or patch it where it is used.
def test_synthesizer_fallback():
    mock_llm_instance = MagicMock()
    mock_response = MagicMock()
    # JSON missing outlook_30_days
    mock_response.content = '{"report_title": "Test Report", "executive_summary": "Summary", "key_developments": [], "competitive_comparison": {}, "swot_summary": [], "weak_signals": [], "strategic_recommendations": [], "data_sources_count": 0, "companies_analyzed": []}'
    mock_llm_instance.invoke.return_value = mock_response
    
    with patch('langchain_mistralai.ChatMistralAI', return_value=mock_llm_instance):
        from agents.synthesizer_agent import SynthesizerAgent
        agent = SynthesizerAgent()
        
        analyses = [
            {"company": "Maaza", "outlook": "Maaza will expand distribution."},
            {"company": "Frooti", "outlook": "Frooti will launch new flavors."}
        ]
        
        print("Running synthesize...")
        # Reduce sleep for test
        with patch('time.sleep', return_value=None):
            report = agent.synthesize(analyses)
        
        outlook = report.get('outlook_30_days')
        print(f"Report Outlook: {outlook}")
        
        if not outlook:
            print("FAILURE: Outlook is missing from report")
            sys.exit(1)
            
        assert "Maaza will expand distribution." in outlook
        assert "Frooti will launch new flavors." in outlook
        print("Test passed: Synthesizer correctly created outlook from individual company data.")

if __name__ == "__main__":
    try:
        test_synthesizer_fallback()
    except Exception as e:
        print(f"Test failed: {e}")
        traceback.print_exc()
        sys.exit(1)
