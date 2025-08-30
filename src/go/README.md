# Go Calculator - Baseline Project

A simple calculator implementation in Go that serves as a baseline project for bug injection testing in ReviewLab.

## Features

- Basic arithmetic operations (add, subtract, multiply, divide)
- Power and square root calculations
- Factorial computation
- Modulo operations
- Absolute value and rounding
- Greatest common divisor (GCD) and least common multiple (LCM)
- Prime number checking
- Mathematical functions (min, max, ceil, floor)
- Logarithmic functions (natural log, base-10 log)
- Trigonometric functions (sin, cos, tan)
- Angle conversions (degrees ↔ radians)
- Comprehensive error handling
- Full unit test coverage with testify

## Requirements

- Go 1.21 or higher
- Go modules enabled

## Installation

```bash
# Initialize Go modules (if not already done)
go mod init reviewlab/calculator

# Download dependencies
go mod tidy
```

## Building and Testing

```bash
# Build the project
go build -o calculator .

# Run tests
go test ./...

# Run tests with verbose output
go test -v ./...

# Run tests with coverage
go test -cover ./...

# Run tests with coverage report
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html

# Run specific test
go test -run TestCalculator_Add

# Run the application
go run .
```

## Project Structure

```
src/
├── calculator.go              # Main calculator implementation
├── calculator_test.go         # Unit tests
├── go.mod                     # Go module definition
├── go.sum                     # Go module checksums
└── README.md                  # This file
```

## Test Coverage

The project includes comprehensive tests covering:
- All arithmetic operations
- Edge cases (zero, negative numbers, large numbers)
- Error conditions (division by zero, negative square root)
- Type safety and error handling
- Integration tests with complex calculations
- Exception handling verification
- Mathematical operations (GCD, LCM, prime checking)
- Trigonometric and logarithmic functions
- Edge cases with infinity and NaN

## Usage Example

```go
package main

import "reviewlab/calculator"

func main() {
    calc := calculator.NewCalculator()

    // Basic operations
    sum := calc.Add(5, 3)        // 8.0
    product := calc.Multiply(4, 2.5) // 10.0
    
    // Division with error handling
    quotient, err := calc.Divide(10, 2)
    if err != nil {
        // Handle error
    }
    // quotient = 5.0

    // Advanced operations
    power := calc.Power(2, 8)        // 256.0
    
    sqrt, err := calc.Sqrt(16)
    if err == nil {
        // sqrt = 4.0
    }
    
    factorial, err := calc.Factorial(5)
    if err == nil {
        // factorial = 120
    }

    // Mathematical operations
    gcd := calc.GCD(48, 18)          // 6
    lcm := calc.LCM(12, 18)          // 36
    isPrime := calc.IsPrime(17)      // true
}
```

## Error Handling

The calculator properly handles error conditions:
- Division by zero returns error "division by zero"
- Negative square root returns error "cannot calculate square root of negative number"
- Negative factorial returns error "factorial is not defined for negative numbers"
- Modulo by zero returns error "modulo by zero"
- Logarithm of non-positive numbers returns error "logarithm is not defined for non-positive numbers"

## Development

This project is designed to be a stable baseline for testing bug injection tools. All tests should pass before any modifications are made for bug injection testing.

## Running the Application

```bash
# Run the calculator as a standalone application
go run .
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
GCD(48, 18) = 6
LCM(12, 18) = 36
Is 17 prime? true
Is 24 prime? false
min(5, 3) = 3.0
max(5, 3) = 5.0
ceil(3.7) = 4.0
floor(3.7) = 3.0
ln(e) = 1.000000
log10(100) = 2.0
sin(30°) = 0.500000
cos(30°) = 0.866025
tan(30°) = 0.577350
```

## Code Quality

The project includes:
- **Go modules**: Modern dependency management
- **Testify**: Enhanced testing assertions and utilities
- **Comprehensive tests**: Table-driven tests for all operations
- **Error handling**: Proper Go error patterns
- **Documentation**: GoDoc compatible comments

## Testing Commands

```bash
# Run all tests
go test ./...

# Run tests with verbose output
go test -v ./...

# Run tests with coverage
go test -cover ./...

# Generate coverage report
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Run specific test function
go test -run TestCalculator_Add

# Run tests matching pattern
go test -run "Test.*Add.*"

# Benchmark tests (if any)
go test -bench=. ./...

# Race condition detection
go test -race ./...
```

## Coverage Report

After running `go test -coverprofile=coverage.out ./...`, you can:
- View coverage in terminal: `go tool cover -func=coverage.out`
- Generate HTML report: `go tool cover -html=coverage.out -o coverage.html`
- View coverage percentage: `go test -cover ./...`

## Go Compatibility

The project is tested with:
- Go 1.21.x
- Go 1.22.x
- Go 1.23.x

## Dependencies

- **github.com/stretchr/testify**: Enhanced testing utilities
  - `assert`: Assertion functions
  - `require`: Required assertions (stop on failure)
  - `suite`: Test suite support

## Building for Distribution

```bash
# Build for current platform
go build -o calculator .

# Build for specific platforms
GOOS=linux GOARCH=amd64 go build -o calculator-linux-amd64 .
GOOS=windows GOARCH=amd64 go build -o calculator-windows-amd64.exe .
GOOS=darwin GOARCH=amd64 go build -o calculator-darwin-amd64 .

# Build with optimizations
go build -ldflags="-s -w" -o calculator .
```

## License

MIT License - see LICENSE file for details.
