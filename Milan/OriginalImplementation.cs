using System;

namespace PMPHF013_NYLSIT_Original
{
    internal class OriginalImplementation
    {
        static int FindLargestAbsoluteValue(int userInputX, int userInputY, int userInputZ)
        {
            // Math.Abs does not work with the minimum value, also the minimum value is the largest absolute value (max+1), so if one of the variables has it, can be printed straight to console to avoid an error
            if(userInputX == int.MinValue || userInputY == int.MinValue || userInputZ == int.MinValue)
            {
                return int.MinValue;
            }
            else
            {
                if (Math.Abs(userInputX) > Math.Abs(userInputY))
                {
                    if (Math.Abs(userInputX) > Math.Abs(userInputZ))
                    {
                        //in this case x abs is larger (not equal to) than both y and z so can be printed right away
                        return userInputX;
                    }
                    else
                    {
                        if (Math.Abs(userInputZ) > Math.Abs(userInputX))
                        {
                            return userInputZ;
                        }
                        else
                        {
                            if (userInputX > userInputZ)
                            {
                                return userInputX;
                            }
                            else
                            {
                                return userInputZ;
                            }
                        }
                    }
                }
                else
                {
                    if (Math.Abs(userInputY) > Math.Abs(userInputX))
                    {
                        if (Math.Abs(userInputY) > Math.Abs(userInputZ))
                        {
                            return userInputY;
                        }
                        else
                        {
                            if (Math.Abs(userInputZ) > Math.Abs(userInputY))
                            {
                                return userInputZ;
                            }
                            else
                            {
                                if (userInputY > userInputZ)
                                {
                                    return userInputY;
                                }
                                else
                                {
                                    return userInputZ;
                                }
                            }
                        }
                    }
                    else
                    {
                        if (userInputX > userInputY)
                        {
                            if (Math.Abs(userInputZ) > Math.Abs(userInputX))
                            {
                                return userInputZ;
                            }
                            else
                            {
                                return userInputX;
                            }
                        }
                        else
                        {
                            if (Math.Abs(userInputZ) > Math.Abs(userInputY))
                            {
                                return userInputZ;
                            }
                            else
                            {
                                if (Math.Abs(userInputY) > Math.Abs(userInputZ))
                                {
                                    return userInputY;
                                }
                                else
                                {
                                    if (userInputY > userInputZ)
                                    {
                                        return userInputY;
                                    }
                                    else
                                    {
                                        return userInputZ;
                                    }
                                }
                            }
                        }
                    }
                }
            }
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
                Console.WriteLine("[FAIL] " + testName + " *** BUG FOUND! ***");
                Console.WriteLine("  Input: x=" + x + ", y=" + y + ", z=" + z);
                Console.WriteLine("  Expected: " + expected);
                Console.WriteLine("  Got: " + result);
            }
        }

        static void Main(string[] args)
        {
            Console.WriteLine("=== Testing Original Implementation ===");
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
            Console.WriteLine();

            // Edge case: All equal
            Console.WriteLine("--- All Equal Cases ---");
            RunTest("All equal positive", 5, 5, 5, 5);
            RunTest("All equal negative", -5, -5, -5, -5);
            RunTest("All zero", 0, 0, 0, 0);
            Console.WriteLine();

            // Edge case: Two equal absolute values - TIE-BREAKING TESTS
            Console.WriteLine("--- Two Equal Absolute Values (Tie-Breaking) ---");
            RunTest("Positive wins: 10, -10, 5", 10, -10, 5, 10);
            RunTest("Positive wins: -10, 10, 5", -10, 10, 5, 10);
            RunTest("Positive wins: 5, 10, -10", 5, 10, -10, 10);
            RunTest("Positive wins: 5, -10, 10", 5, -10, 10, 10);
            RunTest("Two negative same abs", -10, -10, 5, -10);
            RunTest("Two positive same abs", 10, 10, -5, 10);
            Console.WriteLine();

            // Three-way tie with mixed signs
            Console.WriteLine("--- Three-Way Tie Cases ---");
            RunTest("Three-way: -10, -10, 10", -10, -10, 10, 10);
            RunTest("Three-way: 10, -10, -10", 10, -10, -10, 10);
            RunTest("Three-way: -10, 10, -10", -10, 10, -10, 10);
            RunTest("Three-way: 10, 10, 10", 10, 10, 10, 10);
            RunTest("Three-way: -10, -10, -10", -10, -10, -10, -10);
            Console.WriteLine();

            // Edge case: Zero values
            Console.WriteLine("--- Zero Value Cases ---");
            RunTest("One zero, two positive", 0, 5, 10, 10);
            RunTest("One zero, two negative", 0, -5, -10, -10);
            RunTest("Two zeros, one positive", 0, 0, 10, 10);
            RunTest("Two zeros, one negative", 0, 0, -10, -10);
            Console.WriteLine();

            Console.WriteLine("=== Original Implementation Test Complete ===");
            Console.ReadLine();
        }
    }
}

