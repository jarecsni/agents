using System;

namespace PMPHF013_NYLSIT_Tests
{
    internal class TestHarness
    {
        static int GetLargerAbsoluteValue(int a, int b)
        {
            if (Math.Abs(a) > Math.Abs(b))
            {
                return a;
            }
            if (Math.Abs(b) > Math.Abs(a))
            {
                return b;
            }
            // Absolute values are equal, return the larger actual value
            if (a > b)
            {
                return a;
            }
            return b;
        }

        static int FindLargestAbsoluteValue(int x, int y, int z)
        {
            // Math.Abs does not work with the minimum value, also the minimum value is the largest absolute value (max+1)
            if (x == int.MinValue || y == int.MinValue || z == int.MinValue)
            {
                return int.MinValue;
            }
            
            return GetLargerAbsoluteValue(GetLargerAbsoluteValue(x, y), z);
        }

        static void RunTest(string testName, int x, int y, int z, int expected)
        {
            int result = FindLargestAbsoluteValue(x, y, z);
            if (result == expected)
            {
                Console.WriteLine("[PASS] " + testName);
            }
            else
            {
                Console.WriteLine("[FAIL] " + testName);
                Console.WriteLine("  Input: x=" + x + ", y=" + y + ", z=" + z);
                Console.WriteLine("  Expected: " + expected);
                Console.WriteLine("  Got: " + result);
            }
        }

        static void Main(string[] args)
        {
            Console.WriteLine("=== Running Test Harness for PMPHF013 ===");
            Console.WriteLine();

            // Test cases from specification
            Console.WriteLine("--- Specification Test Cases ---");
            RunTest("Spec Test 1", 54, -17, 49, 54);
            RunTest("Spec Test 2", 10, 10, -10, 10);
            RunTest("Spec Test 3", -418640383, -36421470, -1189722754, -1189722754);
            Console.WriteLine();

            // Edge case: int.MinValue
            Console.WriteLine("--- int.MinValue Edge Cases ---");
            RunTest("int.MinValue in X", int.MinValue, 100, 200, int.MinValue);
            RunTest("int.MinValue in Y", 100, int.MinValue, 200, int.MinValue);
            RunTest("int.MinValue in Z", 100, 200, int.MinValue, int.MinValue);
            RunTest("All int.MinValue", int.MinValue, int.MinValue, int.MinValue, int.MinValue);
            Console.WriteLine();

            // Edge case: int.MaxValue
            Console.WriteLine("--- int.MaxValue Edge Cases ---");
            RunTest("int.MaxValue in X", int.MaxValue, 100, 200, int.MaxValue);
            RunTest("int.MaxValue in Y", 100, int.MaxValue, 200, int.MaxValue);
            RunTest("int.MaxValue in Z", 100, 200, int.MaxValue, int.MaxValue);
            RunTest("All int.MaxValue", int.MaxValue, int.MaxValue, int.MaxValue, int.MaxValue);
            Console.WriteLine();

            // Edge case: All equal
            Console.WriteLine("--- All Equal Cases ---");
            RunTest("All equal positive", 5, 5, 5, 5);
            RunTest("All equal negative", -5, -5, -5, -5);
            RunTest("All zero", 0, 0, 0, 0);
            Console.WriteLine();

            // Edge case: Two equal absolute values
            Console.WriteLine("--- Two Equal Absolute Values (Tie-Breaking) ---");
            RunTest("Positive wins over negative (X,Y)", 10, -10, 5, 10);
            RunTest("Positive wins over negative (X,Z)", 10, 5, -10, 10);
            RunTest("Positive wins over negative (Y,Z)", 5, 10, -10, 10);
            RunTest("Two negative same abs", -10, -10, 5, -10);
            RunTest("Two positive same abs", 10, 10, -5, 10);
            Console.WriteLine();

            // Edge case: Zero values
            Console.WriteLine("--- Zero Value Cases ---");
            RunTest("One zero, two positive", 0, 5, 10, 10);
            RunTest("One zero, two negative", 0, -5, -10, -10);
            RunTest("Two zeros, one positive", 0, 0, 10, 10);
            RunTest("Two zeros, one negative", 0, 0, -10, -10);
            Console.WriteLine();

            // Edge case: Mixed positive and negative
            Console.WriteLine("--- Mixed Positive and Negative ---");
            RunTest("Large negative wins", 5, -100, 50, -100);
            RunTest("Large positive wins", 100, -50, 25, 100);
            RunTest("Negative with largest abs", -1000, 500, 250, -1000);
            Console.WriteLine();

            // Edge case: Same absolute value, different signs
            Console.WriteLine("--- Same Absolute Value, Different Signs ---");
            RunTest("15 vs -15 vs 10", 15, -15, 10, 15);
            RunTest("-15 vs 15 vs 10", -15, 15, 10, 15);
            RunTest("10 vs 15 vs -15", 10, 15, -15, 15);
            RunTest("All same abs, one positive", -20, -20, 20, 20);
            Console.WriteLine();

            // Edge case: Sequential values
            Console.WriteLine("--- Sequential and Close Values ---");
            RunTest("Sequential 1,2,3", 1, 2, 3, 3);
            RunTest("Sequential -1,-2,-3", -1, -2, -3, -3);
            RunTest("Close values", 100, 101, 99, 101);
            Console.WriteLine();

            // Edge case: One very large, others small
            Console.WriteLine("--- One Dominant Value ---");
            RunTest("X dominates", 1000000, 1, 2, 1000000);
            RunTest("Y dominates", 1, 1000000, 2, 1000000);
            RunTest("Z dominates", 1, 2, 1000000, 1000000);
            RunTest("Negative dominates", -1000000, 100, 200, -1000000);
            Console.WriteLine();

            Console.WriteLine("=== Test Harness Complete ===");
            Console.ReadLine();
        }
    }
}

