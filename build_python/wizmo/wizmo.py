# -*- coding: utf-8 -*-
# Import
from ctypes import (
    CDLL, Structure, POINTER, cdll,
    c_int, c_float, c_char, c_char_p,
    pointer, create_string_buffer,
)
import time
import platform
import os
import sys
from enum import IntEnum

# Define
WIZMO_HANDLE_ERROR = -1


# ============================================================
#  列挙型
# ============================================================
class wizmoStatus(IntEnum):
    """デバイスの状態 (wizmo_state.h -> State に対応)"""
    # エラー & ストップ
    CanNotFindUsb = 0            # 未接続
    CanNotFindWizmo = 1          # 未接続
    CanNotCalibration = 2        # キャリブレーション起動失敗
    TimeoutCalibration = 3       # キャリブレーション中の失敗
    ShutDownActuator = 4         # アクチュエータ停止
    CanNotCertificate = 5        # 認証失敗
    # ランニング
    Initial = 6                  # 初期状態 通電中
    CalibrationRunning = 7       # キャリブレーション中
    Running = 8                  # 動作中
    # フォールトトレラント
    StopActuator = 9             # アクチュエータ一部停止
    CalibrationRetry = 10        # キャリブレーション再設定


class wizmoSpeedGain(IntEnum):
    """速度ゲインモード"""
    Normal = 0      # ノーマル速度ゲイン(全軸固定速度設定) ※デフォルト
    Variable = 1    # 可変速度ゲイン(追従速度モード)
    Manual = 2      # マニュアル速度ゲイン(軸別の速度設定)
    # C# と同名のエイリアス
    NORMAL = 0
    VARIABLE = 1
    MANUAL = 2


class wizmoAxisMode(IntEnum):
    """軸プロセッシングモード"""
    Manual = 0       # アクチュエータごとに設定 (自作で計算する場合など)
    GlobalPose = 1   # グローバル座標での姿勢計算 ※デフォルト
    LocalPose = 2    # ローカル座標での姿勢計算
    # 旧名エイリアス
    Global = 1
    Local = 2
    # C# と同名のエイリアス
    MANUAL = 0
    GLOBALPOSE = 1
    LOCALPOSE = 2


class wizmoDevice(IntEnum):
    """接続デバイス種別"""
    NONE = 0
    SIMVR2DOF = 1
    SIMVR4DOF = 2
    SIMVR6DOF = 3
    ANTSEAT = 4
    SIMVRMASSIVE_KV = 5
    SIMVRMASSIVE500_KV = 6

    SIMVR_KDIVE2_OEM = 100
    SIMVR_KICKBOARD_KV_OEM = 101
    SIMVR_E2M_EMU_OEM = 102
    SIMVR_DRIVEX_OEM = 103
    SIMVR_OSDX_OEM = 104


# ============================================================
#  WIZMO データパケット
# ============================================================
class wizmoPacket(Structure):
    _fields_ = [
        # 軸オペレーション
        ("axis1", c_float),
        ("axis2", c_float),
        ("axis3", c_float),
        ("axis4", c_float),
        ("axis5", c_float),
        ("axis6", c_float),
        # 軸速度・加速度オペレーション
        ("speed1_all", c_float),
        ("speed2", c_float),
        ("speed3", c_float),
        ("speed4", c_float),
        ("speed5", c_float),
        ("speed6", c_float),
        ("accel", c_float),
        # 軸プロセッシング
        ("roll", c_float),    # -1.0 ~ 1.0
        ("pitch", c_float),   # -1.0 ~ 1.0
        ("yaw", c_float),     # -1.0 ~ 1.0
        ("heave", c_float),   # -1.0 ~ 1.0
        ("sway", c_float),    # -1.0 ~ 1.0
        ("surge", c_float),   # -1.0 ~ 1.0
        # ピボット (SIMVR MASSIVE のみ有効)
        ("pivotX", c_float),  # 軸ピボット X (mm)
        ("pivotY", c_float),  # 軸ピボット Y (mm)
        ("pivotZ", c_float),  # 軸ピボット Z (mm)
        # レシオ
        ("rotationMotionRatio", c_float),  # 0.0 ~ 1.0
        ("gravityMotionRatio", c_float),   # 0.0 ~ 1.0
        # コマンド
        ("commandSendCount", c_int),
        ("command", c_char * 256),
    ]

    def __init__(self):
        super().__init__()
        self.axis1 = 0.5
        self.axis2 = 0.5
        self.axis3 = 0.5
        self.axis4 = 0.5
        self.axis5 = 0.5
        self.axis6 = 0.5

        self.speed1_all = 0.667
        self.speed2 = 0.667
        self.speed3 = 0.667
        self.speed4 = 0.667
        self.speed5 = 0.667
        self.speed6 = 0.667
        self.accel = 0.5

        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.heave = 0.0
        self.sway = 0.0
        self.surge = 0.0

        self.pivotX = 0.0
        self.pivotY = 0.0
        self.pivotZ = 0.0

        self.rotationMotionRatio = 1.0
        self.gravityMotionRatio = 0.0

        self.commandSendCount = 0
        self.command = b""


