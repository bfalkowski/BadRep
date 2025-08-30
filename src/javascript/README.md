# JavaScript Calculator - Baseline Project

A simple calculator implementation in JavaScript that serves as a baseline project for bug injection testing in ReviewLab.

## Features

- Basic arithmetic operations (add, subtract, multiply, divide)
- Power and square root calculations
- Factorial computation
- Modulo operations
- Absolute value and rounding
- Greatest common divisor (GCD) and least common multiple (LCM)
- Prime number checking
- Comprehensive error handling
- Full unit test coverage with Jest

## Requirements

- Node.js 16.0 or higher
- npm for package management

## Installation

```bash
# Install dependencies
npm install
```

## Building and Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch

# Run tests with verbose output
npm run test:verbose

# Run the application
npm start
```

## Project Structure

```
src/
├── calculator.js              # Main calculator class
├── package.json              # Node.js dependencies and scripts
├── README.md                 # This file
└── tests/
    └── calculator.test.js    # Unit tests
```

## Test Coverage

The project includes comprehensive tests covering:
- All arithmetic operations
- Edge cases (zero, negative numbers, large numbers)
- Error conditions (division by zero, negative square root)
- Type conversions and input handling
- Integration tests with complex calculations
- Exception handling verification
- Mathematical operations (GCD, LCM, prime checking)

## Usage Example

```javascript
const Calculator = require('./src/calculator');

const calc = new Calculator();

// Basic operations
const sum = calc.add(5, 3);        // 8
const product = calc.multiply(4, 2.5); // 10
const quotient = calc.divide(10, 2);   // 5

// Advanced operations
const power = calc.power(2, 8);        // 256
const sqrt = calc.sqrt(16);            // 4
const factorial = calc.factorial(5);   // 120
const modulo = calc.modulo(17, 5);     // 2
const absolute = calc.absolute(-7);    // 7
const rounded = calc.roundNumber(3.14159, 2); // 3.14

// Mathematical operations
const gcd = calc.gcd(48, 18);          // 6
const lcm = calc.lcm(12, 18);          // 36
const isPrime = calc.isPrime(17);      // true
```

## Error Handling

The calculator properly handles error conditions:
- Division by zero throws `Error` with message "Division by zero"
- Negative square root throws `Error` with message "Cannot calculate square root of negative number"
- Negative factorial throws `Error` with message "Factorial is not defined for negative numbers"
- Modulo by zero throws `Error` with message "Modulo by zero"

## Development

This project is designed to be a stable baseline for testing bug injection tools. All tests should pass before any modifications are made for bug injection testing.

## Running the Application

```bash
# Run the calculator as a standalone application
npm start
```

This will output:
```
ReviewLab Calculator - Baseline Project
=====================================
5 + 3 = 8
10 - 4 = 6
6 * 7 = 42
15 / 3 = 5
2^8 = 256
√16 = 4
5! = 120
17 % 5 = 2
|-7| = 7
3.14159 rounded to 2 decimals = 3.14
GCD(48, 18) = 6
LCM(12, 18) = 36
Is 17 prime? true
Is 24 prime? false
```

## Code Quality

The project includes code quality tools:
- **ESLint**: Code linting and style checking
- **Jest**: Testing framework with coverage reporting

```bash
# Lint code
npm run lint

# Fix linting issues automatically
npm run lint:fix
```

## Testing Commands

```bash
# Run all tests
npm test

# Run tests with coverage report
npm run test:coverage

# Run tests in watch mode (for development)
npm run test:watch

# Run tests with verbose output
npm run test:verbose

# Run specific test file
npx jest tests/calculator.test.js

# Run specific test
npx jest --testNamePattern="should add two positive numbers"
```

## Coverage Report

After running `npm run test:coverage`, you'll get:
- Console output showing coverage percentages
- HTML coverage report in `coverage/` directory
- LCOV coverage report for CI integration

## Node.js Compatibility

The project is tested with:
- Node.js 16.x
- Node.js 18.x
- Node.js 20.x

## License

MIT License - see LICENSE file for details.
