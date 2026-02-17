using System;
using System.Runtime.InteropServices;

namespace wizmo
{
    /// <summary>
    /// デバイスの状態を表す列挙型
    /// wizmo_state.h -> State に対応
    /// </summary>
    public enum WizmoState : int
    {
        CanNotFindUsb = 0,  // USB 未接続
        CanNotFindWizmo = 1,  // WIZMO 未接続
        CanNotCalibration = 2,  // キャリブレーション起動失敗
        TimeoutCalibration = 3,  // キャリブレーション中の失敗
        ShutDownActuator = 4,  // アクチュエータ停止
        CanNotCertificate = 5,  // 認証失敗
        Initial = 6,  // 初期状態
        Running = 7,  // 動作中
        StopActuator = 8,  // アクチュエータ一部停止
        CalibrationRetry = 9,  // キャリブレーション再設定
    }

    /// <summary>
    /// 接続されているデバイスの種類を表す列挙型
    /// wizmo_state.h -> WIZMODevice に対応
    /// </summary>
    public enum WizmoDevice : int
    {
        NONE = 0,
        SIMVR4DOF = 1,
        SIMVR6DOF = 2,
        SIMVR6DOF_MASSIVE = 3,
        SIMVRDRIVEX = 4,
        ANTSEAT = 5,
        SIMVRMASSIVE_KV = 6,
        SIMVR2DOF_KV = 7,
        SIMVR2DOF = 8,
        SIMVRKICKBOARD_KV = 9,
    }

    /// <summary>
    /// 速度ゲインモードを表す列挙型
    /// wizmo_state.h -> WIZMOSpeedGain に対応
    /// </summary>
    public enum WizmoSpeedGain : int
    {
        Normal = 0,     // ノーマル速度ゲイン（全軸固定速度設定）
        Variable = 1,   // 可変速度ゲイン（追従速度モード）
        Manual = 2,     // マニュアル速度ゲイン（軸別の速度設定）
    }

    /// <summary>
    /// 速度ゲインモードを表す列挙型
    /// wizmo_state.h -> WIZMOSpeedGain に対応
    /// </summary>
    public enum WizmoAxisMode : int
    {
        AXIS_MODE_MANUAL = 0,       //アクチュエータごとに設定（自作で計算する場合など）
        AXIS_MODE_GLOBALPOSE = 1,   //グローバル座標での姿勢計算　※デフォルト
        AXIS_MODE_LOCALPOSE = 2,	//ローカル座標での姿勢計算
    }

    /// <summary>
    /// WIZMO データパケット構造体
    /// </summary>
    [StructLayout(LayoutKind.Sequential)]
    public class wizmoPacket
    {
        // Axis position controls
        public float axis1;
        public float axis2;
        public float axis3;
        public float axis4;
        public float axis5;
        public float axis6;

        // Axis speed/accel controls
        public float speed1_all;
        public float speed2;
        public float speed3;
        public float speed4;
        public float speed5;
        public float speed6;
        public float accel;

        // Axis Processing
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

            speed1_all = 0.667f;
            speed2 = 0.667f;
            speed3 = 0.667f;
            speed4 = 0.667f;
            speed5 = 0.667f;
            speed6 = 0.667f;
            accel = 0.5f;

            roll = 0.0f;
            pitch = 0.0f;
            yaw = 0.0f;
            heave = 0.0f;
            sway = 0.0f;
            surge = 0.0f;

            rotationMotionRatio = 1.0f;
            gravityMotionRatio = 0.0f;

