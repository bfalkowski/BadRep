# Python Calculator - Baseline Project

A simple calculator implementation in Python that serves as a baseline project for bug injection testing in ReviewLab.

## Features

- Basic arithmetic operations (add, subtract, multiply, divide)
- Power and square root calculations
- Factorial computation
- Modulo operations
- Absolute value and rounding
- Comprehensive error handling
- Full unit test coverage with pytest

## Requirements

- Python 3.8 or higher
- pip for package management

## Installation

```bash
# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Building and Testing

```bash
# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_calculator.py

# Run specific test method
pytest tests/test_calculator.py::TestCalculator::test_add_positive_numbers
```

## Project Structure

```
src/
├── calculator.py              # Main calculator class
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── tests/
    └── test_calculator.py    # Unit tests
```

## Test Coverage

The project includes comprehensive tests covering:
- All arithmetic operations
- Edge cases (zero, negative numbers, large numbers)
- Error conditions (division by zero, negative square root)
- Type conversions and return types
- Integration tests with complex calculations
- Exception handling verification

## Usage Example

```python
from src.calculator import Calculator

calc = Calculator()

# Basic operations
sum_result = calc.add(5, 3)        # 8.0
product = calc.multiply(4, 2.5)    # 10.0
quotient = calc.divide(10, 2)      # 5.0

# Advanced operations
power = calc.power(2, 8)           # 256.0
sqrt = calc.sqrt(16)               # 4.0
factorial = calc.factorial(5)      # 120
modulo = calc.modulo(17, 5)        # 2.0
absolute = calc.absolute(-7)       # 7.0
rounded = calc.round_number(3.14159, 2)  # 3.14
```

## Error Handling

The calculator properly handles error conditions:
- Division by zero raises `ZeroDivisionError`
- Negative square root raises `ValueError`
- Negative factorial raises `ValueError`
- Modulo by zero raises `ZeroDivisionError`

## Development

This project is designed to be a stable baseline for testing bug injection tools. All tests should pass before any modifications are made for bug injection testing.

## Running the Application

```bash
# Run the calculator as a standalone application
python src/calculator.py
```

This will output:
```
ReviewLab Calculator - Baseline Project
=====================================
5 + 3 = 8.0
10 - 4 = 6.0
6 * 7 = 42.0
15 / 3 = 5.0
2^8 = 256.0
√16 = 4.0
5! = 120
17 % 5 = 2.0
|-7| = 7.0
3.14159 rounded to 2 decimals = 3.14
```

## Code Quality

The project includes optional code quality tools:
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/
```

## License

MIT License - see LICENSE file for details.
