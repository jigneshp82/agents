#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from financial_researcher.crew import FinancialResearcher

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")



def run():
    """
    Run the crew.
    """
    compay = input("Enter a Company Name for financail research: ")
    inputs = {
        'company': compay,
    }
    
    try:
        res = FinancialResearcher().crew().kickoff(inputs=inputs)
        print (res.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


