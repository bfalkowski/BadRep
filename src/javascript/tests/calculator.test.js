/**
 * Unit tests for the Calculator class.
 * 
 * Tests all arithmetic operations and edge cases using Jest.
 */

const Calculator = require('../src/calculator');

describe('Calculator', () => {
    let calculator;

    beforeEach(() => {
        calculator = new Calculator();
    });

    describe('Basic Operations', () => {
        describe('add', () => {
            test('should add two positive numbers correctly', () => {
                expect(calculator.add(2, 3)).toBe(5);
                expect(calculator.add(7, 3)).toBe(10);
            });

            test('should add negative numbers correctly', () => {
                expect(calculator.add(-3, 2)).toBe(-1);
                expect(calculator.add(-2, -3)).toBe(-5);
            });

            test('should add zero correctly', () => {
                expect(calculator.add(5, 0)).toBe(5);
                expect(calculator.add(0, 3)).toBe(3);
            });

            test('should handle floating point numbers', () => {
                expect(calculator.add(2.5, 3.5)).toBe(6);
                expect(calculator.add(1.1, 2.2)).toBeCloseTo(3.3, 10);
            });
        });

        describe('subtract', () => {
            test('should subtract two numbers correctly', () => {
                expect(calculator.subtract(5, 3)).toBe(2);
                expect(calculator.subtract(3, 5)).toBe(-2);
            });

            test('should subtract zero correctly', () => {
                expect(calculator.subtract(5, 0)).toBe(5);
                expect(calculator.subtract(0, 3)).toBe(-3);
            });

            test('should handle floating point numbers', () => {
                expect(calculator.subtract(5.5, 2.5)).toBe(3);
                expect(calculator.subtract(3.3, 1.1)).toBeCloseTo(2.2, 10);
            });
        });

        describe('multiply', () => {
            test('should multiply two numbers correctly', () => {
                expect(calculator.multiply(3, 5)).toBe(15);
                expect(calculator.multiply(3, -5)).toBe(-15);
            });

            test('should multiply by zero correctly', () => {
                expect(calculator.multiply(5, 0)).toBe(0);
                expect(calculator.multiply(0, 5)).toBe(0);
            });

            test('should handle floating point numbers', () => {
                expect(calculator.multiply(2.5, 3)).toBe(7.5);
                expect(calculator.multiply(1.5, 2.5)).toBe(3.75);
            });
        });

        describe('divide', () => {
            test('should divide two numbers correctly', () => {
                expect(calculator.divide(5, 2)).toBe(2.5);
                expect(calculator.divide(-5, 2)).toBe(-2.5);
            });

            test('should handle floating point numbers', () => {
                expect(calculator.divide(5.5, 2)).toBe(2.75);
                expect(calculator.divide(3.3, 1.1)).toBeCloseTo(3, 10);
            });

            test('should throw error when dividing by zero', () => {
                expect(() => calculator.divide(5, 0)).toThrow('Division by zero');
                expect(() => calculator.divide(0, 0)).toThrow('Division by zero');
            });
        });
    });

    describe('Advanced Operations', () => {
        describe('power', () => {
            test('should calculate power correctly', () => {
                expect(calculator.power(2, 3)).toBe(8);
                expect(calculator.power(5, 0)).toBe(1);
                expect(calculator.power(3, 2)).toBe(9);
            });

            test('should handle negative exponents', () => {
                expect(calculator.power(2, -2)).toBe(0.25);
                expect(calculator.power(4, -1)).toBe(0.25);
            });

            test('should handle floating point numbers', () => {
                expect(calculator.power(2.5, 2)).toBe(6.25);
                expect(calculator.power(4, 0.5)).toBe(2);
            });
        });

        describe('sqrt', () => {
            test('should calculate square root correctly', () => {
                expect(calculator.sqrt(16)).toBe(4);
                expect(calculator.sqrt(0)).toBe(0);
                expect(calculator.sqrt(25)).toBe(5);
            });

            test('should handle floating point numbers', () => {
                expect(calculator.sqrt(16.0)).toBe(4);
                expect(calculator.sqrt(2.25)).toBe(1.5);
            });

            test('should throw error for negative numbers', () => {
                expect(() => calculator.sqrt(-1)).toThrow('Cannot calculate square root of negative number');
                expect(() => calculator.sqrt(-16)).toThrow('Cannot calculate square root of negative number');
            });
        });

        describe('factorial', () => {
            test('should calculate factorial for valid inputs', () => {
                expect(calculator.factorial(0)).toBe(1);
                expect(calculator.factorial(1)).toBe(1);
                expect(calculator.factorial(2)).toBe(2);
                expect(calculator.factorial(3)).toBe(6);
                expect(calculator.factorial(4)).toBe(24);
                expect(calculator.factorial(5)).toBe(120);
            });

            test('should throw error for negative numbers', () => {
                expect(() => calculator.factorial(-1)).toThrow('Factorial is not defined for negative numbers');
                expect(() => calculator.factorial(-5)).toThrow('Factorial is not defined for negative numbers');
            });

            test('should handle large factorials', () => {
                expect(calculator.factorial(10)).toBe(3628800);
            });
        });

        describe('modulo', () => {
            test('should calculate modulo correctly', () => {
                expect(calculator.modulo(17, 5)).toBe(2);
                expect(calculator.modulo(10, 3)).toBe(1);
                expect(calculator.modulo(8, 4)).toBe(0);
            });

            test('should handle negative numbers', () => {
                expect(calculator.modulo(-17, 5)).toBe(-2);
                expect(calculator.modulo(17, -5)).toBe(2);
            });

            test('should handle floating point numbers', () => {
                expect(calculator.modulo(17.5, 5)).toBe(2.5);
                expect(calculator.modulo(10.7, 3)).toBeCloseTo(1.7, 10);
            });

            test('should throw error when modulo by zero', () => {
                expect(() => calculator.modulo(5, 0)).toThrow('Modulo by zero');
            });
        });

        describe('absolute', () => {
            test('should calculate absolute value correctly', () => {
                expect(calculator.absolute(7)).toBe(7);
                expect(calculator.absolute(-7)).toBe(7);
                expect(calculator.absolute(0)).toBe(0);
            });

            test('should handle floating point numbers', () => {
                expect(calculator.absolute(3.14)).toBe(3.14);
                expect(calculator.absolute(-2.718)).toBe(2.718);
            });
        });

        describe('roundNumber', () => {
            test('should round numbers correctly', () => {
                expect(calculator.roundNumber(3.14159)).toBe(3);
                expect(calculator.roundNumber(3.14159, 2)).toBe(3.14);
                expect(calculator.roundNumber(3.14159, 4)).toBe(3.1416);
            });

            test('should handle negative numbers', () => {
                expect(calculator.roundNumber(-3.7)).toBe(-4);
                expect(calculator.roundNumber(-3.14159, 2)).toBe(-3.14);
            });

                    test('should use default decimals when not specified', () => {
            expect(calculator.roundNumber(3.14159)).toBe(3);
            expect(calculator.roundNumber(2.5)).toBe(3); // 2.5 rounds to 3
        });
        });
    });

    describe('Mathematical Operations', () => {
        describe('gcd', () => {
            test('should calculate greatest common divisor correctly', () => {
                expect(calculator.gcd(48, 18)).toBe(6);
                expect(calculator.gcd(12, 18)).toBe(6);
                expect(calculator.gcd(7, 13)).toBe(1);
            });

            test('should handle negative numbers', () => {
                expect(calculator.gcd(-48, 18)).toBe(6);
                expect(calculator.gcd(48, -18)).toBe(6);
                expect(calculator.gcd(-48, -18)).toBe(6);
            });

            test('should handle zero', () => {
                expect(calculator.gcd(0, 5)).toBe(5);
                expect(calculator.gcd(5, 0)).toBe(5);
                expect(calculator.gcd(0, 0)).toBe(0);
            });
        });

        describe('lcm', () => {
            test('should calculate least common multiple correctly', () => {
                expect(calculator.lcm(12, 18)).toBe(36);
                expect(calculator.lcm(8, 12)).toBe(24);
                expect(calculator.lcm(5, 7)).toBe(35);
            });

            test('should handle negative numbers', () => {
                expect(calculator.lcm(-12, 18)).toBe(36);
                expect(calculator.lcm(12, -18)).toBe(36);
            });

            test('should handle zero', () => {
                expect(calculator.lcm(0, 5)).toBe(0);
                expect(calculator.lcm(5, 0)).toBe(0);
            });
        });

        describe('isPrime', () => {
            test('should identify prime numbers correctly', () => {
                expect(calculator.isPrime(2)).toBe(true);
                expect(calculator.isPrime(3)).toBe(true);
                expect(calculator.isPrime(5)).toBe(true);
                expect(calculator.isPrime(7)).toBe(true);
                expect(calculator.isPrime(11)).toBe(true);
                expect(calculator.isPrime(13)).toBe(true);
                expect(calculator.isPrime(17)).toBe(true);
            });

            test('should identify non-prime numbers correctly', () => {
                expect(calculator.isPrime(1)).toBe(false);
                expect(calculator.isPrime(4)).toBe(false);
                expect(calculator.isPrime(6)).toBe(false);
                expect(calculator.isPrime(8)).toBe(false);
                expect(calculator.isPrime(9)).toBe(false);
                expect(calculator.isPrime(10)).toBe(false);
                expect(calculator.isPrime(12)).toBe(false);
            });

            test('should handle edge cases', () => {
                expect(calculator.isPrime(0)).toBe(false);
                expect(calculator.isPrime(-1)).toBe(false);
                expect(calculator.isPrime(-5)).toBe(false);
            });
        });
    });

    describe('Edge Cases', () => {
        test('should handle very large numbers', () => {
            expect(calculator.add(1e10, 1e10)).toBe(2e10);
            expect(calculator.multiply(1e5, 1e5)).toBe(1e10);
        });

        test('should handle very small numbers', () => {
            expect(calculator.add(1e-10, 1e-10)).toBe(2e-10);
            expect(calculator.multiply(1e-5, 1e-5)).toBeCloseTo(1e-10, 10);
        });

        test('should handle zero operations', () => {
            expect(calculator.add(0, 0)).toBe(0);
            expect(calculator.multiply(0, 0)).toBe(0);
            expect(calculator.power(0, 1)).toBe(0);
            expect(calculator.absolute(0)).toBe(0);
        });

        test('should handle infinity and NaN', () => {
            expect(calculator.add(Infinity, 5)).toBe(Infinity);
            expect(calculator.multiply(Infinity, 0)).toBeNaN();
            // Division by zero throws an error in our implementation
            expect(() => calculator.divide(1, 0)).toThrow('Division by zero');
        });
    });

    describe('Integration Tests', () => {
        test('should handle complex calculations', () => {
            // Calculate: (5 + 3) * 2 - 4 / 2
            const result = calculator.subtract(
                calculator.multiply(
                    calculator.add(5, 3), 2
                ),
                calculator.divide(4, 2)
            );
            const expected = (5 + 3) * 2 - 4 / 2;
            expect(result).toBe(expected);
        });

        test('should handle factorial chains', () => {
            // Calculate: 5! + 3! - 2!
            const result = calculator.add(
                calculator.factorial(5),
                calculator.subtract(
                    calculator.factorial(3),
                    calculator.factorial(2)
                )
            );
            const expected = 120 + 6 - 2;
            expect(result).toBe(expected);
        });

        test('should handle power and square root together', () => {
            // Calculate: √(2^8 + 3^2)
            const result = calculator.sqrt(
                calculator.add(
                    calculator.power(2, 8),
                    calculator.power(3, 2)
                )
            );
            const expected = Math.sqrt(2**8 + 3**2);
            expect(result).toBe(expected);
        });
    });

    describe('Type Safety', () => {
        test('should handle string inputs gracefully', () => {
            expect(calculator.add('5', '3')).toBe('53'); // String concatenation in JS
            expect(calculator.multiply('2', '3')).toBe(6); // String * number = number
        });

        test('should handle mixed type inputs', () => {
            expect(calculator.add('5', 3)).toBe('53'); // String + number = string
            expect(calculator.multiply(2, '3')).toBe(6); // Number * string = number
        });

        test('should handle boolean inputs', () => {
            expect(calculator.add(true, false)).toBe(1);
            expect(calculator.multiply(true, 5)).toBe(5);
        });
    });
});
