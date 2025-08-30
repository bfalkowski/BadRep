# Java Calculator - Baseline Project

A simple calculator implementation in Java that serves as a baseline project for bug injection testing in ReviewLab.

## Features

- Basic arithmetic operations (add, subtract, multiply, divide)
- Power and square root calculations
- Factorial computation
- Comprehensive error handling
- Full unit test coverage

## Requirements

- Java 11 or higher
- Maven 3.6 or higher

## Building the Project

```bash
# Compile the project
mvn compile

# Run tests
mvn test

# Create JAR file
mvn package

# Run the application
java -jar target/calculator-1.0.0.jar
```

## Project Structure

```
src/
├── main/java/com/reviewlab/calculator/
│   └── Calculator.java          # Main calculator class
└── test/java/com/reviewlab/calculator/
    └── CalculatorTest.java      # Unit tests
```

## Running Tests

```bash
# Run all tests
mvn test

# Run tests with coverage
mvn test jacoco:report

# Run specific test
mvn test -Dtest=CalculatorTest#testAddPositiveNumbers
```

## Test Coverage

The project includes comprehensive tests covering:
- All arithmetic operations
- Edge cases (zero, negative numbers)
- Error conditions (division by zero, negative square root)
- Parameterized tests for factorial calculations
- Exception handling verification

## Usage Example

```java
Calculator calc = new Calculator();

// Basic operations
double sum = calc.add(5.0, 3.0);        // 8.0
double product = calc.multiply(4.0, 2.5); // 10.0
double quotient = calc.divide(10.0, 2.0); // 5.0

// Advanced operations
double power = calc.power(2.0, 8.0);     // 256.0
double sqrt = calc.sqrt(16.0);           // 4.0
long factorial = calc.factorial(5);      // 120
```

## Error Handling

The calculator properly handles error conditions:
- Division by zero throws `ArithmeticException`
- Negative square root throws `IllegalArgumentException`
- Negative factorial throws `IllegalArgumentException`

## Development

This project is designed to be a stable baseline for testing bug injection tools. All tests should pass before any modifications are made for bug injection testing.

## License

MIT License - see LICENSE file for details.
