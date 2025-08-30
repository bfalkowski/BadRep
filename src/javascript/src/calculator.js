#!/usr/bin/env node
/**
 * Calculator module for ReviewLab baseline project.
 * 
 * A simple calculator implementation that serves as a baseline project
 * for bug injection testing.
 */

/**
 * A simple calculator class for basic arithmetic operations.
 * 
 * This serves as a baseline project for bug injection testing.
 */
class Calculator {
    /**
     * Initialize the calculator.
     */
    constructor() {
        // No initialization needed for this simple calculator
    }

    /**
     * Add two numbers.
     * 
     * @param {number} a - The first number
     * @param {number} b - The second number
     * @returns {number} The sum of a and b
     */
    add(a, b) {
        return a + b;
    }

    /**
     * Subtract the second number from the first.
     * 
     * @param {number} a - The first number
     * @param {number} b - The second number
     * @returns {number} The difference of a and b
     */
    subtract(a, b) {
        return a - b;
    }

    /**
     * Multiply two numbers.
     * 
     * @param {number} a - The first number
     * @param {number} b - The second number
     * @returns {number} The product of a and b
     */
    multiply(a, b) {
        return a * b;
    }

    /**
     * Divide the first number by the second.
     * 
     * @param {number} a - The dividend
     * @param {number} b - The divisor
     * @returns {number} The quotient of a divided by b
     * @throws {Error} If b is zero
     */
    divide(a, b) {
        if (b === 0) {
            throw new Error('Division by zero');
        }
        return a / b;
    }

    /**
     * Calculate the power of a number.
     * 
     * @param {number} base - The base number
     * @param {number} exponent - The exponent
     * @returns {number} base raised to the power of exponent
     */
    power(base, exponent) {
        return Math.pow(base, exponent);
    }

    /**
     * Calculate the square root of a number.
     * 
     * @param {number} number - The number to find the square root of
     * @returns {number} The square root of the number
     * @throws {Error} If number is negative
     */
    sqrt(number) {
        if (number < 0) {
            throw new Error('Cannot calculate square root of negative number');
        }
        return Math.sqrt(number);
    }

    /**
     * Calculate the factorial of a non-negative integer.
     * 
     * @param {number} n - The number to calculate factorial for
     * @returns {number} The factorial of n
     * @throws {Error} If n is negative
     */
    factorial(n) {
        if (n < 0) {
            throw new Error('Factorial is not defined for negative numbers');
        }
        if (n === 0 || n === 1) {
            return 1;
        }

        let result = 1;
        for (let i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }

    /**
     * Calculate the modulo of two numbers.
     * 
     * @param {number} a - The dividend
     * @param {number} b - The divisor
     * @returns {number} The remainder of a divided by b
     * @throws {Error} If b is zero
     */
    modulo(a, b) {
        if (b === 0) {
            throw new Error('Modulo by zero');
        }
        return a % b;
    }

    /**
     * Calculate the absolute value of a number.
     * 
     * @param {number} number - The number to find the absolute value of
     * @returns {number} The absolute value of the number
     */
    absolute(number) {
        return Math.abs(number);
    }

    /**
     * Round a number to a specified number of decimal places.
     * 
     * @param {number} number - The number to round
     * @param {number} decimals - Number of decimal places (default: 0)
     * @returns {number} The rounded number
     */
    roundNumber(number, decimals = 0) {
        const factor = Math.pow(10, decimals);
        return Math.round(number * factor) / factor;
    }

    /**
     * Calculate the greatest common divisor of two numbers.
     * 
     * @param {number} a - The first number
     * @param {number} b - The second number
     * @returns {number} The greatest common divisor
     */
    gcd(a, b) {
        a = Math.abs(a);
        b = Math.abs(b);
        
        while (b !== 0) {
            const temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    /**
     * Calculate the least common multiple of two numbers.
     * 
     * @param {number} a - The first number
     * @param {number} b - The second number
     * @returns {number} The least common multiple
     */
    lcm(a, b) {
        return Math.abs(a * b) / this.gcd(a, b);
    }

    /**
     * Check if a number is prime.
     * 
     * @param {number} n - The number to check
     * @returns {boolean} True if the number is prime, false otherwise
     */
    isPrime(n) {
        if (n < 2) return false;
        if (n === 2) return true;
        if (n % 2 === 0) return false;
        
        for (let i = 3; i <= Math.sqrt(n); i += 2) {
            if (n % i === 0) return false;
        }
        return true;
    }
}

/**
 * Main function to run the calculator as a standalone application.
 */
function main() {
    const calc = new Calculator();
    
    console.log('ReviewLab Calculator - Baseline Project');
    console.log('=====================================');
    
    // Test basic operations
    console.log(`5 + 3 = ${calc.add(5, 3)}`);
    console.log(`10 - 4 = ${calc.subtract(10, 4)}`);
    console.log(`6 * 7 = ${calc.multiply(6, 7)}`);
    console.log(`15 / 3 = ${calc.divide(15, 3)}`);
    
    // Test advanced operations
    console.log(`2^8 = ${calc.power(2, 8)}`);
    console.log(`√16 = ${calc.sqrt(16)}`);
    console.log(`5! = ${calc.factorial(5)}`);
    console.log(`17 % 5 = ${calc.modulo(17, 5)}`);
    console.log(`|-7| = ${calc.absolute(-7)}`);
    console.log(`3.14159 rounded to 2 decimals = ${calc.roundNumber(3.14159, 2)}`);
    
    // Test additional operations
    console.log(`GCD(48, 18) = ${calc.gcd(48, 18)}`);
    console.log(`LCM(12, 18) = ${calc.lcm(12, 18)}`);
    console.log(`Is 17 prime? ${calc.isPrime(17)}`);
    console.log(`Is 24 prime? ${calc.isPrime(24)}`);
}

// Export for use in tests
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Calculator;
}

// Run main function if this file is executed directly
if (require.main === module) {
    main();
}
