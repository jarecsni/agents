#!/usr/bin/env python3
"""
Example: Using notebook_extender to add a new section to any notebook

This shows how to reuse the tool for future challenges.
"""

from notebook_extender import extend_notebook, create_markdown_cell, create_code_cell

# Example 1: Add a data visualization section


def add_visualization_section(source_nb, output_nb):
    """Add a complete data visualization section to a notebook."""

    cells = [
        create_markdown_cell(
            "---\n\n"
            "# Data Visualization Section\n\n"
            "This section provides interactive visualizations of the data."
        ),
        create_code_cell(
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n\n"
            "# Set style\n"
            "sns.set_style('whitegrid')\n"
            "plt.rcParams['figure.figsize'] = (12, 6)"
        ),
        create_markdown_cell("## Distribution Analysis"),
        create_code_cell(
            "# Plot distributions\n"
            "fig, axes = plt.subplots(1, 2, figsize=(15, 5))\n"
            "df['column1'].hist(ax=axes[0], bins=30)\n"
            "df['column2'].hist(ax=axes[1], bins=30)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        create_markdown_cell("## Correlation Heatmap"),
        create_code_cell(
            "# Create correlation heatmap\n"
            "plt.figure(figsize=(10, 8))\n"
            "sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0)\n"
            "plt.title('Feature Correlations')\n"
            "plt.show()"
        )
    ]

    extend_notebook(source_nb, output_nb, cells)
    print(f"✅ Added visualization section to {output_nb}")


# Example 2: Add testing and validation
def add_testing_section(source_nb, output_nb):
    """Add unit tests and data validation to a notebook."""

    cells = [
        create_markdown_cell(
            "---\n\n"
            "# Testing & Validation\n\n"
            "Automated tests to ensure data quality and code correctness."
        ),
        create_code_cell(
            "import unittest\n"
            "from IPython.display import display, HTML\n\n"
            "class DataValidationTests(unittest.TestCase):\n"
            "    def test_no_nulls(self):\n"
            "        self.assertEqual(df.isnull().sum().sum(), 0)\n"
            "    \n"
            "    def test_positive_values(self):\n"
            "        self.assertTrue((df['amount'] > 0).all())\n"
            "    \n"
            "    def test_date_range(self):\n"
            "        self.assertTrue(df['date'].min() >= pd.Timestamp('2020-01-01'))"
        ),
        create_code_cell(
            "# Run tests\n"
            "suite = unittest.TestLoader().loadTestsFromTestCase(DataValidationTests)\n"
            "runner = unittest.TextTestRunner(verbosity=2)\n"
            "result = runner.run(suite)\n\n"
            "# Display results\n"
            "if result.wasSuccessful():\n"
            "    display(HTML('<h3 style=\"color:green\">✅ All tests passed!</h3>'))\n"
            "else:\n"
            "    display(HTML('<h3 style=\"color:red\">❌ Some tests failed</h3>'))"
        )
    ]

    extend_notebook(source_nb, output_nb, cells)
    print(f"✅ Added testing section to {output_nb}")


# Example 3: Add ML model evaluation
def add_ml_evaluation_section(source_nb, output_nb):
    """Add model evaluation metrics and visualizations."""

    cells = [
        create_markdown_cell(
            "---\n\n"
            "# Model Evaluation\n\n"
            "Comprehensive evaluation of model performance."
        ),
        create_code_cell(
            "from sklearn.metrics import classification_report, confusion_matrix\n"
            "import seaborn as sns\n\n"
            "# Generate predictions\n"
            "y_pred = model.predict(X_test)\n"
            "y_pred_proba = model.predict_proba(X_test)"
        ),
        create_markdown_cell("## Classification Report"),
        create_code_cell(
            "print(classification_report(y_test, y_pred))"
        ),
        create_markdown_cell("## Confusion Matrix"),
        create_code_cell(
            "cm = confusion_matrix(y_test, y_pred)\n"
            "plt.figure(figsize=(8, 6))\n"
            "sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')\n"
            "plt.title('Confusion Matrix')\n"
            "plt.ylabel('True Label')\n"
            "plt.xlabel('Predicted Label')\n"
            "plt.show()"
        ),
        create_markdown_cell("## ROC Curve"),
        create_code_cell(
            "from sklearn.metrics import roc_curve, auc\n\n"
            "fpr, tpr, _ = roc_curve(y_test, y_pred_proba[:, 1])\n"
            "roc_auc = auc(fpr, tpr)\n\n"
            "plt.figure(figsize=(8, 6))\n"
            "plt.plot(fpr, tpr, label=f'ROC curve (AUC = {roc_auc:.2f})')\n"
            "plt.plot([0, 1], [0, 1], 'k--')\n"
            "plt.xlabel('False Positive Rate')\n"
            "plt.ylabel('True Positive Rate')\n"
            "plt.title('ROC Curve')\n"
            "plt.legend()\n"
            "plt.show()"
        )
    ]

    extend_notebook(source_nb, output_nb, cells)
    print(f"✅ Added ML evaluation section to {output_nb}")


# Example 4: Add documentation and summary
def add_documentation_section(source_nb, output_nb, project_name="Project"):
    """Add comprehensive documentation to a notebook."""

    cells = [
        create_markdown_cell(
            "---\n\n"
            f"# {project_name} Documentation\n\n"
            "## Overview\n\n"
            "This notebook contains the complete analysis pipeline.\n\n"
            "## Key Findings\n\n"
            "- Finding 1: [Description]\n"
            "- Finding 2: [Description]\n"
            "- Finding 3: [Description]\n\n"
            "## Next Steps\n\n"
            "1. Step 1\n"
            "2. Step 2\n"
            "3. Step 3"
        ),
        create_code_cell(
            "# Generate summary statistics\n"
            "summary = {\n"
            "    'Total Records': len(df),\n"
            "    'Features': len(df.columns),\n"
            "    'Missing Values': df.isnull().sum().sum(),\n"
            "    'Memory Usage': f\"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\"\n"
            "}\n\n"
            "for key, value in summary.items():\n"
            "    print(f'{key}: {value}')"
        ),
        create_markdown_cell(
            "## References\n\n"
            "- [Documentation](https://example.com/docs)\n"
            "- [GitHub Repository](https://github.com/example/repo)\n"
            "- [Related Paper](https://example.com/paper)"
        )
    ]

    extend_notebook(source_nb, output_nb, cells)
    print(f"✅ Added documentation section to {output_nb}")


if __name__ == "__main__":
    print("📓 Notebook Extender Examples\n")
    print("These functions show how to reuse the tool for different purposes:\n")
    print("1. add_visualization_section() - Add data viz")
    print("2. add_testing_section() - Add unit tests")
    print("3. add_ml_evaluation_section() - Add ML metrics")
    print("4. add_documentation_section() - Add docs\n")
    print("Usage:")
    print("  from example_extend_notebook import add_visualization_section")
    print("  add_visualization_section('input.ipynb', 'output.ipynb')")
