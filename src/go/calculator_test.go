package main

import (
	"math"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewCalculator(t *testing.T) {
	calc := NewCalculator()
	assert.NotNil(t, calc)
}

func TestCalculator_Add(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name     string
		a, b     float64
		expected float64
	}{
		{"positive numbers", 2, 3, 5},
		{"negative numbers", -3, 2, -1},
		{"both negative", -2, -3, -5},
		{"with zero", 5, 0, 5},
		{"both zero", 0, 0, 0},
		{"floating point", 2.5, 3.5, 6.0},
		{"large numbers", 1e10, 1e10, 2e10},
		{"small numbers", 1e-10, 1e-10, 2e-10},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := calc.Add(tt.a, tt.b)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCalculator_Subtract(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name     string
		a, b     float64
		expected float64
	}{
		{"positive numbers", 5, 3, 2},
		{"negative result", 3, 5, -2},
		{"with zero", 5, 0, 5},
		{"from zero", 0, 3, -3},
		{"floating point", 5.5, 2.5, 3.0},
		{"negative numbers", -5, -3, -2},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := calc.Subtract(tt.a, tt.b)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCalculator_Multiply(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name     string
		a, b     float64
		expected float64
	}{
		{"positive numbers", 3, 5, 15},
		{"negative result", 3, -5, -15},
		{"with zero", 5, 0, 0},
		{"both zero", 0, 0, 0},
		{"floating point", 2.5, 3, 7.5},
		{"negative numbers", -2, -3, 6},
		{"large numbers", 1e5, 1e5, 1e10},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := calc.Multiply(tt.a, tt.b)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCalculator_Divide(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name        string
		a, b        float64
		expected    float64
		expectError bool
	}{
		{"valid division", 5, 2, 2.5, false},
		{"negative result", -5, 2, -2.5, false},
		{"floating point", 5.5, 2, 2.75, false},
		{"division by zero", 5, 0, 0, true},
		{"zero divided", 0, 5, 0, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := calc.Divide(tt.a, tt.b)
			if tt.expectError {
				assert.Error(t, err)
				assert.Equal(t, "division by zero", err.Error())
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expected, result)
			}
		})
	}
}

func TestCalculator_Power(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name     string
		base     float64
		exponent float64
		expected float64
	}{
		{"positive power", 2, 3, 8},
		{"zero power", 5, 0, 1},
		{"negative power", 2, -2, 0.25},
		{"fractional power", 4, 0.5, 2},
		{"floating point base", 2.5, 2, 6.25},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := calc.Power(tt.base, tt.exponent)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCalculator_Sqrt(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name        string
		number      float64
		expected    float64
		expectError bool
	}{
		{"positive number", 16, 4, false},
		{"zero", 0, 0, false},
		{"perfect square", 25, 5, false},
		{"floating point", 2.25, 1.5, false},
		{"negative number", -1, 0, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := calc.Sqrt(tt.number)
			if tt.expectError {
				assert.Error(t, err)
				assert.Equal(t, "cannot calculate square root of negative number", err.Error())
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expected, result)
			}
		})
	}
}

func TestCalculator_Factorial(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name        string
		n           int
		expected    int
		expectError bool
	}{
		{"zero", 0, 1, false},
		{"one", 1, 1, false},
		{"small numbers", 2, 2, false},
		{"medium numbers", 5, 120, false},
		{"large number", 10, 3628800, false},
		{"negative number", -1, 0, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := calc.Factorial(tt.n)
			if tt.expectError {
				assert.Error(t, err)
				assert.Equal(t, "factorial is not defined for negative numbers", err.Error())
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expected, result)
			}
		})
	}
}

func TestCalculator_Modulo(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name        string
		a, b        float64
		expected    float64
		expectError bool
	}{
		{"valid modulo", 17, 5, 2, false},
		{"exact division", 10, 2, 0, false},
		{"floating point", 17.5, 5, 2.5, false},
		{"modulo by zero", 5, 0, 0, true},
		{"negative numbers", -17, 5, -2, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := calc.Modulo(tt.a, tt.b)
			if tt.expectError {
				assert.Error(t, err)
				assert.Equal(t, "modulo by zero", err.Error())
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expected, result)
			}
		})
	}
}

