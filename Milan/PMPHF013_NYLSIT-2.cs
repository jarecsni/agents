using System;

namespace PMPHF013_NYLSIT
{
    internal class PMPHF013_NYLSIT
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

        static void Main(string[] args)
        {
            int userInputX = int.Parse(Console.ReadLine());
            int userInputY = int.Parse(Console.ReadLine());
            int userInputZ = int.Parse(Console.ReadLine());

            // Math.Abs does not work with the minimum value, also the minimum value is the largest absolute value (max+1), so if one of the variables has it, can be printed straight to console to avoid an error
            if (userInputX == int.MinValue || userInputY == int.MinValue || userInputZ == int.MinValue)
            {
                Console.WriteLine(int.MinValue);
            }
            else
            {
                int result = GetLargerAbsoluteValue(GetLargerAbsoluteValue(userInputX, userInputY), userInputZ);
                Console.WriteLine(result);
            }
            Console.ReadLine();
        }
    }
}
