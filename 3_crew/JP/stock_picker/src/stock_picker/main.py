#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from stock_picker.crew import StockPicker

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """

    sector = input("Please enter Sector for which you would like to pick stocks : ")
    inputs = {
        'sector': sector,
    }
    
    try:
        res = StockPicker().crew().kickoff(inputs=inputs)
        print (res.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


