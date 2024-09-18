
# LLM4ModuleSum

This repository contains the code for the paper **"Commenting Higher-level Code Unit: Full Code, Reduced Code, or Hierarchical Code Summarization"**.

## Overview

The goal of this project is to explore different approaches to generating comments for higher-level code units such as modules or classes. This includes working with:
- **Full Code**: Using the complete code for generating summaries.
- **Reduced Code**: Leveraging compressed or abstracted versions of the code.
- **Hierarchical Code Summarization**: Creating summaries at different levels of granularity.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Functions and Scripts](#functions-and-scripts)
- [License](#license)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/wssun/LLM4ModuleSum.git
    ```
2. Navigate into the project directory:
    ```bash
    cd LLM4ModuleSum
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Data Processing

The scripts located at the root directory are primarily for data processing tasks, including:
- **caseslect_file.py**: Selects specific cases from the dataset.
- **compress.py**: Compresses the Java code by removing unnecessary comments and whitespace.
- **slicebycommunity.py**: Slices the code based on community detection.
- **slicebyfunction.py**: Slices the code by individual functions.
- **understand.py**: Analyzes and processes the code using the 'understand' tool.

### Comment Generation

The scripts used to interact with large language models (LLMs) for comment generation are organized in two levels:

#### File Level (Located in `file_level/`)
- **run_all.py**: Runs the full process for generating comments on all files.
- **run_compression.py**: Applies compression techniques before generating comments.
- **run_fuc.py**: Focuses on function-level summarization.
- **run_fuc_summary.py**: Generates summaries for each function within the code files.
- **run_point.py**: Extracts key points from the code for summarization.
- **run_point_summary.py**: Generates summaries based on key points extracted from the code.

#### Module Level (Located in `module_level/`)
- **find_package.py**: Identifies and processes package-level information in the code.
- **module_summary.py**: Generates summaries at the module level.
- **module_summary_prompt.py**: Provides prompts for LLMs to generate module-level summaries.

### Example Command
To process files and generate comments:
```bash
python file_level/run_all.py
```

## Project Structure

```
LLM4ModuleSum/
│
├── data/                              # Directory containing JSON and CSV files
├── file_level/                        # File-level comment generation scripts
│   ├── run_all.py
│   ├── run_compression.py
│   ├── run_fuc.py
│   ├── run_fuc_summary.py
│   ├── run_point.py
│   └── run_point_summary.py
├── module_level/                      # Module-level comment generation scripts
│   ├── find_package.py
│   ├── module_summary.py
│   └── module_summary_prompt.py
├── caseslect_file.py                  # Script to select specific cases
├── compress.py                        # Script to compress Java code
├── slicebycommunity.py                # Script to slice code by community
├── slicebyfunction.py                 # Script to slice code by function
├── understand.py                      # Code analysis script using 'understand' tool
├── requirements.txt                   # Required Python packages
└── README.md                          # Readme file
```

## Functions and Scripts

### Data Processing Scripts

- **caseslect_file.py**: Selects specific cases from the dataset.
- **compress.py**: Compresses the Java code by removing unnecessary comments and whitespace.
- **slicebycommunity.py**: Slices the code based on community detection.
- **slicebyfunction.py**: Slices the code by individual functions.
- **understand.py**: Analyzes and processes the code using the 'understand' tool.

### File-Level Comment Generation

- **run_all.py**: Runs the full process for generating comments on all files.
- **run_compression.py**: Applies compression techniques before generating comments.
- **run_fuc.py**: Focuses on function-level summarization.
- **run_fuc_summary.py**: Generates summaries for each function within the code files.
- **run_point.py**: Extracts key points from the code for summarization.
- **run_point_summary.py**: Generates summaries based on key points extracted from the code.

### Module-Level Comment Generation

- **find_package.py**: Identifies and processes module-level information in the code.
- **module_summary.py**: Generates summaries at the module level.
- **module_summary_prompt.py**: Provides prompts for LLMs to generate module-level summaries.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
