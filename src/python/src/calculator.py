#!/usr/bin/env python3
"""
Calculator module for ReviewLab baseline project.

A simple calculator implementation that serves as a baseline project
for bug injection testing.
"""

import math
from typing import Union, Optional


class Calculator:
    """
    A simple calculator class for basic arithmetic operations.
    
    This serves as a baseline project for bug injection testing.
    """
    
    def __init__(self):
        """Initialize the calculator."""
        pass
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Add two numbers.
        
        Args:
            a: The first number
            b: The second number
            
        Returns:
            The sum of a and b
        """
        return float(a + b)
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Subtract the second number from the first.
        
        Args:
            a: The first number
            b: The second number
            
        Returns:
            The difference of a and b
        """
        return float(a - b)
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Multiply two numbers.
        
        Args:
            a: The first number
            b: The second number
            
        Returns:
            The product of a and b
        """
        return float(a * b)
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Divide the first number by the second.
        
        Args:
            a: The dividend
            b: The divisor
            
        Returns:
            The quotient of a divided by b
            
        Raises:
            ZeroDivisionError: If b is zero
        """
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        return float(a / b)
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> float:
        """
        Calculate the power of a number.
        
        Args:
            base: The base number
            exponent: The exponent
            
        Returns:
            base raised to the power of exponent
        """
        return float(math.pow(base, exponent))
    
    def sqrt(self, number: Union[int, float]) -> float:
        """
        Calculate the square root of a number.
        
        Args:
            number: The number to find the square root of
            
        Returns:
            The square root of the number
            
        Raises:
            ValueError: If number is negative
        """
        if number < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return float(math.sqrt(number))
    
    def factorial(self, n: int) -> int:
        """
        Calculate the factorial of a non-negative integer.
        
        Args:
            n: The number to calculate factorial for
            
        Returns:
            The factorial of n
            
        Raises:
            ValueError: If n is negative
        """
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        if n == 0 or n == 1:
            return 1
        
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    def modulo(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Calculate the modulo of two numbers.
        
        Args:
            a: The dividend
            b: The divisor
            
        Returns:
            The remainder of a divided by b
            
        Raises:
            ZeroDivisionError: If b is zero
        """
        if b == 0:
            raise ZeroDivisionError("Modulo by zero")
        return float(a % b)
    
    def absolute(self, number: Union[int, float]) -> float:
        """
        Calculate the absolute value of a number.
        
        Args:
            number: The number to find the absolute value of
            
        Returns:
            The absolute value of the number
        """
        return float(abs(number))
    
    def round_number(self, number: Union[int, float], decimals: Optional[int] = 0) -> float:
        """
        Round a number to a specified number of decimal places.
        
        Args:
            number: The number to round
            decimals: Number of decimal places (default: 0)
            
        Returns:
            The rounded number
        """
        return float(round(number, decimals))


def main():
    """Main function to run the calculator as a standalone application."""
    calc = Calculator()
    
    print("ReviewLab Calculator - Baseline Project")
    print("=====================================")
    
    # Test basic operations
    print(f"5 + 3 = {calc.add(5, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
    print(f"6 * 7 = {calc.multiply(6, 7)}")
    print(f"15 / 3 = {calc.divide(15, 3)}")
    
    # Test advanced operations
    print(f"2^8 = {calc.power(2, 8)}")
    print(f"√16 = {calc.sqrt(16)}")
    print(f"5! = {calc.factorial(5)}")
    print(f"17 % 5 = {calc.modulo(17, 5)}")
    print(f"|-7| = {calc.absolute(-7)}")
    print(f"3.14159 rounded to 2 decimals = {calc.round_number(3.14159, 2)}")


if __name__ == "__main__":
    main()