func TestCalculator_Absolute(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name     string
		number   float64
		expected float64
	}{
		{"positive number", 7, 7},
		{"negative number", -7, 7},
		{"zero", 0, 0},
		{"floating point", -3.14, 3.14},
		{"large negative", -1e10, 1e10},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := calc.Absolute(tt.number)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCalculator_Round(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name     string
		number   float64
		decimals int
		expected float64
	}{
		{"no decimals", 3.14159, 0, 3},
		{"two decimals", 3.14159, 2, 3.14},
		{"four decimals", 3.14159, 4, 3.1416},
		{"negative number", -3.7, 0, -4},
		{"round up", 2.5, 0, 2},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := calc.Round(tt.number, tt.decimals)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCalculator_GCD(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name     string
		a, b     int
		expected int
	}{
		{"positive numbers", 48, 18, 6},
		{"coprime numbers", 7, 13, 1},
		{"same number", 12, 12, 12},
		{"negative numbers", -48, 18, 6},
		{"zero", 0, 5, 5},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := calc.GCD(tt.a, tt.b)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCalculator_LCM(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name     string
		a, b     int
		expected int
	}{
		{"positive numbers", 12, 18, 36},
		{"coprime numbers", 5, 7, 35},
		{"same number", 8, 8, 8},
		{"negative numbers", -12, 18, 36},
		{"with zero", 0, 5, 0},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := calc.LCM(tt.a, tt.b)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCalculator_IsPrime(t *testing.T) {
	calc := NewCalculator()

	tests := []struct {
		name     string
		n        int
		expected bool
	}{
		{"small primes", 2, true},
		{"small primes", 3, true},
		{"small primes", 5, true},
		{"small primes", 7, true},
		{"larger prime", 17, true},
		{"larger prime", 23, true},
		{"non-prime 1", 1, false},
		{"non-prime 4", 4, false},
		{"non-prime 6", 6, false},
		{"non-prime 9", 9, false},
		{"non-prime 15", 15, false},
		{"zero", 0, false},
		{"negative", -1, false},
		{"negative", -5, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := calc.IsPrime(tt.n)
			assert.Equal(t, tt.expected, result)
		})
	}
}

func TestCalculator_MinMax(t *testing.T) {
	calc := NewCalculator()

	// Test Min
	assert.Equal(t, 3.0, calc.Min(5, 3))
	assert.Equal(t, -5.0, calc.Min(-5, 3))
	assert.Equal(t, 0.0, calc.Min(0, 5))

	// Test Max
	assert.Equal(t, 5.0, calc.Max(5, 3))
	assert.Equal(t, 3.0, calc.Max(-5, 3))
	assert.Equal(t, 5.0, calc.Max(0, 5))
}

func TestCalculator_CeilFloor(t *testing.T) {
	calc := NewCalculator()

	// Test Ceil
	assert.Equal(t, 4.0, calc.Ceil(3.7))
	assert.Equal(t, 3.0, calc.Ceil(3.0))
	assert.Equal(t, -3.0, calc.Ceil(-3.7))

	// Test Floor
	assert.Equal(t, 3.0, calc.Floor(3.7))
	assert.Equal(t, 3.0, calc.Floor(3.0))
	assert.Equal(t, -4.0, calc.Floor(-3.7))
}

func TestCalculator_Log(t *testing.T) {
	calc := NewCalculator()

	// Test natural logarithm
	result, err := calc.Log(math.E)
	require.NoError(t, err)
	assert.Equal(t, 1.0, result)

	// Test base-10 logarithm
	result, err = calc.Log10(100)
	require.NoError(t, err)
	assert.Equal(t, 2.0, result)

	// Test error cases
	_, err = calc.Log(0)
	assert.Error(t, err)
	assert.Equal(t, "logarithm is not defined for non-positive numbers", err.Error())

	_, err = calc.Log(-1)
	assert.Error(t, err)
	assert.Equal(t, "logarithm is not defined for non-positive numbers", err.Error())
}

func TestCalculator_Trigonometric(t *testing.T) {
	calc := NewCalculator()

	// Test angle conversions
	radians := calc.DegreesToRadians(30)
	degrees := calc.RadiansToDegrees(radians)
	assert.Equal(t, 30.0, degrees)

	// Test trigonometric functions
	angle := calc.DegreesToRadians(30)
	sin := calc.Sin(angle)
	cos := calc.Cos(angle)
	tan := calc.Tan(angle)

	// These should be approximately correct for 30 degrees
	assert.InDelta(t, 0.5, sin, 0.001)
	assert.InDelta(t, 0.866, cos, 0.001)
	assert.InDelta(t, 0.577, tan, 0.001)
}

func TestCalculator_Integration(t *testing.T) {
	calc := NewCalculator()

	// Test complex calculation: (5 + 3) * 2 - 4 / 2
	addResult := calc.Add(5, 3)
	multiplyResult := calc.Multiply(addResult, 2)
	divideResult, err := calc.Divide(4, 2)
	require.NoError(t, err)
	finalResult := calc.Subtract(multiplyResult, divideResult)

	expected := (5 + 3) * 2 - 4/2
	assert.Equal(t, expected, finalResult)

	// Test factorial chain: 5! + 3! - 2!
	fact5, err := calc.Factorial(5)
	require.NoError(t, err)
	fact3, err := calc.Factorial(3)
	require.NoError(t, err)
	fact2, err := calc.Factorial(2)
	require.NoError(t, err)

	chainResult := calc.Add(fact5, calc.Subtract(fact3, fact2))
	expectedChain := 120 + 6 - 2
	assert.Equal(t, expectedChain, chainResult)

	// Test power and square root: √(2^8 + 3^2)
	powerResult := calc.Power(2, 8)
	powerResult2 := calc.Power(3, 2)
	sumResult := calc.Add(powerResult, powerResult2)
	sqrtResult, err := calc.Sqrt(sumResult)
	require.NoError(t, err)

	expectedSqrt := math.Sqrt(2*8 + 3*2)
	assert.Equal(t, expectedSqrt, sqrtResult)
}

func TestCalculator_EdgeCases(t *testing.T) {
	calc := NewCalculator()

	// Test very large numbers
	assert.Equal(t, 2e10, calc.Add(1e10, 1e10))
	assert.Equal(t, 1e10, calc.Multiply(1e5, 1e5))

	// Test very small numbers
	assert.Equal(t, 2e-10, calc.Add(1e-10, 1e-10))
	assert.Equal(t, 1e-10, calc.Multiply(1e-5, 1e-5))

	// Test infinity handling
	assert.True(t, math.IsInf(calc.Add(math.Inf(1), 5), 1))
	assert.True(t, math.IsNaN(calc.Multiply(math.Inf(1), 0)))

	// Test division by zero (should return infinity in Go)
	result, err := calc.Divide(1, 0)
	assert.Error(t, err)
	assert.Equal(t, "division by zero", err.Error())
}
