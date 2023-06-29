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

        Thread.Sleep(3000);	//3s wait

        while (wm.IsRunning())
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
