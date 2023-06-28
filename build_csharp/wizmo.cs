using System;
using System.Runtime.InteropServices;
using System.Threading;

namespace wizmo
{
    [StructLayout(LayoutKind.Sequential)]
    public class wizmoPacket
    {
        //Axis position controls
        public float axis1;
        public float axis2;
        public float axis3;
        public float axis4;
        public float axis5;
        public float axis6;

        //Axis speed/accel controls
        public float speed1_all;
        public float speed2;
        public float speed3;
        public float speed4;
        public float speed5;
        public float speed6;
        public float accel;

        //Axis Processing
        public float roll;
        public float pitch;
        public float yaw;
        public float heave;
        public float sway;
        public float surge;

        public float rotationMotionRatio;
        public float gravityMotionRatio;

        public int commandSendCount;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 256)]
        public string command;

        public wizmoPacket()
        {
            axis1 = 0.5f;
            axis2 = 0.5f;
            axis3 = 0.5f;
            axis4 = 0.5f;
            axis5 = 0.5f;
            axis6 = 0.5f;

            //Axis speed/accel controls
            speed1_all = 0.667f;
            speed2 = 0.667f;
            speed3 = 0.667f;
            speed4 = 0.667f;
            speed5 = 0.667f;
            speed6 = 0.667f;
            accel = 0.5f;

            //Axis Processing
            roll = 0.0f;
            pitch = 0.0f;
            yaw = 0.0f;
            heave = 0.0f;
            sway = 0.0f;
            surge = 0.0f;

            rotationMotionRatio = 0.8f;
            gravityMotionRatio = 0.8f;

            commandSendCount = 0;
            command = "";
        }
    }

    public class WIZMO
    {
        //Serial
        public string appPassCode = "";

        #region WIZMO DLL IMPORTER
        [DllImport("wizmo", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoOpen(string serialNo);
        [DllImport("wizmo", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoOpenSerialAssign(string appCode, string assign);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoClose(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoGetState(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern int wizmoGetDevice(int handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern void wizmoWrite(Int32 handle, wizmoPacket packet);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern void wizmoSetAxisProcessingMode(Int32 handle, Int32 flag);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern void wizmoSetVariableGainMode(Int32 handle, Int32 flag);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern void wizmoSetOriginMode(Int32 handle, Int32 flag);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        [return: MarshalAs(UnmanagedType.U1)]
        static extern Int32 wizmoGetOriginMode(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        [return: MarshalAs(UnmanagedType.U1)]
        static extern Int32 wizmoGetAxisProcessingMode(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        [return: MarshalAs(UnmanagedType.U1)]
        static extern Int32 wizmoGetVariableGainMode(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern System.IntPtr wizmoGetAppCode(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoGetStatusEXT4(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern System.IntPtr wizmoGetVersion(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        [return: MarshalAs(UnmanagedType.U1)]
        static extern Int32 wizmoIsRunning(Int32 handle);

        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoGetBackLog(byte[] str, Int32 str_size);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoBackLogDataAvailable();
        #endregion

        static string? wizmoGetAppCadeString(int handle)
        {
            // Receive the pointer to Unicde character array
            System.IntPtr pStr = wizmoGetAppCode(handle);
            // Construct a string from the pointer.
            return Marshal.PtrToStringAnsi(pStr);
        }

        public enum wizmoState : int {
            CanNotFindUsb = 0,
            CanNotFindSimvr = 1,
            CanNotCalibration = 2,
            TimeoutCalibration = 3,
            ShutDownActuator = 4,
            CanNotCertificate = 5,
            Initial = 6,
            Running = 7,
            StopActuator = 8,
            CalibrationRetry = 9,
        }

        private bool g_verbose;
        private bool g_wizmoIsOpen;
        private wizmoPacket g_simplePacket;
        private int g_wizmoHandle;

        public WIZMO(bool verbose)
        {
            g_wizmoIsOpen = false;
            g_verbose = verbose;
            g_simplePacket = new wizmoPacket();

            if (verbose)
                Console.WriteLine("LOADED WIZMO DLL.");

            g_wizmoHandle = -1;
        }

        public void Starter(string appCode, string serialAssign)
        {
            if (g_wizmoIsOpen)
                return;

            appPassCode = appCode;
            g_wizmoHandle = wizmoOpenSerialAssign(appPassCode, serialAssign);
            if (g_wizmoHandle >= 0)
            {
                if (g_verbose)
                    Console.WriteLine("STARTED WIZMO.");

                g_wizmoIsOpen = true;
            }
            else
            {
                if (g_verbose)
                {
                    Console.WriteLine("WIZMO OPEN ERROR!");
                }
            }
        }

        public void Starter(string appCode)
        {
            Starter(appCode, "");
        }

        public void Close()
        {
            if (!g_wizmoIsOpen)
                return;

            wizmoClose(g_wizmoHandle);
            g_wizmoIsOpen = false;
        }

        public string UpdateBackLog()
        {
            string resultString = "";
            var size = wizmoBackLogDataAvailable();

            if (size > 0)
            {
                byte[] dataArray = new byte[size];
                int iRet = wizmoGetBackLog(dataArray, size);

                if (iRet <= 0 || dataArray == null) //Error
                    return resultString;

                //for debug Log
                resultString = System.Text.Encoding.UTF8.GetString(dataArray, 0, iRet);
            }

            if (g_verbose && resultString != "")
                Console.Write(resultString);

            return resultString;
        }

        public int GetStatus()
        {
            return (int)wizmoGetState(g_wizmoHandle);
        }

        public bool IsRunning()
        {
            return wizmoIsRunning(g_wizmoHandle) != 0;
        }

        public void SimplePoseUpdate(float roll, float pitch, float yaw, float heave, float sway, float surge)
        {
            if (!g_wizmoIsOpen)
                return;

            g_simplePacket.roll = roll;
            g_simplePacket.pitch = pitch;
            g_simplePacket.yaw = yaw;
            g_simplePacket.heave = heave;
            g_simplePacket.sway = sway;
            g_simplePacket.surge = surge;
            wizmoWrite(g_wizmoHandle, g_simplePacket);
        }

        public void SimpleMotionRatioUpdate(float rotation, float gravity)
        {
            if (!g_wizmoIsOpen)
                return;

            g_simplePacket.rotationMotionRatio = rotation;
            g_simplePacket.gravityMotionRatio = gravity;
            wizmoWrite(g_wizmoHandle, g_simplePacket);

        }
        public void SimpleMotionPowerUpdate(float accel, float speed)
        {
            if (!g_wizmoIsOpen)
                return;

            g_simplePacket.accel = accel;
            g_simplePacket.speed1_all = speed;
            wizmoWrite(g_wizmoHandle, g_simplePacket);
        }
        public void PacketUpdate(wizmoPacket packet)
        {
            if (!g_wizmoIsOpen)
                return;

            wizmoWrite(g_wizmoHandle,packet);
        }

        public void SetOriginMode(bool value)
        {
            wizmoSetOriginMode(g_wizmoHandle, Convert.ToInt32(value));
        }
        public void SetAxisProcessingMode(bool value)
        {
            wizmoSetAxisProcessingMode(g_wizmoHandle, Convert.ToInt32(value));
        }
        public void SetVariableGainMode(bool value)
        {
            wizmoSetVariableGainMode(g_wizmoHandle, Convert.ToInt32(value));
        }

        public bool GetOriginMode()
        {
            return wizmoGetOriginMode(g_wizmoHandle) != 0;
        }
        public bool GetAxisProcessingMode()
        {
            return wizmoGetAxisProcessingMode(g_wizmoHandle) != 0;
        }
        public bool GetVariableGainMode()
        {
            return wizmoGetVariableGainMode(g_wizmoHandle) != 0;
        }

        public string GetDeviceName()
        {
            //wizmo_state.h -> WIZMODevice
            string res = "NONE";
            switch(wizmoGetDevice(g_wizmoHandle)){
                case 1: res = "SIMVR4DOF";
                    break;
                case 2: res = "SIMVR6DOF";
                    break;
                case 3: res = "SIMVR6DOF_MASSIVE";
                    break;
                case 4: res = "ANTSEAT";
                    break;
                case 0:
                default:
                    res = "NONE";
                    break;
            }

            return res;
        }
    }
}