            commandSendCount = 0;
            command = "";
        }
    }

    /// <summary>
    /// WIZMO メインクラス
    /// </summary>
    public class WIZMO
    {
        public string appPassCode = "";

        #region WIZMO DLL IMPORTER
        [DllImport("wizmo", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoOpen(string appCode);
        [DllImport("wizmo", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoOpenSerialAssign(string appCode, string assign);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoClose(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern int wizmoWrite(Int32 handle, wizmoPacket packet);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern void wizmoSetOriginMode(Int32 handle, Int32 flag);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoGetOriginMode(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern void wizmoSetAxisProcessingMode(Int32 handle, Int32 flag);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoGetAxisProcessingMode(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern void wizmoSetSpeedGainMode(Int32 handle, Int32 value);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoGetSpeedGainMode(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern IntPtr wizmoGetAppCode(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern IntPtr wizmoGetSerialNumber(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoGetState(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoGetSystemStatus(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoGetDevice(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoGetStatusEXT4(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern IntPtr wizmoGetVersion(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoIsRunning(Int32 handle);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoGetBackLog(byte[] str, Int32 str_size);
        [DllImport("wizmo", CallingConvention = CallingConvention.Cdecl)]
        static extern Int32 wizmoBackLogDataAvailable();
        #endregion

        private bool g_verbose;
        private bool g_wizmoIsOpen;
        private wizmoPacket g_simplePacket;
        private int g_wizmoHandle;

        /// <summary>
        /// コンストラクタ
        /// </summary>
        /// <param name="verbose">true にするとデバッグメッセージをコンソールに出力する</param>
        public WIZMO(bool verbose)
        {
            g_wizmoIsOpen = false;
            g_verbose = verbose;
            g_simplePacket = new wizmoPacket();
            g_wizmoHandle = -1;

            if (verbose)
                Console.WriteLine("LOADED WIZMO DLL.");
        }

        // ============================================================
        //  接続・切断
        // ============================================================

        /// <summary>
        /// WIZMO をオープンし動作可能モードにする
        /// </summary>
        /// <param name="appCode">アプリケーションコード</param>
        public void Starter(string appCode)
        {
            Starter(appCode, "");
        }

        /// <summary>
        /// シリアル番号を指定して WIZMO をオープンし動作可能モードにする
        /// </summary>
        /// <param name="appCode">アプリケーションコード</param>
        /// <param name="serialAssign">シリアル番号でデバイスを指定</param>
        public void Starter(string appCode, string serialAssign)
        {
            if (g_wizmoIsOpen)
                return;

            appPassCode = appCode;

            if (string.IsNullOrEmpty(serialAssign))
                g_wizmoHandle = wizmoOpen(appPassCode);
            else
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
                    Console.WriteLine("WIZMO OPEN ERROR!");
            }
        }

        /// <summary>
        /// WIZMO を閉じ、接続を終了する
        /// </summary>
        public void Close()
        {
            if (!g_wizmoIsOpen)
                return;

            wizmoClose(g_wizmoHandle);
            g_wizmoIsOpen = false;
        }

        // ============================================================
        //  パケット送信
        // ============================================================

        /// <summary>
        /// wizmoPacket を直接指定してアクチュエータにパケットを送信する
        /// </summary>
        /// <param name="packet">送信するデータパケット</param>
        public void PacketUpdate(wizmoPacket packet)
        {
            if (!g_wizmoIsOpen)
                return;

            wizmoWrite(g_wizmoHandle, packet);
        }

        /// <summary>
        /// 6 軸のモーション値を指定してパケットを送信する
        /// </summary>
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

        /// <summary>
        /// モーション比率を更新してパケットを送信する
        /// </summary>
        /// <param name="rotation">回転モーション比率 (0.0～1.0)</param>
        /// <param name="gravity">G モーション比率 (0.0～1.0)</param>
        public void SimpleMotionRatioUpdate(float rotation, float gravity)
        {
            if (!g_wizmoIsOpen)
                return;

            g_simplePacket.rotationMotionRatio = rotation;
            g_simplePacket.gravityMotionRatio = gravity;
            wizmoWrite(g_wizmoHandle, g_simplePacket);
        }

        /// <summary>
        /// 各軸の速度と加速度を個別に設定してパケットを送信する
        /// </summary>
        public void SimpleMotionSpeedUpdate(float accel, float speed1, float speed2, float speed3, float speed4, float speed5, float speed6)
        {
            if (!g_wizmoIsOpen)
                return;

            g_simplePacket.accel = accel;
            g_simplePacket.speed1_all = speed1;
            g_simplePacket.speed2 = speed2;
            g_simplePacket.speed3 = speed3;
            g_simplePacket.speed4 = speed4;
            g_simplePacket.speed5 = speed5;
            g_simplePacket.speed6 = speed6;
            wizmoWrite(g_wizmoHandle, g_simplePacket);
        }

        /// <summary>
        /// 全軸を同一の速度に設定してパケットを送信する
        /// </summary>
        /// <param name="accel">加速度レート (0.0～1.0)</param>
        /// <param name="speed">全軸共通の速度 (0.0～1.0)</param>
        public void SimpleMotionPowerUpdate(float accel, float speed)
        {
            if (!g_wizmoIsOpen)
                return;

            g_simplePacket.accel = accel;
            g_simplePacket.speed1_all = speed;
            g_simplePacket.speed2 = speed;
            g_simplePacket.speed3 = speed;
            g_simplePacket.speed4 = speed;
            g_simplePacket.speed5 = speed;
            g_simplePacket.speed6 = speed;
            wizmoWrite(g_wizmoHandle, g_simplePacket);
        }

        // ============================================================
        //  プロパティ設定・取得
        // ============================================================

        /// <summary>乗降モードを設定する</summary>
        public void SetOriginMode(bool value)
        {
            wizmoSetOriginMode(g_wizmoHandle, Convert.ToInt32(value));
        }

        /// <summary>現在の乗降モードを取得する</summary>
        public bool GetOriginMode()
        {
            return wizmoGetOriginMode(g_wizmoHandle) != 0;
        }

        /// <summary>軸プロセスモード（自動計算）を設定する</summary>
        public void SetAxisProcessingMode(WizmoAxisMode value)
        {
            wizmoSetAxisProcessingMode(g_wizmoHandle, Convert.ToInt32(value));
        }

        /// <summary>現在の軸プロセスモードを取得する</summary>
        public WizmoAxisMode GetAxisProcessingMode()
        {
            return (WizmoAxisMode)wizmoGetAxisProcessingMode(g_wizmoHandle);
        }

        /// <summary>速度ゲインモードを設定する</summary>
        /// <param name="value">速度ゲインモード</param>
        public void SetSpeedGainMode(WizmoSpeedGain value)
        {
            wizmoSetSpeedGainMode(g_wizmoHandle, (int)value);
        }

        /// <summary>現在の速度ゲインモードを取得する</summary>
        public WizmoSpeedGain GetSpeedGainMode()
        {
            return (WizmoSpeedGain)wizmoGetSpeedGainMode(g_wizmoHandle);
        }

        // ============================================================
        //  デバイス情報取得
        // ============================================================

        /// <summary>現在接続されているアプリケーションコードを取得する</summary>
        public string? GetAppCode()
        {
            IntPtr pStr = wizmoGetAppCode(g_wizmoHandle);
            return Marshal.PtrToStringAnsi(pStr);
        }

        /// <summary>現在接続されているシリアル番号を取得する</summary>
        public string? GetSerialNumber()
        {
            IntPtr pStr = wizmoGetSerialNumber(g_wizmoHandle);
            return Marshal.PtrToStringAnsi(pStr);
        }

        /// <summary>デバイスの現在の状態を取得する</summary>
        public WizmoState GetStatus()
        {
            return (WizmoState)wizmoGetState(g_wizmoHandle);
        }

        /// <summary>ライブラリが動作中かどうかを取得する</summary>
        public bool GetSystemStatus()
        {
            return wizmoGetSystemStatus(g_wizmoHandle) != 0;
        }

        /// <summary>デバイスが動作中かどうかを返す</summary>
        public bool IsRunning()
        {
            return wizmoIsRunning(g_wizmoHandle) != 0;
        }

        /// <summary>接続されているデバイスの種類を取得する</summary>
        public WizmoDevice GetDevice()
        {
            return (WizmoDevice)wizmoGetDevice(g_wizmoHandle);
        }
        /// <summary>接続されているデバイス名を取得する</summary>
        public string GetDeviceName()
        {
            return GetDevice().ToString();
        }

        /// <summary>ライブラリのバージョンを取得する</summary>
        public string? GetVersion()
        {
            IntPtr pStr = wizmoGetVersion(g_wizmoHandle);
            return Marshal.PtrToStringAnsi(pStr);
        }

        /// <summary>外部データ（EXT4）を取得する</summary>
        public int GetStatusEXT4()
        {
            return wizmoGetStatusEXT4(g_wizmoHandle);
        }

        // ============================================================
        //  バックログ
        // ============================================================

        /// <summary>ライブラリ内部のバックログを取得する</summary>
        public string UpdateBackLog()
        {
            string resultString = "";
            var size = wizmoBackLogDataAvailable();

            if (size > 0)
            {
                byte[] dataArray = new byte[size];
                int iRet = wizmoGetBackLog(dataArray, size);

                if (iRet <= 0 || dataArray == null)
                    return resultString;

                resultString = System.Text.Encoding.UTF8.GetString(dataArray, 0, iRet);
            }

            if (g_verbose && resultString != "")
                Console.Write(resultString);

            return resultString;
        }

        // ============================================================
        //  後方互換（Obsolete）
        // ============================================================

        /// <summary>可変速度ゲインモードの ON/OFF を設定する</summary>
        [Obsolete("SetSpeedGainMode(WizmoSpeedGain) を使用してください")]
        public void SetVariableGainMode(bool value)
        {
            SetSpeedGainMode(value ? WizmoSpeedGain.Variable : WizmoSpeedGain.Normal);
        }

        /// <summary>現在の可変速度ゲインモードの ON/OFF を取得する</summary>
        [Obsolete("GetSpeedGainMode() を使用してください")]
        public bool GetVariableGainMode()
        {
            return GetSpeedGainMode() == WizmoSpeedGain.Variable;
        }
    }
}