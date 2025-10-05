namespace PMPHF013_NYLSIT
{
    internal class PMPHF013_NYLSIT
    {
        static void Main(string[] args)
        {
            int userInputX = int.Parse(Console.ReadLine());
            int userInputY = int.Parse(Console.ReadLine());
            int userInputZ = int.Parse(Console.ReadLine());
            // Math.Abs does not work with the minimum value, also the minimum value is the largest absolute value (max+1), so if one of the variables has it, can be printed straight to console to avoid an error
            if(userInputX == int.MinValue || userInputY == int.MinValue || userInputZ == int.MinValue)
            {
                Console.WriteLine(int.MinValue);
            }
            else
            {
                if (Math.Abs(userInputX) > Math.Abs(userInputY))
                {
                    if (Math.Abs(userInputX) > Math.Abs(userInputZ))
                    {
                        //in this case x abs is larger (not equal to) than both y and z so can be printed right away
                        Console.WriteLine(userInputX);
                    }
                    else
                    {
                        if (Math.Abs(userInputZ) > Math.Abs(userInputX))
                        {
                            Console.WriteLine(userInputZ);
                        }
                        else
                        {
                            if (userInputX > userInputZ)
                            {
                                Console.WriteLine(userInputX);
                            }
                            else
                            {
                                Console.WriteLine(userInputZ);
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
                            Console.WriteLine(userInputY);
                        }
                        else
                        {
                            if (Math.Abs(userInputZ) > Math.Abs(userInputY))
                            {
                                Console.WriteLine(userInputZ);
                            }
                            else
                            {
                                if (userInputY > userInputZ)
                                {
                                    Console.WriteLine(userInputY);
                                }
                                else
                                {
                                    Console.WriteLine(userInputZ);
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
                                Console.WriteLine(userInputZ);
                            }
                            else
                            {
                                Console.WriteLine(userInputX);
                            }
                        }
                        else
                        {
                            if (Math.Abs(userInputZ) > Math.Abs(userInputY))
                            {
                                Console.WriteLine(userInputZ);
                            }
                            else
                            {
                                if (Math.Abs(userInputY) > Math.Abs(userInputZ))
                                {
                                    Console.WriteLine(userInputY);
                                }
                                else
                                {
                                    if (userInputY > userInputZ)
                                    {
                                        Console.WriteLine(userInputY);
                                    }
                                    else
                                    {
                                        Console.WriteLine(userInputZ);
                                    }
                                }
                            }
                        }
                    }
                }
            }
            Console.ReadLine();
        }
    }
}
