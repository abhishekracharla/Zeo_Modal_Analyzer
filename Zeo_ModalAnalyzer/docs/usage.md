# Usage of Zeo Modal Analyzer

## Overview
The Zeo Modal Analyzer is a tool designed for performing finite element method (FEM) analysis and visualizing the results. This document provides guidance on how to effectively use the application.

## Getting Started
1. **Installation**: Before using the application, ensure that you have followed the installation instructions provided in `docs/installation.md`.

2. **Running the Application**: 
   - Navigate to the directory where the application is located.
   - Execute the main script using Python:
     ```
     python src/main.py
     ```

## Using the Application
### Performing FEM Analysis
1. **Input Data**: Prepare your input data according to the format specified in `examples/sample_analysis.txt`. This file serves as a template for the required input structure.

2. **Executing Analysis**:
   - Once the application is running, you can load your input data through the GUI.
   - Follow the prompts to set up the analysis parameters.

3. **Viewing Results**:
   - After the analysis is complete, results will be displayed in the GUI.
   - You can visualize the results using the built-in visualization tools.

### Example Usage
- Load the sample analysis file provided in the `examples` directory to see how the application processes input data.
- Modify the sample file to experiment with different parameters and observe how the results change.

## Tips
- Ensure that all required dependencies are installed as listed in `requirements.txt`.
- Refer to `docs/theory.md` for a deeper understanding of the FEM methodologies used in the application.

## Troubleshooting
If you encounter issues while using the application, check the following:
- Ensure that your input data is correctly formatted.
- Review the installation steps to confirm that all dependencies are properly installed.
- Consult the `tests` directory for unit tests that can help verify the functionality of specific components.