# ============================================================
#  WIZMO メインクラス
# ============================================================
class wizmo():

    _wizmo_lib = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def __init__(self, verbose: bool = False):
        os_name = platform.system()
        arch_is64bit = platform.architecture()[0] == '64bit'
        arch_isARM = False
        if 'armv' in platform.machine() or 'aarch64' in platform.machine():
            arch_isARM = True

        # For pyinstaller build
        if getattr(sys, 'frozen', False):
            libloadpath = ""
        else:
            libloadpath = os.path.dirname(__file__)

        if os_name == 'Windows':
            if arch_is64bit:
                if arch_isARM:
                    libloadpath += '\\wizmoARM64.dll'
                else:
                    libloadpath += '\\wizmo.dll'
            else:
                libloadpath += '\\wizmo32.dll'
        else:
            if arch_isARM:
                if arch_is64bit:
                    libloadpath += '/libwizmoRPi64.so'
                else:
                    libloadpath += '/libwizmoRPi32.so'
            else:
                if arch_is64bit:
                    libloadpath += '/libwizmo.so'
                else:
                    libloadpath += '/libwizmo32.so'

        if wizmo._wizmo_lib is None:
            try:
                wizmo._wizmo_lib = cdll.LoadLibrary(libloadpath)
            except OSError as e:
                raise RuntimeError(f"WIZMO Load Library Error:{libloadpath}") from e
            wizmo._setup_signatures(wizmo._wizmo_lib)

        self.wizmolib = wizmo._wizmo_lib
        self.verbose = verbose
        self.simplePacket = wizmoPacket()
        self.wizmoHandle = WIZMO_HANDLE_ERROR

        if self.verbose:
            print("LOADED WIZMO DLL.")

    # ------------------------------------------------------------
    #  ライブラリ関数シグネチャ設定
    # ------------------------------------------------------------
    @staticmethod
    def _setup_signatures(lib: CDLL) -> None:
        # 接続
        lib.wizmoOpen.argtypes = (c_char_p,)
        lib.wizmoOpen.restype = c_int
        lib.wizmoOpenSerialAssign.argtypes = (c_char_p, c_char_p)
        lib.wizmoOpenSerialAssign.restype = c_int
        lib.wizmoClose.argtypes = (c_int,)
        lib.wizmoClose.restype = c_int
        # 書込
        lib.wizmoWrite.argtypes = (c_int, POINTER(wizmoPacket))
        lib.wizmoWrite.restype = c_int
        # モード
        lib.wizmoSetOriginMode.argtypes = (c_int, c_int)
        lib.wizmoSetOriginMode.restype = None
        lib.wizmoGetOriginMode.argtypes = (c_int,)
        lib.wizmoGetOriginMode.restype = c_int
        lib.wizmoSetAxisProcessingMode.argtypes = (c_int, c_int)
        lib.wizmoSetAxisProcessingMode.restype = None
        lib.wizmoGetAxisProcessingMode.argtypes = (c_int,)
        lib.wizmoGetAxisProcessingMode.restype = c_int
        lib.wizmoSetSpeedGainMode.argtypes = (c_int, c_int)
        lib.wizmoSetSpeedGainMode.restype = None
        lib.wizmoGetSpeedGainMode.argtypes = (c_int,)
        lib.wizmoGetSpeedGainMode.restype = c_int
        # 情報取得
        lib.wizmoGetAppCode.argtypes = (c_int,)
        lib.wizmoGetAppCode.restype = c_char_p
        lib.wizmoGetSerialNumber.argtypes = (c_int,)
        lib.wizmoGetSerialNumber.restype = c_char_p
        lib.wizmoGetState.argtypes = (c_int,)
        lib.wizmoGetState.restype = c_int
        lib.wizmoGetSystemStatus.argtypes = (c_int,)
        lib.wizmoGetSystemStatus.restype = c_int
        lib.wizmoGetDevice.argtypes = (c_int,)
        lib.wizmoGetDevice.restype = c_int
        lib.wizmoGetStatusEXT4.argtypes = (c_int,)
        lib.wizmoGetStatusEXT4.restype = c_int
        lib.wizmoGetVersion.argtypes = (c_int,)
        lib.wizmoGetVersion.restype = c_char_p
        lib.wizmoIsRunning.argtypes = (c_int,)
        lib.wizmoIsRunning.restype = c_int
        # バックログ
        lib.wizmoGetBackLog.argtypes = (c_char_p, c_int)
        lib.wizmoGetBackLog.restype = c_int
        lib.wizmoBackLogDataAvailable.argtypes = ()
        lib.wizmoBackLogDataAvailable.restype = c_int

    # ------------------------------------------------------------
    #  バックログ
    # ------------------------------------------------------------
    @staticmethod
    def get_backlog(printing: bool = False) -> str:
        buf_res = ''
        size = wizmo._wizmo_lib.wizmoBackLogDataAvailable()
        if size > 0:
            p = create_string_buffer(size)
            iRef = wizmo._wizmo_lib.wizmoGetBackLog(p, size)
            if iRef > 0:
                bufferString = p.value.decode()
                buf_res += bufferString.rstrip("\n")

        if printing and buf_res != '':
            print(buf_res)

        return buf_res

    # ------------------------------------------------------------
    #  接続・切断
    # ------------------------------------------------------------
    def starter(self, appCode: str, assign: str = "", blocking: bool = False) -> int:
        """WIZMO をオープンし動作可能モードにする

        Args:
            appCode: アプリケーションコード
            assign: シリアル番号でデバイスを指定 (空文字なら自動選択)
            blocking: 初期化完了までブロックするか
        """
        if self.wizmoHandle >= 0:
            if self.verbose:
                print("WIZMO IS ALREADY OPEN.")
            return WIZMO_HANDLE_ERROR

        if assign == "":
            self.wizmoHandle = int(self.wizmolib.wizmoOpen(appCode.encode()))
        else:
            self.wizmoHandle = int(self.wizmolib.wizmoOpenSerialAssign(
                appCode.encode(), assign.encode()))

        if self.wizmoHandle < 0:
            if self.verbose:
                print("WIZMO OPEN ERROR!")
            self.wizmoHandle = WIZMO_HANDLE_ERROR
        else:
            if self.verbose:
                print("STARTED WIZMO.")
            if blocking:
                while self.get_status() <= wizmoStatus.Initial:
                    print(self.get_status())
                    time.sleep(0.1)

        return self.wizmoHandle

    def starter_serialassign(self, appCode: str, assign: str, blocking: bool = False) -> int:
        """非推奨: starter(appCode, assign=...) を使用してください"""
        return self.starter(appCode, assign, blocking)

    def close(self) -> None:
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            if self.verbose:
                print("WIZMO IS NOT OPEN.")
            return

        self.wizmolib.wizmoClose(self.wizmoHandle)
        self.wizmoHandle = WIZMO_HANDLE_ERROR

    # ------------------------------------------------------------
    #  パケット送信
    # ------------------------------------------------------------
    def packet_update(self, packet: wizmoPacket) -> None:
        """wizmoPacket を直接指定してアクチュエータにパケットを送信する"""
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return
        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(packet))

    def simple_pose_update(self, roll: float, pitch: float, yaw: float,
                           heave: float, sway: float, surge: float) -> None:
        """6 軸のモーション値を指定してパケットを送信する"""
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return

        self.simplePacket.roll = roll
        self.simplePacket.pitch = pitch
        self.simplePacket.yaw = yaw
        self.simplePacket.heave = heave
        self.simplePacket.sway = sway
        self.simplePacket.surge = surge
        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(self.simplePacket))

    def simple_pose_update_tuple(self, value: tuple) -> None:
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return

        if len(value) != 6:
            if self.verbose:
                print("ERROR TUPLE FORMAT.")
            return

        self.simplePacket.roll = value[0]
        self.simplePacket.pitch = value[1]
        self.simplePacket.yaw = value[2]
        self.simplePacket.heave = value[3]
        self.simplePacket.sway = value[4]
        self.simplePacket.surge = value[5]
        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(self.simplePacket))

    def simple_motion_ratio_update(self, rotation: float, gravity: float) -> None:
        """モーション比率を更新してパケットを送信する"""
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return

        self.simplePacket.rotationMotionRatio = rotation
        self.simplePacket.gravityMotionRatio = gravity
        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(self.simplePacket))

    def simple_motion_speed_update(self, accel: float, speed1: float, speed2: float,
                                   speed3: float, speed4: float, speed5: float,
                                   speed6: float) -> None:
        """各軸の速度と加速度を個別に設定してパケットを送信する"""
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return

        self.simplePacket.accel = accel
        self.simplePacket.speed1_all = speed1
        self.simplePacket.speed2 = speed2
        self.simplePacket.speed3 = speed3
        self.simplePacket.speed4 = speed4
        self.simplePacket.speed5 = speed5
        self.simplePacket.speed6 = speed6
        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(self.simplePacket))

    def simple_motion_power_update(self, accel: float, speed: float) -> None:
        """全軸を同一の速度に設定してパケットを送信する"""
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return

        self.simplePacket.accel = accel
        self.simplePacket.speed1_all = speed
        self.simplePacket.speed2 = speed
        self.simplePacket.speed3 = speed
        self.simplePacket.speed4 = speed
        self.simplePacket.speed5 = speed
        self.simplePacket.speed6 = speed
        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(self.simplePacket))

    def simple_pivot_update(self, x: float, y: float, z: float) -> None:
        """ピボット位置を変更 (SIMVR MASSIVE のみ有効)

        Args:
            x 左右方向のオフセット [mm]（正=右方）
            y 上下方向のオフセット [mm]（正=上方）
            z 前後方向のオフセット [mm]（正=前方）
        """
        if self.wizmoHandle == WIZMO_HANDLE_ERROR:
            return

        self.simplePacket.pivotX = x
        self.simplePacket.pivotY = y
        self.simplePacket.pivotZ = z
        self.wizmolib.wizmoWrite(self.wizmoHandle, pointer(self.simplePacket))

    # ------------------------------------------------------------
    #  プロパティ設定・取得
    # ------------------------------------------------------------
    def axis_processing_mode(self, value: wizmoAxisMode = None):
        """軸プロセスモードの設定/取得"""
        if value is None:
            return wizmoAxisMode(self.wizmolib.wizmoGetAxisProcessingMode(self.wizmoHandle))
        else:
            self.wizmolib.wizmoSetAxisProcessingMode(self.wizmoHandle, int(value))

    def origin_mode(self, value: bool = None):
        """乗降モードの設定/取得"""
        if value is None:
            return bool(self.wizmolib.wizmoGetOriginMode(self.wizmoHandle))
        else:
            self.wizmolib.wizmoSetOriginMode(self.wizmoHandle, int(bool(value)))

    def speed_gain_mode(self, value: wizmoSpeedGain = None):
        """速度ゲインモードの設定/取得"""
        if value is None:
            return wizmoSpeedGain(self.wizmolib.wizmoGetSpeedGainMode(self.wizmoHandle))
        else:
            self.wizmolib.wizmoSetSpeedGainMode(self.wizmoHandle, int(value))

    # ------------------------------------------------------------
    #  デバイス情報取得
    # ------------------------------------------------------------
    def get_app_code(self) -> str:
        """現在接続されているアプリケーションコードを取得する"""
        p = self.wizmolib.wizmoGetAppCode(self.wizmoHandle)
        return p.decode() if p else ""

    def get_serial_number(self) -> str:
        """現在接続されているシリアル番号を取得する"""
        p = self.wizmolib.wizmoGetSerialNumber(self.wizmoHandle)
        return p.decode() if p else ""

    def get_status(self) -> wizmoStatus:
        """デバイスの現在の状態を取得する"""
        return wizmoStatus(self.wizmolib.wizmoGetState(self.wizmoHandle))

    def get_system_status(self) -> bool:
        """ライブラリが動作中かどうかを取得する"""
        return bool(self.wizmolib.wizmoGetSystemStatus(self.wizmoHandle))

    def is_running(self) -> bool:
        """デバイスが動作中かどうかを返す"""
        return bool(self.wizmolib.wizmoIsRunning(self.wizmoHandle))

    def get_device(self) -> wizmoDevice:
        """接続されているデバイスの種類を取得する"""
        return wizmoDevice(self.wizmolib.wizmoGetDevice(self.wizmoHandle))

    def get_device_name(self) -> str:
        """接続されているデバイス名を取得する"""
        return self.get_device().name

    def get_version(self) -> str:
        """ライブラリのバージョンを取得する"""
        p = self.wizmolib.wizmoGetVersion(self.wizmoHandle)
        return p.decode() if p else ""

    def get_status_ext4(self) -> int:
        """外部データ (EXT4) を取得する"""
        return int(self.wizmolib.wizmoGetStatusEXT4(self.wizmoHandle))

    # ------------------------------------------------------------
    #  後方互換 (Deprecated)
    # ------------------------------------------------------------
    def set_variable_gain_mode(self, value: bool) -> None:
        """非推奨: speed_gain_mode() を使用してください"""
        self.speed_gain_mode(
            wizmoSpeedGain.Variable if value else wizmoSpeedGain.Normal)

    def get_variable_gain_mode(self) -> bool:
        """非推奨: speed_gain_mode() を使用してください"""
        return self.speed_gain_mode() == wizmoSpeedGain.Variable
