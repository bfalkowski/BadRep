package main

import (
	"errors"
	"fmt"
	"math"
)

// Calculator represents a simple calculator for basic arithmetic operations.
// This serves as a baseline project for bug injection testing.
type Calculator struct{}

// NewCalculator creates a new Calculator instance.
func NewCalculator() *Calculator {
	return &Calculator{}
}

// Add adds two numbers.
func (c *Calculator) Add(a, b float64) float64 {
	return a + b
}

// Subtract subtracts the second number from the first.
func (c *Calculator) Subtract(a, b float64) float64 {
	return a - b
}

// Multiply multiplies two numbers.
func (c *Calculator) Multiply(a, b float64) float64 {
	return a * b
}

// Divide divides the first number by the second.
func (c *Calculator) Divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, errors.New("division by zero")
	}
	return a / b, nil
}

// Power calculates the power of a number.
func (c *Calculator) Power(base, exponent float64) float64 {
	return math.Pow(base, exponent)
}

// Sqrt calculates the square root of a number.
func (c *Calculator) Sqrt(number float64) (float64, error) {
	if number < 0 {
		return 0, errors.New("cannot calculate square root of negative number")
	}
	return math.Sqrt(number), nil
}

// Factorial calculates the factorial of a non-negative integer.
func (c *Calculator) Factorial(n int) (int, error) {
	if n < 0 {
		return 0, errors.New("factorial is not defined for negative numbers")
	}
	if n == 0 || n == 1 {
		return 1, nil
	}

	result := 1
	for i := 2; i <= n; i++ {
		result *= i
	}
	return result, nil
}

// Modulo calculates the modulo of two numbers.
func (c *Calculator) Modulo(a, b float64) (float64, error) {
	if b == 0 {
		return 0, errors.New("modulo by zero")
	}
	return math.Mod(a, b), nil
}

// Absolute calculates the absolute value of a number.
func (c *Calculator) Absolute(number float64) float64 {
	return math.Abs(number)
}

// Round rounds a number to a specified number of decimal places.
func (c *Calculator) Round(number float64, decimals int) float64 {
	shift := math.Pow(10, float64(decimals))
	return math.Round(number*shift) / shift
}

// GCD calculates the greatest common divisor of two integers.
func (c *Calculator) GCD(a, b int) int {
	a = int(math.Abs(float64(a)))
	b = int(math.Abs(float64(b)))

	for b != 0 {
		temp := b
		b = a % b
		a = temp
	}
	return a
}

// LCM calculates the least common multiple of two integers.
func (c *Calculator) LCM(a, b int) int {
	return int(math.Abs(float64(a*b)) / float64(c.GCD(a, b)))
}

// IsPrime checks if a number is prime.
func (c *Calculator) IsPrime(n int) bool {
	if n < 2 {
		return false
	}
	if n == 2 {
		return true
	}
	if n%2 == 0 {
		return false
	}

	for i := 3; i <= int(math.Sqrt(float64(n))); i += 2 {
		if n%i == 0 {
			return false
		}
	}
	return true
}

// Min returns the minimum of two numbers.
func (c *Calculator) Min(a, b float64) float64 {
	return math.Min(a, b)
}

// Max returns the maximum of two numbers.
func (c *Calculator) Max(a, b float64) float64 {
	return math.Max(a, b)
}

// Ceil returns the ceiling of a number.
func (c *Calculator) Ceil(number float64) float64 {
	return math.Ceil(number)
}

// Floor returns the floor of a number.
func (c *Calculator) Floor(number float64) float64 {
	return math.Floor(number)
}

// Log calculates the natural logarithm of a number.
func (c *Calculator) Log(number float64) (float64, error) {
	if number <= 0 {
		return 0, errors.New("logarithm is not defined for non-positive numbers")
	}
	return math.Log(number), nil
}

// Log10 calculates the base-10 logarithm of a number.
func (c *Calculator) Log10(number float64) (float64, error) {
	if number <= 0 {
		return 0, errors.New("logarithm is not defined for non-positive numbers")
	}
	return math.Log10(number), nil
}

// Sin calculates the sine of an angle in radians.
func (c *Calculator) Sin(angle float64) float64 {
	return math.Sin(angle)
}

// Cos calculates the cosine of an angle in radians.
func (c *Calculator) Cos(angle float64) float64 {
	return math.Cos(angle)
}

// Tan calculates the tangent of an angle in radians.
func (c *Calculator) Tan(angle float64) float64 {
	return math.Tan(angle)
}

// DegreesToRadians converts degrees to radians.
func (c *Calculator) DegreesToRadians(degrees float64) float64 {
	return degrees * math.Pi / 180
}

// RadiansToDegrees converts radians to degrees.
func (c *Calculator) RadiansToDegrees(radians float64) float64 {
	return radians * 180 / math.Pi
}

// main function runs the calculator as a standalone application.
func main() {
	calc := NewCalculator()

	fmt.Println("ReviewLab Calculator - Baseline Project")
	fmt.Println("=====================================")

	// Test basic operations
	fmt.Printf("5 + 3 = %.1f\n", calc.Add(5, 3))
	fmt.Printf("10 - 4 = %.1f\n", calc.Subtract(10, 4))
	fmt.Printf("6 * 7 = %.1f\n", calc.Multiply(6, 7))

	if result, err := calc.Divide(15, 3); err == nil {
		fmt.Printf("15 / 3 = %.1f\n", result)
	}

	// Test advanced operations
	fmt.Printf("2^8 = %.1f\n", calc.Power(2, 8))

	if result, err := calc.Sqrt(16); err == nil {
		fmt.Printf("√16 = %.1f\n", result)
	}

	if result, err := calc.Factorial(5); err == nil {
		fmt.Printf("5! = %d\n", result)
	}

	if result, err := calc.Modulo(17, 5); err == nil {
		fmt.Printf("17 %% 5 = %.1f\n", result)
	}

	fmt.Printf("|-7| = %.1f\n", calc.Absolute(-7))
	fmt.Printf("3.14159 rounded to 2 decimals = %.2f\n", calc.Round(3.14159, 2))

	// Test additional operations
	fmt.Printf("GCD(48, 18) = %d\n", calc.GCD(48, 18))
	fmt.Printf("LCM(12, 18) = %d\n", calc.LCM(12, 18))
	fmt.Printf("Is 17 prime? %t\n", calc.IsPrime(17))
	fmt.Printf("Is 24 prime? %t\n", calc.IsPrime(24))

	// Test mathematical functions
	fmt.Printf("min(5, 3) = %.1f\n", calc.Min(5, 3))
	fmt.Printf("max(5, 3) = %.1f\n", calc.Max(5, 3))
	fmt.Printf("ceil(3.7) = %.1f\n", calc.Ceil(3.7))
	fmt.Printf("floor(3.7) = %.1f\n", calc.Floor(3.7))

	if result, err := calc.Log(math.E); err == nil {
		fmt.Printf("ln(e) = %.6f\n", result)
	}

	if result, err := calc.Log10(100); err == nil {
		fmt.Printf("log10(100) = %.1f\n", result)
	}

	// Test trigonometric functions
	angle := calc.DegreesToRadians(30)
	fmt.Printf("sin(30°) = %.6f\n", calc.Sin(angle))
	fmt.Printf("cos(30°) = %.6f\n", calc.Cos(angle))
	fmt.Printf("tan(30°) = %.6f\n", calc.Tan(angle))
}
