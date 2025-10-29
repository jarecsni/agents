# Notebook Extender Tool

A reusable utility for safely adding cells to Jupyter notebooks without breaking JSON structure.

## Why This Tool?

Jupyter notebooks are JSON files. Manually editing them or using simple text append can break the structure. This tool:
- ✅ Reads notebooks as proper JSON
- ✅ Adds cells programmatically
- ✅ Validates structure
- ✅ Guarantees valid output

## Installation

No installation needed! Just use the Python file:

```bash
python 2_openai/notebook_extender.py --help
```

## Usage

### Option 1: Original Use Case (Email Reply Notebook)

```bash
python 2_openai/notebook_extender.py --create-reply-notebook
```

This creates `2_lab2_with_replies.ipynb` with email reply functionality.

### Option 2: Extend Any Notebook

```bash
python 2_openai/notebook_extender.py source.ipynb output.ipynb --cells new_cells.json
```

Where `new_cells.json` contains:

```json
[
  {
    "cell_type": "markdown",
    "metadata": {},
    "source": ["# My New Section\n", "\n", "Some description"]
  },
  {
    "cell_type": "code",
    "execution_count": null,
    "metadata": {},
    "outputs": [],
    "source": ["print('Hello World')"]
  }
]
```

### Option 3: Use as Python Module

```python
from notebook_extender import extend_notebook, create_code_cell, create_markdown_cell

# Create cells
cells = [
    create_markdown_cell("# New Section\n\nDescription here"),
    create_code_cell("import pandas as pd\ndf = pd.DataFrame()"),
    create_code_cell("print(df.head())")
]

# Extend notebook
extend_notebook(
    source_path="original.ipynb",
    output_path="extended.ipynb",
    new_cells=cells
)
```

## API Reference

### `extend_notebook(source_path, output_path, new_cells, validate=True)`

Extend a Jupyter notebook by adding new cells.

**Parameters:**
- `source_path` (str): Path to source notebook
- `output_path` (str): Path to output notebook
- `new_cells` (List[Dict]): List of cell dictionaries to add
- `validate` (bool): Whether to validate notebook structure (default: True)

**Returns:**
- Dict: The modified notebook dictionary

**Raises:**
- `FileNotFoundError`: If source notebook doesn't exist
- `json.JSONDecodeError`: If source notebook is invalid JSON
- `ValueError`: If notebook structure is invalid

### `create_code_cell(source, execution_count=None)`

Create a properly formatted code cell.

**Parameters:**
- `source` (str or List[str]): Python code
- `execution_count` (int, optional): Execution count (None for unexecuted)

**Returns:**
- Dict: Jupyter code cell dictionary

**Example:**
```python
cell = create_code_cell("""
import numpy as np
arr = np.array([1, 2, 3])
print(arr)
""")
```

### `create_markdown_cell(source)`

Create a properly formatted markdown cell.

**Parameters:**
- `source` (str or List[str]): Markdown text

**Returns:**
- Dict: Jupyter markdown cell dictionary

**Example:**
```python
cell = create_markdown_cell("""
# Data Analysis

This section covers:
- Data loading
- Preprocessing
- Visualization
""")
```

### `load_cells_from_json(cells_file)`

Load cell definitions from a JSON file.

**Parameters:**
- `cells_file` (str): Path to JSON file

**Returns:**
- List[Dict]: List of cell dictionaries

## Examples

### Example 1: Add Analysis Section to Existing Notebook

```python
from notebook_extender import extend_notebook, create_markdown_cell, create_code_cell

cells = [
    create_markdown_cell("## Data Analysis\n\nPerforming exploratory analysis..."),
    create_code_cell("df.describe()"),
    create_code_cell("df.plot()"),
    create_markdown_cell("### Insights\n\nKey findings from the analysis...")
]

extend_notebook("data_notebook.ipynb", "data_notebook_with_analysis.ipynb", cells)
```

### Example 2: Add Testing Section

```python
from notebook_extender import extend_notebook, create_code_cell

test_cells = [
    create_code_cell("# Run tests\nimport pytest\npytest.main(['-v'])"),
    create_code_cell("# Check coverage\n!coverage report")
]

extend_notebook("main.ipynb", "main_with_tests.ipynb", test_cells)
```

### Example 3: Batch Process Multiple Notebooks

```python
from pathlib import Path
from notebook_extender import extend_notebook, create_markdown_cell

footer = [create_markdown_cell("---\n\n*Generated automatically*")]

for nb_path in Path("notebooks").glob("*.ipynb"):
    output_path = Path("notebooks_with_footer") / nb_path.name
    extend_notebook(str(nb_path), str(output_path), footer)
```

## Cell Structure Reference

### Code Cell Structure
```json
{
  "cell_type": "code",
  "execution_count": null,
  "metadata": {},
  "outputs": [],
  "source": [
    "import pandas as pd\n",
    "df = pd.DataFrame()"
  ]
}
```

### Markdown Cell Structure
```json
{
  "cell_type": "markdown",
  "metadata": {},
  "source": [
    "# Title\n",
    "\n",
    "Description text"
  ]
}
```

## Tips

1. **Always validate first**: Use `validate=True` (default) to catch structure issues
2. **Test with copies**: Test on notebook copies before modifying originals
3. **Use helper functions**: `create_code_cell()` and `create_markdown_cell()` handle formatting
4. **Check output**: Open the generated notebook in Jupyter to verify
5. **Version control**: Commit notebooks before extending them

## Troubleshooting

### "Invalid notebook: missing 'cells' key"
The source file isn't a valid Jupyter notebook. Check it opens in Jupyter first.

### "FileNotFoundError"
Check the source path is correct and the file exists.

### "JSONDecodeError"
The source notebook has invalid JSON. Try opening it in Jupyter to see the error.

### Cells not appearing correctly
Check your cell structure matches the format above. Use helper functions to avoid errors.

## Future Enhancements

Potential additions:
- Insert cells at specific positions (not just append)
- Remove/modify existing cells
- Merge multiple notebooks
- Extract cells from notebooks
- Convert between notebook formats
- Batch operations on cell metadata

## Contributing

This tool was created to solve the email reply notebook challenge. Feel free to extend it for your use cases!

## License

Free to use and modify for your projects.

---

**Created for the AI Agentic Engineering course** 🚀
