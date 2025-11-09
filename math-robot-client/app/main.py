#!/usr/bin/env python3
"""
Math Robot Client - Main Entry Point
Simple client for mathematical problem processing pipeline
"""

import sys
from services.pipeline_service import PipelineService

def main():
    """Main application entry point"""
    
    try:
        PipelineService.run_complete_pipeline()
            
    except KeyboardInterrupt:
        print("\n⏹️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()