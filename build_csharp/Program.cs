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
        wm.SetAxisProcessingMode(WizmoAxisMode.AXIS_MODE_GLOBALPOSE);
        wm.SimpleMotionPowerUpdate(0.02f,0.666f);

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
