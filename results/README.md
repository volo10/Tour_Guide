# Results Directory

This directory contains output files from Tour Guide experiments and analyses.

## Structure

```
results/
├── README.md                    # This file
├── parameter_analysis.json      # Parameter sensitivity analysis results
└── experiment_logs/             # Detailed experiment logs
```

## Output Files

### parameter_analysis.json
Contains results from parameter sensitivity experiments including:
- Junction interval impact analysis
- Agent timeout impact analysis
- Winner distribution statistics

## Notes

- Large result files should be added to `.gitignore`
- Results should include timestamps for reproducibility
- Raw experiment data should be preserved for verification
