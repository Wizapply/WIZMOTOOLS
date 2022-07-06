using System;
using System.Threading;
using wizmo;

class WIZMOTest
{
    static void Main(string[] args)
    {
        Console.WriteLine("-------- START WIZMO-TOOLS --------");

        WIZMO wm = new wizmo.WIZMO(true);
        wm.Starter("");
        wm.SetAxisProcessingMode(true);

        while (wm.UpdateState())
        {
            wm.SimplePoseUpdate(0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f);
            wm.UpdateBackLog();
            Thread.Sleep(100); //100ms
        }

        wm.Close();
        wm.UpdateBackLog();

        Console.WriteLine("-------- FINISH WIZMO-TOOLS --------");
    }
}
