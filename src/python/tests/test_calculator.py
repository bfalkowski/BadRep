"""
Unit tests for the Calculator class.

Tests all arithmetic operations and edge cases using pytest.
"""

import pytest
import math
from src.calculator import Calculator


class TestCalculator:
    """Test suite for the Calculator class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.calc = Calculator()
    
    def test_add_positive_numbers(self):
        """Test addition of positive numbers."""
        assert self.calc.add(2, 3) == 5.0
        assert self.calc.add(7, 3) == 10.0
        assert self.calc.add(0, 5) == 5.0
    
    def test_add_negative_numbers(self):
        """Test addition of negative numbers."""
        assert self.calc.add(-3, 2) == -1.0
        assert self.calc.add(-2, -3) == -5.0
        assert self.calc.add(-5, 0) == -5.0
    
    def test_add_floats(self):
        """Test addition with floating point numbers."""
        assert self.calc.add(2.5, 3.5) == 6.0
        assert self.calc.add(1.1, 2.2) == pytest.approx(3.3, rel=1e-10)
    
    def test_subtract_numbers(self):
        """Test subtraction of numbers."""
        assert self.calc.subtract(5, 3) == 2.0
        assert self.calc.subtract(3, 5) == -2.0
        assert self.calc.subtract(5, 0) == 5.0
        assert self.calc.subtract(0, 3) == -3.0
    
    def test_subtract_floats(self):
        """Test subtraction with floating point numbers."""
        assert self.calc.subtract(5.5, 2.5) == 3.0
        assert self.calc.subtract(3.3, 1.1) == pytest.approx(2.2, rel=1e-10)
    
    def test_multiply_numbers(self):
        """Test multiplication of numbers."""
        assert self.calc.multiply(3, 5) == 15.0
        assert self.calc.multiply(3, -5) == -15.0
        assert self.calc.multiply(5, 0) == 0.0
        assert self.calc.multiply(0, 5) == 0.0
    
    def test_multiply_floats(self):
        """Test multiplication with floating point numbers."""
        assert self.calc.multiply(2.5, 3.0) == 7.5
        assert self.calc.multiply(1.5, 2.5) == 3.75
    
    def test_divide_numbers(self):
        """Test division of numbers."""
        assert self.calc.divide(5, 2) == 2.5
        assert self.calc.divide(-5, 2) == -2.5
        assert self.calc.divide(0, 5) == 0.0
        assert self.calc.divide(10, 2) == 5.0
    
    def test_divide_floats(self):
        """Test division with floating point numbers."""
        assert self.calc.divide(5.5, 2.0) == 2.75
        assert self.calc.divide(3.3, 1.1) == pytest.approx(3.0, rel=1e-10)
    
    def test_divide_by_zero(self):
        """Test that division by zero raises an exception."""
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.calc.divide(5, 0)
        assert str(exc_info.value) == "Division by zero"
    
    def test_power(self):
        """Test power calculations."""
        assert self.calc.power(2, 3) == 8.0
        assert self.calc.power(5, 0) == 1.0
        assert self.calc.power(2, -2) == 0.25
        assert self.calc.power(3, 2) == 9.0
    
    def test_power_floats(self):
        """Test power calculations with floating point numbers."""
        assert self.calc.power(2.5, 2) == 6.25
        assert self.calc.power(4, 0.5) == 2.0
    
    def test_sqrt(self):
        """Test square root calculations."""
        assert self.calc.sqrt(16) == 4.0
        assert self.calc.sqrt(0) == 0.0
        assert self.calc.sqrt(2) == pytest.approx(math.sqrt(2), rel=1e-10)
        assert self.calc.sqrt(25) == 5.0
    
    def test_sqrt_floats(self):
        """Test square root with floating point numbers."""
        assert self.calc.sqrt(16.0) == 4.0
        assert self.calc.sqrt(2.25) == 1.5
    
    def test_sqrt_negative(self):
        """Test that square root of negative numbers raises an exception."""
        with pytest.raises(ValueError) as exc_info:
            self.calc.sqrt(-1)
        assert str(exc_info.value) == "Cannot calculate square root of negative number"
    
    def test_factorial(self):
        """Test factorial calculations."""
        assert self.calc.factorial(0) == 1
        assert self.calc.factorial(1) == 1
        assert self.calc.factorial(2) == 2
        assert self.calc.factorial(3) == 6
        assert self.calc.factorial(4) == 24
        assert self.calc.factorial(5) == 120
    
    def test_factorial_negative(self):
        """Test that factorial of negative numbers raises an exception."""
        with pytest.raises(ValueError) as exc_info:
            self.calc.factorial(-1)
        assert str(exc_info.value) == "Factorial is not defined for negative numbers"
    
    def test_modulo(self):
        """Test modulo operations."""
        assert self.calc.modulo(17, 5) == 2.0
        assert self.calc.modulo(10, 3) == 1.0
        assert self.calc.modulo(8, 4) == 0.0
        assert self.calc.modulo(-17, 5) == 3.0
    
    def test_modulo_floats(self):
        """Test modulo with floating point numbers."""
        assert self.calc.modulo(17.5, 5.0) == 2.5
        assert self.calc.modulo(10.7, 3.0) == pytest.approx(1.7, rel=1e-10)
    
    def test_modulo_by_zero(self):
        """Test that modulo by zero raises an exception."""
        with pytest.raises(ZeroDivisionError) as exc_info:
            self.calc.modulo(5, 0)
        assert str(exc_info.value) == "Modulo by zero"
    
    def test_absolute(self):
        """Test absolute value calculations."""
        assert self.calc.absolute(7) == 7.0
        assert self.calc.absolute(-7) == 7.0
        assert self.calc.absolute(0) == 0.0
        assert self.calc.absolute(-3.5) == 3.5
    
    def test_absolute_floats(self):
        """Test absolute value with floating point numbers."""
        assert self.calc.absolute(3.14) == 3.14
        assert self.calc.absolute(-2.718) == 2.718
    
    def test_round_number(self):
        """Test number rounding."""
        assert self.calc.round_number(3.14159) == 3.0
        assert self.calc.round_number(3.14159, 2) == 3.14
        assert self.calc.round_number(3.14159, 4) == 3.1416
        assert self.calc.round_number(2.5) == 2.0
        assert self.calc.round_number(2.5, 0) == 2.0
    
    def test_round_number_floats(self):
        """Test rounding with floating point numbers."""
        assert self.calc.round_number(3.7) == 4.0
        assert self.calc.round_number(-3.7) == -4.0
        assert self.calc.round_number(3.14159, 3) == 3.142
    
    def test_type_conversion(self):
        """Test that all methods return the correct types."""
        assert isinstance(self.calc.add(1, 2), float)
        assert isinstance(self.calc.subtract(5, 3), float)
        assert isinstance(self.calc.multiply(2, 3), float)
        assert isinstance(self.calc.divide(6, 2), float)
        assert isinstance(self.calc.power(2, 3), float)
        assert isinstance(self.calc.sqrt(4), float)
        assert isinstance(self.calc.factorial(5), int)
        assert isinstance(self.calc.modulo(7, 3), float)
        assert isinstance(self.calc.absolute(-5), float)
        assert isinstance(self.calc.round_number(3.14), float)
    
    def test_edge_cases(self):
        """Test various edge cases."""
        # Very large numbers
        assert self.calc.add(1e10, 1e10) == 2e10
        assert self.calc.multiply(1e5, 1e5) == 1e10
        
        # Very small numbers
        assert self.calc.add(1e-10, 1e-10) == 2e-10
        assert self.calc.multiply(1e-5, 1e-5) == pytest.approx(1e-10, rel=1e-10)
        
        # Zero operations
        assert self.calc.add(0, 0) == 0.0
        assert self.calc.multiply(0, 0) == 0.0
        assert self.calc.power(0, 1) == 0.0
        assert self.calc.absolute(0) == 0.0


class TestCalculatorIntegration:
    """Integration tests for the Calculator class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.calc = Calculator()
    
    def test_complex_calculation(self):
        """Test a complex calculation combining multiple operations."""
        # Calculate: (5 + 3) * 2 - 4 / 2
        result = self.calc.subtract(
            self.calc.multiply(
                self.calc.add(5, 3), 2
            ),
            self.calc.divide(4, 2)
        )
        expected = (5 + 3) * 2 - 4 / 2
        assert result == expected
    
    def test_factorial_chain(self):
        """Test chaining factorial calculations."""
        # Calculate: 5! + 3! - 2!
        result = self.calc.add(
            self.calc.factorial(5),
            self.calc.subtract(
                self.calc.factorial(3),
                self.calc.factorial(2)
            )
        )
        expected = math.factorial(5) + math.factorial(3) - math.factorial(2)
        assert result == expected
    
    def test_power_and_sqrt(self):
        """Test power and square root operations together."""
        # Calculate: √(2^8 + 3^2)
        result = self.calc.sqrt(
            self.calc.add(
                self.calc.power(2, 8),
                self.calc.power(3, 2)
            )
        )
        expected = math.sqrt(2**8 + 3**2)
        assert result == pytest.approx(expected, rel=1e-10)


if __name__ == "__main__":
    pytest.main([__file__])
