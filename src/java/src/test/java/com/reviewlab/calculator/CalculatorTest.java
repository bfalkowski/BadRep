package com.reviewlab.calculator;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.junit.jupiter.params.provider.CsvSource;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for the Calculator class.
 * Tests all arithmetic operations and edge cases.
 */
@DisplayName("Calculator Tests")
class CalculatorTest {
    
    private Calculator calculator;
    
    @BeforeEach
    void setUp() {
        calculator = new Calculator();
    }
    
    @Test
    @DisplayName("Should add two positive numbers correctly")
    void testAddPositiveNumbers() {
        assertEquals(5.0, calculator.add(2.0, 3.0), 0.001);
        assertEquals(10.0, calculator.add(7.0, 3.0), 0.001);
    }
    
    @Test
    @DisplayName("Should add negative numbers correctly")
    void testAddNegativeNumbers() {
        assertEquals(-1.0, calculator.add(-3.0, 2.0), 0.001);
        assertEquals(-5.0, calculator.add(-2.0, -3.0), 0.001);
    }
    
    @Test
    @DisplayName("Should add zero correctly")
    void testAddWithZero() {
        assertEquals(5.0, calculator.add(5.0, 0.0), 0.001);
        assertEquals(3.0, calculator.add(0.0, 3.0), 0.001);
    }
    
    @Test
    @DisplayName("Should subtract two numbers correctly")
    void testSubtractNumbers() {
        assertEquals(2.0, calculator.subtract(5.0, 3.0), 0.001);
        assertEquals(-2.0, calculator.subtract(3.0, 5.0), 0.001);
    }
    
    @Test
    @DisplayName("Should subtract zero correctly")
    void testSubtractWithZero() {
        assertEquals(5.0, calculator.subtract(5.0, 0.0), 0.001);
        assertEquals(-3.0, calculator.subtract(0.0, 3.0), 0.001);
    }
    
    @Test
    @DisplayName("Should multiply two numbers correctly")
    void testMultiplyNumbers() {
        assertEquals(15.0, calculator.multiply(3.0, 5.0), 0.001);
        assertEquals(-15.0, calculator.multiply(3.0, -5.0), 0.001);
    }
    
    @Test
    @DisplayName("Should multiply by zero correctly")
    void testMultiplyByZero() {
        assertEquals(0.0, calculator.multiply(5.0, 0.0), 0.001);
        assertEquals(0.0, calculator.multiply(0.0, 5.0), 0.001);
    }
    
    @Test
    @DisplayName("Should divide two numbers correctly")
    void testDivideNumbers() {
        assertEquals(2.5, calculator.divide(5.0, 2.0), 0.001);
        assertEquals(-2.5, calculator.divide(-5.0, 2.0), 0.001);
    }
    
    @Test
    @DisplayName("Should throw exception when dividing by zero")
    void testDivideByZero() {
        ArithmeticException exception = assertThrows(
            ArithmeticException.class,
            () -> calculator.divide(5.0, 0.0)
        );
        assertEquals("Division by zero", exception.getMessage());
    }
    
    @Test
    @DisplayName("Should calculate power correctly")
    void testPower() {
        assertEquals(8.0, calculator.power(2.0, 3.0), 0.001);
        assertEquals(1.0, calculator.power(5.0, 0.0), 0.001);
        assertEquals(0.25, calculator.power(2.0, -2.0), 0.001);
    }
    
    @Test
    @DisplayName("Should calculate square root correctly")
    void testSquareRoot() {
        assertEquals(4.0, calculator.sqrt(16.0), 0.001);
        assertEquals(0.0, calculator.sqrt(0.0), 0.001);
        assertEquals(1.414, calculator.sqrt(2.0), 0.001);
    }
    
    @Test
    @DisplayName("Should throw exception for negative square root")
    void testSquareRootNegative() {
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> calculator.sqrt(-1.0)
        );
        assertEquals("Cannot calculate square root of negative number", exception.getMessage());
    }
    
    @ParameterizedTest
    @ValueSource(ints = {0, 1, 2, 3, 4, 5})
    @DisplayName("Should calculate factorial for valid inputs")
    void testFactorialValid(int n) {
        long expected = calculateExpectedFactorial(n);
        assertEquals(expected, calculator.factorial(n));
    }
    
    @Test
    @DisplayName("Should throw exception for negative factorial")
    void testFactorialNegative() {
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> calculator.factorial(-1)
        );
        assertEquals("Factorial is not defined for negative numbers", exception.getMessage());
    }
    
    @ParameterizedTest
    @CsvSource({
        "0, 1",
        "1, 1", 
        "2, 2",
        "3, 6",
        "4, 24",
        "5, 120"
    })
    @DisplayName("Should calculate factorial for specific values")
    void testFactorialSpecific(int input, long expected) {
        assertEquals(expected, calculator.factorial(input));
    }
    
    @Test
    @DisplayName("Should handle large factorial calculations")
    void testFactorialLarge() {
        // Test that factorial doesn't overflow for reasonable inputs
        assertDoesNotThrow(() -> calculator.factorial(10));
        assertTrue(calculator.factorial(10) > 0);
    }
    
    /**
     * Helper method to calculate expected factorial values.
     * This is used to verify our implementation is correct.
     */
    private long calculateExpectedFactorial(int n) {
        if (n <= 1) return 1;
        long result = 1;
        for (int i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }
}
