import vlc
import time
import csv
from pynput import keyboard as pynput_keyboard
import wizmo
import math
import json
import os
from ctypes import windll
import asyncio as aio
import threading
from collections import deque
import tkinter as tk
import ctypes
from ctypes import wintypes

# ----- global var -----
g_bMainProcess = True
g_bResetRequest = False   # 停止時にシーケンスを最初に戻すリクエスト
g_bExitRequest  = False   # Escで再生を終了しGUIに戻るリクエスト
g_dictSimvrVariable = {
    'heave':     0.0,
    'sway':      0.0,
    'surge':     0.0,
    'pitch':     0.0,
    'roll':      0.0,
    'yaw':       0.0,
    'accel_gain':0.5,
    'speed_gain':0.5,
    'is_origin': 0,
    'variable_mode': True
}
g_bSimvrEndFlag = False

g_bVideoRunning = False
_objVlcInstance = vlc.Instance()
_objPlayer = _objVlcInstance.media_player_new()


def _enum_monitor_rects():
    """接続中の全モニタの矩形 (left, top, right, bottom) を返す"""
    list_tplRects = []

    def _callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
        objRect = lprcMonitor.contents
        list_tplRects.append((objRect.left, objRect.top, objRect.right, objRect.bottom))
        return 1

    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(wintypes.RECT),
        ctypes.c_void_p,
    )
    windll.user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(_callback), 0)
    return list_tplRects


def _get_extended_monitor_rect():
    """拡張ディスプレイ（プライマリ以外）の矩形を返す。無ければプライマリを返す。"""
    list_tplRects = _enum_monitor_rects()
    if not list_tplRects:
        return None
    # プライマリの左上は必ず (0,0)。それ以外を拡張ディスプレイとみなす
    for tpl_Rect in list_tplRects:
        if (tpl_Rect[0], tpl_Rect[1]) != (0, 0):
            return tpl_Rect
    return list_tplRects[0]


def get_monitors():
    """接続中の全モニタ矩形リスト [(left, top, right, bottom), ...] を返す（GUIのディスプレイ選択用）"""
    return _enum_monitor_rects()


def _get_target_monitor_rect(n_nDisplayIndex=None):
    """表示先モニタの矩形を返す。
    n_nDisplayIndex=None なら拡張ディスプレイ（プライマリ以外）を自動選択。
    整数ならそのインデックスのモニタ。範囲外／不正なら自動選択にフォールバック。
    """
    list_tplRects = _enum_monitor_rects()
    if not list_tplRects:
        return None
    if n_nDisplayIndex is not None:
        try:
            n_nIdx = int(n_nDisplayIndex)
            if 0 <= n_nIdx < len(list_tplRects):
                return list_tplRects[n_nIdx]
            print(f"警告: ディスプレイ番号 {n_nIdx} は範囲外です。自動選択します。")
        except (ValueError, TypeError):
            print(f"警告: ディスプレイ番号が不正です: {n_nDisplayIndex}。自動選択します。")
    # 自動: プライマリ(0,0)以外を拡張ディスプレイとみなす
    for tpl_Rect in list_tplRects:
        if (tpl_Rect[0], tpl_Rect[1]) != (0, 0):
            return tpl_Rect
    return list_tplRects[0]

# デフォルトのゲイン値
DEFAULT_SPEED_GAIN = 0.667
DEFAULT_ACCEL_GAIN = 0.03

# デバイスのシリアル一覧（先頭から使用台数ぶんを使う）
SERIALS = [
    "SIMVR-0001", "SIMVR-0002", "SIMVR-0003", "SIMVR-0004", "SIMVR-0005",
    "SIMVR-0006", "SIMVR-0007", "SIMVR-0008", "SIMVR-0009", "SIMVR-0010",
    "SIMVR-0011", "SIMVR-0012", "SIMVR-0013", "SIMVR-0014", "SIMVR-0015",
    "SIMVR-0016", "SIMVR-0017", "SIMVR-0018", "SIMVR-0019", "SIMVR-0020",
]


def get_device_serials():
    """登録済みデバイスのシリアル一覧を返す（GUIの台数選択用）"""
    return list(SERIALS)

# 待機状態: True=is_origin（heave=1.0） / False=is_origin解除（heave=0.0）（Rキーで切替）
g_bStandbyOrigin = True

# ----- データ補間クラス -----
class DataInterpolator:
    """CSVデータの線形補間を行うクラス"""
    
    def __init__(self, data_list):
        """
        data_list: CSVから読み込んだデータのリスト
        """
        self.m_listData = data_list
        self.m_nDataLength = len(data_list)
        self.m_nCurrentIndex = 0
        
    def get_interpolated_data(self, f_fCurrentTime):
        """
        指定時刻のデータを線形補間で取得
        f_fCurrentTime: 現在時刻（秒）
        """
        # データ範囲外チェック
        if self.m_nCurrentIndex >= self.m_nDataLength - 1:
            return self.m_listData[-1], True
            
        # 現在と次のデータポイントを取得
        dict_objCurrent = self.m_listData[self.m_nCurrentIndex]
        dict_objNext = self.m_listData[self.m_nCurrentIndex + 1]
        
        f_fCurrentDataTime = float(dict_objCurrent['time'])
        f_fNextDataTime = float(dict_objNext['time'])
        
        # 次のデータポイントを過ぎた場合、インデックスを進める
        while f_fCurrentTime >= f_fNextDataTime and self.m_nCurrentIndex < self.m_nDataLength - 2:
            self.m_nCurrentIndex += 1
            dict_objCurrent = self.m_listData[self.m_nCurrentIndex]
            dict_objNext = self.m_listData[self.m_nCurrentIndex + 1]
            f_fCurrentDataTime = float(dict_objCurrent['time'])
            f_fNextDataTime = float(dict_objNext['time'])
        
        # 補間係数を計算
        f_fAlpha = 0.0
        if f_fNextDataTime - f_fCurrentDataTime > 0:
            f_fAlpha = (f_fCurrentTime - f_fCurrentDataTime) / (f_fNextDataTime - f_fCurrentDataTime)
            f_fAlpha = max(0.0, min(1.0, f_fAlpha))  # 0-1にクランプ
        
        # 補間されたデータを作成
        dict_objInterpolated = {'time': f_fCurrentTime}
        
        # 各パラメータを線形補間
        list_strParams = ['heave', 'sway', 'surge', 'roll', 'pitch', 'yaw', 'speed', 'accel']
        for str_param in list_strParams:
            if str_param in dict_objCurrent and str_param in dict_objNext:
                f_fCurrentVal = float(dict_objCurrent[str_param])
                f_fNextVal = float(dict_objNext[str_param])
                dict_objInterpolated[str_param] = f_fCurrentVal + (f_fNextVal - f_fCurrentVal) * f_fAlpha
            elif str_param in dict_objCurrent:
                dict_objInterpolated[str_param] = float(dict_objCurrent[str_param])
        
        # is_originは補間せず現在値を使用
        if 'is_origin' in dict_objCurrent:
            dict_objInterpolated['is_origin'] = int(dict_objCurrent['is_origin'])
        
        return dict_objInterpolated, False

# ----- リングバッファクラス -----
class RingBuffer:
    """スムージング用のリングバッファ"""
    
    def __init__(self, n_nSize=5):
        """
        n_nSize: バッファサイズ
        """
        self.m_dequeBuffer = deque(maxlen=n_nSize)
        
    def add(self, f_fValue):
        """値を追加"""
        self.m_dequeBuffer.append(f_fValue)
        
    def get_average(self):
        """平均値を取得"""
        if len(self.m_dequeBuffer) == 0:
            return 0.0
        return sum(self.m_dequeBuffer) / len(self.m_dequeBuffer)
    
    def clear(self):
        """バッファをクリア"""
        self.m_dequeBuffer.clear()

# ----- Configuration -----
def load_filter_config(config_path=None):
    """
    フィルタ設定をJSONファイルから読み込む
    config_path: 設定ファイルのパス（省略時はデフォルトファイルを使用）
    """
    dict_objDefaultConfig = {
        "filter_settings": {
            "sample_rate": 100,
            "filters": {
                "heave": {"type": "HIGH_PASS", "cutoff": 1.2, "normalization": 2.0},
                "sway":  {"type": "LOW_PASS", "cutoff": 2.55, "normalization": 3.3},
                "surge": {"type": "LOW_PASS", "cutoff": 2.55, "normalization": 3.3},
                "roll":  {"type": "LOW_PASS", "cutoff": 1.25, "normalization": 16.0, "is_radian": True},
                "pitch": {"type": "LOW_PASS", "cutoff": 1.25, "normalization": 16.0, "is_radian": True},
                "yaw":   {"type": "LOW_PASS", "cutoff": 1.25, "normalization": 16.0, "is_radian": True}
            }
        },
        "motion_ratio": {
            "rotation": 1.0,
            "gravity": 0.0
        },
        "gain_mode": {
            "variable_mode": True
        },
        "smoothing": {
            "enabled": True,
            "buffer_size": 3
        }
    }
    
    # デフォルトパスの設定
    if config_path is None:
        config_path = "filter_config.json"
    
    # ファイルが存在しない場合はデフォルト設定を使用
    if not os.path.exists(config_path):
        print(f"設定ファイル '{config_path}' が見つかりません。デフォルト設定を使用します。")
        # デフォルト設定をファイルとして保存（初回用）
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(dict_objDefaultConfig, f, indent=2, ensure_ascii=False)
            print(f"デフォルト設定を '{config_path}' に保存しました。")
        except Exception as e:
            print(f"設定ファイルの保存に失敗: {e}")
        
        return dict_objDefaultConfig
    
    # ファイルから設定を読み込む
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            dict_objConfig = json.load(f)
        print(f"設定ファイル '{config_path}' を読み込みました。")
        
        # 必要なキーが存在するか確認し、不足分はデフォルトで補完
        for str_key in dict_objDefaultConfig:
            if str_key not in dict_objConfig:
                dict_objConfig[str_key] = dict_objDefaultConfig[str_key]
        
        # smoothing設定の追加（古い設定ファイル用）
        if "smoothing" not in dict_objConfig:
            dict_objConfig["smoothing"] = dict_objDefaultConfig["smoothing"]
            print("smoothing設定を追加しました（デフォルト値使用）")
        
        # gain_mode設定の処理
        if "gain_mode" in dict_objConfig:
            b_bVariableMode = dict_objConfig["gain_mode"].get("variable_mode", True)
        else:
            # gain_mode自体がない場合はデフォルトを設定
            dict_objConfig["gain_mode"] = {
                "variable_mode": True,
            }
            print("gain_mode設定を追加しました（デフォルト値使用）")
        
        return dict_objConfig
        
    except json.JSONDecodeError as e:
        print(f"設定ファイルの解析エラー: {e}")
        return dict_objDefaultConfig
    except Exception as e:
        print(f"設定ファイルの読み込みエラー: {e}")
        return dict_objDefaultConfig

# ----- IIRFilter Class -----
class IIRFilter:
    LOW_PASS       = 0
    LOW_PASS_ODR1  = 1
    HIGH_PASS      = 2
    HIGH_PASS_ODR1 = 3
    ALL_PASS       = 4
    NONE           = 5

    def __init__(self, n_nFilterMode, f_fSampleRate, f_fCutoff):
        self.n_nFilterMode = n_nFilterMode  # フィルタモードを保持
        self.f_fCutoff = f_fCutoff
        self.f_fSampleRate = f_fSampleRate
        self.f_fA1 = self.f_fA2 = self.f_fA3 = self.f_fB1 = self.f_fB2 = 0.0
        self.list_fInPrev  = [0.0, 0.0]
        self.list_fOutPrev = [0.0, 0.0]

        if   n_nFilterMode == self.LOW_PASS:       self._lowPassFilter(f_fSampleRate, f_fCutoff)
        elif n_nFilterMode == self.LOW_PASS_ODR1:  self._lowPassFilter1(f_fSampleRate, f_fCutoff)
        elif n_nFilterMode == self.HIGH_PASS:      self._highPassFilter(f_fSampleRate, f_fCutoff)
        elif n_nFilterMode == self.HIGH_PASS_ODR1: self._highPassFilter1(f_fSampleRate, f_fCutoff)
        elif n_nFilterMode == self.NONE:           self._noneFilter()  # NONEフィルタの初期化
        else:                                       self._allPassFilter(f_fSampleRate, f_fCutoff)

    def compute(self, f_fInData:float) -> float:
        # NONEフィルタの場合は入力値をそのまま返す
        if self.n_nFilterMode == self.NONE:
            return f_fInData
        
        f_fRet = ( self.f_fA1 * f_fInData
                 + self.f_fA2 * self.list_fInPrev[0]
                 + self.f_fA3 * self.list_fInPrev[1]
                 - self.f_fB1 * self.list_fOutPrev[0]
                 - self.f_fB2 * self.list_fOutPrev[1] )

        self.list_fInPrev[1]  = self.list_fInPrev[0]
        self.list_fInPrev[0]  = f_fInData
        self.list_fOutPrev[1] = self.list_fOutPrev[0]
        self.list_fOutPrev[0] = f_fRet
        return f_fRet

    def reset(self):
        """フィルタの履歴（内部状態）をゼロに戻す"""
        self.list_fInPrev  = [0.0, 0.0]
        self.list_fOutPrev = [0.0, 0.0]

    def _noneFilter(self):
        """NONEフィルタ（パススルー）の初期化"""
        # 係数は使用しないが、初期化しておく
        self.f_fA1 = 1.0
        self.f_fA2 = 0.0
        self.f_fA3 = 0.0
        self.f_fB1 = 0.0
        self.f_fB2 = 0.0

    def _lowPassFilter(self, f_fSampleRate, f_fCutoff):
        f_fFa  = 1.0 / (2.0*math.pi) * math.tan(math.pi*f_fCutoff/f_fSampleRate)
        f_fPfc = 2.0*math.pi*f_fFa
        f_fRt2 = math.sqrt(2.0)

        f_fDenom = 1 + f_fRt2*f_fPfc + f_fPfc*f_fPfc
        self.f_fA1 = f_fPfc*f_fPfc / f_fDenom
        self.f_fA2 = 2.0*f_fPfc*f_fPfc / f_fDenom
        self.f_fA3 = f_fPfc*f_fPfc / f_fDenom
        self.f_fB1 = (-2.0 + 2.0*f_fPfc*f_fPfc) / f_fDenom
        self.f_fB2 = (1.0 - f_fRt2*f_fPfc + f_fPfc*f_fPfc) / f_fDenom

    def _lowPassFilter1(self, f_fSampleRate, f_fCutoff):
        f_fFa  = 1.0 / (2.0*math.pi) * math.tan(math.pi*f_fCutoff/f_fSampleRate)
        f_fPfc = 2.0*math.pi*f_fFa

        f_fDenom = f_fPfc + 1.0
        self.f_fA1 = f_fPfc / f_fDenom
        self.f_fA2 = f_fPfc / f_fDenom
        self.f_fA3 = 0.0
        self.f_fB1 = (f_fPfc - 1.0) / f_fDenom
        self.f_fB2 = 0.0

    def _highPassFilter(self, f_fSampleRate, f_fCutoff):
        f_fFa  = 1.0 / (2.0*math.pi) * math.tan(math.pi*f_fCutoff/f_fSampleRate)
        f_fPfc = 2.0*math.pi*f_fFa
        f_fRt2 = math.sqrt(2.0)

        f_fDenom = f_fPfc*f_fPfc + f_fRt2*f_fPfc + 1.0
        self.f_fA1 = 1.0 / f_fDenom
        self.f_fA2 = -2.0 / f_fDenom
        self.f_fA3 = 1.0 / f_fDenom
        self.f_fB1 = (2.0*f_fPfc*f_fPfc - 2.0) / f_fDenom
        self.f_fB2 = (f_fPfc*f_fPfc - f_fRt2*f_fPfc + 1.0) / f_fDenom

    def _highPassFilter1(self, f_fSampleRate, f_fCutoff):
        f_fFa  = 1.0 / (2.0*math.pi) * math.tan(math.pi*f_fCutoff/f_fSampleRate)
        f_fPfc = 2.0*math.pi*f_fFa

        f_fDenom = f_fPfc + 1.0
        self.f_fA1 = 1.0 / f_fDenom
        self.f_fA2 = -1.0 / f_fDenom
        self.f_fA3 = 0.0
        self.f_fB1 = (f_fPfc - 1.0) / f_fDenom
        self.f_fB2 = 0.0

    def _allPassFilter(self, f_fSampleRate, f_fCutoff):
        f_fW0    = 2.0 * math.pi * f_fCutoff / f_fSampleRate
        f_fAlpha = math.sin(f_fW0) / 2.0

        self.f_fA1 = (1.0 - f_fAlpha) / (1.0 + f_fAlpha)
        self.f_fA2 = -2.0 * math.cos(f_fW0) / (1.0 + f_fAlpha)
        self.f_fA3 = (1.0 + f_fAlpha) / (1.0 + f_fAlpha)
        self.f_fB1 = -2.0 * math.cos(f_fW0) / (1.0 + f_fAlpha)
        self.f_fB2 = (1.0 - f_fAlpha) / (1.0 + f_fAlpha)

# ----- Helper Functions -----
def get_filter_type(str_strType):
    """文字列からフィルタタイプを取得"""
    dict_objTypeMap = {
        "LOW_PASS": IIRFilter.LOW_PASS,
        "LOW_PASS_ODR1": IIRFilter.LOW_PASS_ODR1,
        "HIGH_PASS": IIRFilter.HIGH_PASS,
        "HIGH_PASS_ODR1": IIRFilter.HIGH_PASS_ODR1,
        "ALL_PASS": IIRFilter.ALL_PASS,
        "NONE": IIRFilter.NONE
    }
    return dict_objTypeMap.get(str_strType, IIRFilter.LOW_PASS)

# ----- functions -----
async def simvr_unified_loop(lock, list_objWorkData, dict_objConfig=None):
    """
    統合されたメインループ処理
    データ読み取りと出力を同一ループで管理
    """
    global g_dictSimvrVariable, g_bSimvrEndFlag, g_bMainProcess, g_bResetRequest, g_bExitRequest
    
    # 設定を読み込む
    if dict_objConfig is None:
        dict_objConfig = load_filter_config()
    
    dict_objFilterSettings = dict_objConfig.get("filter_settings", {})
    f_fSampleRate = dict_objFilterSettings.get("sample_rate", 100)
    dict_objFiltersConfig = dict_objFilterSettings.get("filters", {})
    dict_objSmoothingConfig = dict_objConfig.get("smoothing", {"enabled": True, "buffer_size": 3})
    
    f_fStartTime = float(list_objWorkData[0]['time'])
    f_fEndTime   = float(list_objWorkData[-1]['time'])
    print(f'DATA START:{f_fStartTime}s, END:{f_fEndTime}s')
    
    # データ補間器を初期化
    objInterpolator = DataInterpolator(list_objWorkData)
    
    # フィルタ配列の初期化
    list_strParamNames = ['heave', 'sway', 'surge', 'roll', 'pitch', 'yaw']
    list_objFilters = []
    dict_objNormalizationValues = {}
    dict_objUseDegrees = {}
    
    for str_param in list_strParamNames:
        if str_param in dict_objFiltersConfig:
            n_nFilterType = get_filter_type(dict_objFiltersConfig[str_param].get("type", "LOW_PASS"))
            f_fCutoff = dict_objFiltersConfig[str_param].get("cutoff", 2.0)
            dict_objNormalizationValues[str_param] = dict_objFiltersConfig[str_param].get("normalization", 1.0)
            dict_objUseDegrees[str_param] = dict_objFiltersConfig[str_param].get("is_radian", False)
            
            # NONEタイプの場合のログ出力
            if n_nFilterType == IIRFilter.NONE:
                print(f"  {str_param}: フィルタなし（NONE）")
        else:
            # デフォルト値
            n_nFilterType = IIRFilter.LOW_PASS
            f_fCutoff = 2.0 if str_param in ['heave', 'sway', 'surge'] else 1.25
            dict_objNormalizationValues[str_param] = 3.3 if str_param in ['heave', 'sway', 'surge'] else 10.0
            dict_objUseDegrees[str_param] = str_param in ['roll', 'pitch', 'yaw']
        
        list_objFilters.append(IIRFilter(n_nFilterType, f_fSampleRate, f_fCutoff))
    
    # スムージング用バッファの初期化
    dict_objSmoothingBuffers = {}
    if dict_objSmoothingConfig.get("enabled", True):
        n_nBufferSize = dict_objSmoothingConfig.get("buffer_size", 3)
        for str_param in list_strParamNames:
            dict_objSmoothingBuffers[str_param] = RingBuffer(n_nBufferSize)
    
    print(f"フィルタ設定: サンプルレート={f_fSampleRate}Hz")
    print(f"スムージング設定: 有効={dict_objSmoothingConfig.get('enabled', True)}, バッファサイズ={dict_objSmoothingConfig.get('buffer_size', 3)}")
    
    # gain_mode から accel/speed の初期値を反映（固定モード時はこの値を保持）
    dict_objGainMode = dict_objConfig.get("gain_mode", {})
    b_bVariableMode = dict_objGainMode.get("variable_mode", True)
    async with lock:
        g_dictSimvrVariable['variable_mode'] = b_bVariableMode
        g_dictSimvrVariable['speed_gain'] = float(dict_objGainMode.get('speed_gain', 0.667))
        g_dictSimvrVariable['accel_gain'] = float(dict_objGainMode.get('accel_gain', 0.03))
    print(f"ゲイン初期値: accel={g_dictSimvrVariable['accel_gain']}, speed={g_dictSimvrVariable['speed_gain']}, variable={b_bVariableMode}")

    await aio.sleep(1.0)  # 1秒待機
    
    # 実際の開始時刻を記録
    f_fSequenceStartTime = time.perf_counter()
    f_fTargetFrameTime = 1.0 / f_fSampleRate  # 目標フレーム時間
    n_nFrameCount = 0
    
    while not g_bExitRequest:
        # 停止時の「最初に戻す」リクエスト処理
        if g_bResetRequest:
            n_nFrameCount = 0
            objInterpolator.m_nCurrentIndex = 0
            for objFilter in list_objFilters:
                objFilter.reset()
            for str_paramKey in dict_objSmoothingBuffers:
                dict_objSmoothingBuffers[str_paramKey].clear()
            f_fSequenceStartTime = time.perf_counter()
            g_bResetRequest = False

        # 再生中かチェック（終了検知後も待機）
        if not g_bMainProcess or g_bSimvrEndFlag:
            await aio.sleep(0.01)
            # 一時停止から復帰した際の時刻補正
            f_fSequenceStartTime = time.perf_counter() - (n_nFrameCount * f_fTargetFrameTime)
            continue
        
        # フレーム開始時刻
        f_fFrameStartTime = time.perf_counter()
        
        # 現在のシーケンス時刻を計算
        f_fCurrentSequenceTime = (f_fFrameStartTime - f_fSequenceStartTime) + f_fStartTime
        
        # 終了判定（終了を通知して待機へ。ループは継続）
        if f_fCurrentSequenceTime >= f_fEndTime:
            g_bSimvrEndFlag = True
            continue
        
        # 補間されたデータを取得
        dict_objInterpolatedData, b_bIsEnd = objInterpolator.get_interpolated_data(f_fCurrentSequenceTime)
        if b_bIsEnd:
            g_bSimvrEndFlag = True
            continue              

        # フィルタ処理とスムージング
        dict_objFilteredValues = {}
        for n_nIdx, str_param in enumerate(list_strParamNames):
            if str_param in dict_objInterpolatedData:
                try:
                    f_fValue = float(dict_objInterpolatedData[str_param])
                except (ValueError, TypeError):
                    continue  # 空欄や不正値はスキップ
        
                norm_val = dict_objNormalizationValues[str_param]
                if str_param in ['roll','pitch','yaw']:
                    if dict_objFiltersConfig[str_param].get("is_radian", False):
                        # CSVが度ならラジアンに変換
                        f_fValue = math.degrees(f_fValue)
                
                f_fValue = f_fValue / norm_val
        
                # フィルタ適用
                f_fFilteredValue = list_objFilters[n_nIdx].compute(f_fValue)
        
                # スムージング適用
                if dict_objSmoothingConfig.get("enabled", True):
                    dict_objSmoothingBuffers[str_param].add(f_fFilteredValue)
                    avg = dict_objSmoothingBuffers[str_param].get_average()
                    f_fFilteredValue = avg if avg is not None else f_fFilteredValue
        
                dict_objFilteredValues[str_param] = f_fFilteredValue
            else:
                dict_objFilteredValues[str_param] = g_dictSimvrVariable[str_param]

        # データ更新
        async with lock:
            # 可変モードのときのみ CSV の speed/accel でゲインを上書き
            if b_bVariableMode:
                if 'speed' in dict_objInterpolatedData:
                    g_dictSimvrVariable['speed_gain'] = float(dict_objInterpolatedData['speed'])
                if 'accel' in dict_objInterpolatedData:
                    g_dictSimvrVariable['accel_gain'] = float(dict_objInterpolatedData['accel'])
            if 'is_origin' in dict_objInterpolatedData: 
                g_dictSimvrVariable['is_origin'] = int(dict_objInterpolatedData['is_origin'])
            
            g_dictSimvrVariable.update({
                'heave': dict_objFilteredValues['heave'],
                'sway':  dict_objFilteredValues['sway'],
                'surge': dict_objFilteredValues['surge'],
                'roll':  dict_objFilteredValues['roll'],
                'pitch': dict_objFilteredValues['pitch'],
                'yaw':   dict_objFilteredValues['yaw']
            })
        
        # フレームカウントを増加
        n_nFrameCount += 1

        # 現在の再生位置を表示（10フレームごと = 0.1秒ごと）
        if n_nFrameCount % 10 == 0:
            print(f'\r再生位置: {f_fCurrentSequenceTime:.2f}秒 / {f_fEndTime:.2f}秒 ({(f_fCurrentSequenceTime/f_fEndTime*100):.1f}%)', end='', flush=True)
        
        # 次のフレームまでの待機時間を計算
        f_fFrameEndTime = time.perf_counter()
        f_fProcessTime = f_fFrameEndTime - f_fFrameStartTime
        f_fWaitTime = f_fTargetFrameTime - f_fProcessTime
        
        if f_fWaitTime > 0:
            await aio.sleep(f_fWaitTime)
        elif n_nFrameCount % 100 == 0:  # 100フレームごとに警告
            print(f'警告: フレーム処理時間超過 ({f_fProcessTime*1000:.2f}ms > {f_fTargetFrameTime*1000:.2f}ms)')
    
    # 待機状態にリセット（関数の最後部分）
    dict_objGainMode = dict_objConfig.get("gain_mode", {})
    
    # デフォルトのゲイン値
    DEFAULT_SPEED_GAIN = 0.667
    DEFAULT_ACCEL_GAIN = 0.03
    
    async with lock:
        g_dictSimvrVariable.update({
            "variable_mode": dict_objGainMode.get('variable_mode', True),
            'speed_gain': dict_objGainMode.get('speed_gain', DEFAULT_SPEED_GAIN),
            'accel_gain': dict_objGainMode.get('accel_gain', DEFAULT_ACCEL_GAIN),
            'is_origin': 0,
            'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0,
            'heave':0.0, 'sway':0.0, 'surge':0.0
        })
    
    print('DATA FINISH')

def _read_csv_data(str_strCsvFilePath):
    print('Read CSV file name :', str_strCsvFilePath)
    with open(str_strCsvFilePath, 'r', newline='') as objFileCsv:
        objReader = csv.DictReader(objFileCsv)
        list_objData = sorted(objReader, key=lambda row: float(row['time']))
    return list_objData

async def _start_simvr_system(str_strVideoPath, str_strCsvPath, f_fFadeDuration, str_strConfigPath=None, n_nDisplayIndex=None, n_nDeviceCount=1):
    global g_bMainProcess, g_bSimvrEndFlag, g_bVideoRunning, _objPlayer, g_bResetRequest, g_bExitRequest, g_bStandbyOrigin
   
    b_bInitFlag = True
    b_bResumeFlag = False
    f_fScale = 1.0                   # 現在のフェード係数（0.0～1.0）
    
    # ── 再入禁止ガード ──
    if g_bVideoRunning:
        print("►すでに再生中です。処理をスキップします。")
        return
    g_bVideoRunning = True
    
    # 設定ファイルを読み込む
    dict_objConfig = load_filter_config(str_strConfigPath)
    
    # motion_ratio設定を取得
    dict_objMotionRatio = dict_objConfig.get("motion_ratio", {"rotation": 1.0, "gravity": 0.8})
    f_fMotionRatio1 = dict_objMotionRatio.get("rotation", 1.0)
    f_fMotionRatio2 = dict_objMotionRatio.get("gravity", 0.8)
    print(f"モーション比率設定: rotation={f_fMotionRatio1}, gravity={f_fMotionRatio2}")
    
    # gain_mode設定を取得
    dict_objGainMode = dict_objConfig.get("gain_mode", {})
    b_bVariableMode = dict_objGainMode.get('variable_mode', True)
    
    # 設定内容を表示
    if b_bVariableMode:
        print(f"ゲインモード設定: 可変モード(データ追従)")
    else:
        print(f"ゲインモード設定: CSVモード(データ参照)")
 
    windll.winmm.timeBeginPeriod(1)
    print('-------- START WIZMO-TOOLS --------')

    # 使用するデバイス（先頭から n_nDeviceCount 台）
    n_nCount = max(1, min(int(n_nDeviceCount), len(SERIALS)))
    list_strSerials = SERIALS[:n_nCount]
    print(f"使用デバイス台数: {len(list_strSerials)} / {len(SERIALS)}")

    list_objWizmo = []
    for i_nIndex, str_strSerial in enumerate(list_strSerials, start=1):
        try:
            obj_objWizmo = wizmo.wizmo(True)
        except FileNotFoundError:
            print("WIZMO DLL NOT FOUND ERROR!")
            for obj in list_objWizmo:      # すでに開いた分を閉じる
                obj.close()
            g_bVideoRunning = False
            return

        obj_objWizmo.starter('')   # シリアルで台を指定
        obj_objWizmo.axis_processing_mode(wizmo.wizmoAxisMode.Local)
        obj_objWizmo.simple_motion_ratio_update(f_fMotionRatio1, f_fMotionRatio2)

        # variable_mode設定に基づいてゲインモードを設定
        if b_bVariableMode:
            obj_objWizmo.speed_gain_mode(wizmo.wizmoSpeedGain.Variable)
        else:
            obj_objWizmo.speed_gain_mode(wizmo.wizmoSpeedGain.Normal)
            # 固定モードの場合、まずはデフォルトを設定
            obj_objWizmo.simple_motion_power_update(DEFAULT_ACCEL_GAIN, DEFAULT_SPEED_GAIN)

        obj_objWizmo.origin_mode(1)
        list_objWizmo.append(obj_objWizmo)
        print(f"  [{i_nIndex}/{len(list_strSerials)}] starter 実行: {str_strSerial}")

    print(f"WIZMO: {len(list_objWizmo)}台 starter 完了 "
          f"({'Variable' if b_bVariableMode else 'Normal'}モード)。接続を待機します...")

    # 全台が Initial を抜ける（=接続完了）まで待つ。
    # 1台でもシリアル不一致/未接続だと Initial のままなので、
    # タイムアウトを設けて「どの台が繋がっていないか」を表示する。
    f_fTimeoutSec = 15.0
    f_fDeadline = time.perf_counter() + f_fTimeoutSec
    while True:
        list_strPending = [
            list_strSerials[idx]
            for idx, obj in enumerate(list_objWizmo)
            if obj.get_status() == wizmo.wizmoStatus.Initial
        ]
        if not list_strPending:
            break
        if time.perf_counter() > f_fDeadline:
            print(f"!! 初期化タイムアウト（{f_fTimeoutSec:.0f}秒）。未接続の台:")
            for str_strNg in list_strPending:
                print("     -", str_strNg)
            print("   → シリアルの綴り(O/0の取り違え等)、電源/LAN、ライセンスを確認してください。")
            for obj in list_objWizmo:
                obj.close()
            g_bVideoRunning = False
            return
        await aio.sleep(0.1)

    print(f"WIZMO: {len(list_objWizmo)}台すべて接続完了")

    # 動画プレーヤーを先に作っておく
    f_fVideoLength = None
    obj_objVideoWindow = None   # 拡張ディスプレイ用の映像ウィンドウ
    if str_strVideoPath:            
        # Media オブジェクトを生成してセット
        objMedia = _objVlcInstance.media_new(str_strVideoPath)
        _objPlayer.set_media(objMedia)
        _objPlayer.set_fullscreen(False)

        # ── 拡張ディスプレイに枠なしウィンドウを作り、そこに映像を埋め込む ──
        obj_objRootTk = tk._default_root
        if obj_objRootTk is not None:
            obj_objVideoWindow = tk.Toplevel(obj_objRootTk)
        else:
            obj_objVideoWindow = tk.Tk()
        obj_objVideoWindow.overrideredirect(True)      # 枠・タイトルバー無し
        obj_objVideoWindow.configure(bg="black")
        obj_objVideoWindow.attributes("-topmost", True)

        tpl_MonRect = _get_target_monitor_rect(n_nDisplayIndex)
        if tpl_MonRect is not None:
            n_nLeft, n_nTop, n_nRight, n_nBottom = tpl_MonRect
            obj_objVideoWindow.geometry(
                f"{n_nRight - n_nLeft}x{n_nBottom - n_nTop}+{n_nLeft}+{n_nTop}"
            )

        obj_objVideoFrame = tk.Frame(obj_objVideoWindow, bg="black")
        obj_objVideoFrame.pack(fill=tk.BOTH, expand=True)
        obj_objVideoWindow.update_idletasks()
        obj_objVideoWindow.update()

        # 埋め込み先ウィンドウの hwnd を VLC に渡す
        _objPlayer.set_hwnd(obj_objVideoFrame.winfo_id())
        obj_objVideoWindow.withdraw()   # 起動時は非表示（停止状態）
        await aio.sleep(0.5)

        # シークや長さ取得も同じ player を使う
        f_fVideoLength = _objPlayer.get_length() / 1000.0
        _objPlayer.set_time(0)

    # 初期状態は待機（再生・シーケンス始動ともオフ） 
    b_bPaused = True
    g_bMainProcess = False
    g_bSimvrEndFlag = False
    g_bExitRequest = False
    print("► スペースキーを押して再生／シーケンスを開始してください")

    # スペースで再生／シーケンス開始 or 一時停止
    def _toggle_play_pause():       
        nonlocal b_bPaused, b_bResumeFlag, b_bInitFlag
        global g_bMainProcess, g_bResetRequest, g_bStandbyOrigin
        
        b_bPaused = not b_bPaused
        g_bMainProcess = not b_bPaused       

        # 待機中はオリジン復帰しない（heave=1.0 はメインループ側で保持）
        g_dictSimvrVariable['is_origin'] = 0
        for obj in list_objWizmo:
            obj.origin_mode(False)

        # 動画制御      
        if b_bPaused:
            g_bStandbyOrigin = True       # 停止＝origin に戻す
            g_bResetRequest = True        # シーケンスを最初に戻す
            _objPlayer.stop()             # 動画を停止して先頭に戻す（Ended状態でも確実にリセット）
        else:             
            _objPlayer.play()             # 停止状態から先頭再生       

        if b_bPaused:
            print("\n► 停止中／待機中です。スペースキーで開始してください")
            b_bInitFlag = False
        else:
            b_bResumeFlag = True
            print("► 再生を開始しました（is_origin=0）")

    # ── pynput でキー入力を監視（space=再生/停止, Esc=終了, R=待機heave切替）──

    # Escキーで再生を終了してGUIに戻る
    def _request_end():
        global g_bExitRequest
        g_bExitRequest = True
        print("► Escが押されました。再生を終了してGUIに戻ります")

    # Rキーで待機heaveを 0.0（is_origin解除）/ 1.0 に切り替え
    def _toggle_standby_heave():
        global g_bStandbyOrigin
        g_bStandbyOrigin = not g_bStandbyOrigin
        if g_bStandbyOrigin:
            print("► R: is_origin=True / heave=1.0")
        else:
            print("► R: is_origin=False / heave=0.0")

    # キー離上時に実行（旧 keyboard の trigger_on_release=True 相当）
    def _on_key_release(objKey):
        try:
            if objKey == pynput_keyboard.Key.space:
                _toggle_play_pause()
            elif objKey == pynput_keyboard.Key.esc:
                _request_end()
            elif getattr(objKey, "char", None) and objKey.char.lower() == "r":
                _toggle_standby_heave()
        except Exception as e:
            print("キー処理エラー:", e)

    objKeyListener = pynput_keyboard.Listener(on_release=_on_key_release)
    objKeyListener.start()

    # CSVを読み込んで統合ループ開始
    list_objDataContent = _read_csv_data(str_strCsvPath)
    objLock = aio.Lock()
    objScTask = aio.create_task(simvr_unified_loop(objLock, list_objDataContent, dict_objConfig))   

    try:
        f_fLastUpdateTime = time.perf_counter()
        f_fTargetInterval = 0.01  # 10msごとの更新を目標（100Hz）
        b_bVideoShown = False   # 映像ウィンドウの表示状態

        # ── USB切断時の自動再接続 ──
        set_reconnecting = set()   # 再接続中のデバイスindex

        def _reconnect_worker(n_nIdx):
            try:
                print(f"► デバイス{n_nIdx}: 切断を検知。再接続します...")
                try:
                    list_objWizmo[n_nIdx].close()
                except Exception:
                    pass
                obj_new = wizmo.wizmo(True)
                obj_new.starter('')
                obj_new.axis_processing_mode(wizmo.wizmoAxisMode.Local)
                obj_new.simple_motion_ratio_update(f_fMotionRatio1, f_fMotionRatio2)
                if b_bVariableMode:
                    obj_new.speed_gain_mode(wizmo.wizmoSpeedGain.Variable)
                else:
                    obj_new.speed_gain_mode(wizmo.wizmoSpeedGain.Normal)
                    obj_new.simple_motion_power_update(DEFAULT_ACCEL_GAIN, DEFAULT_SPEED_GAIN)
                obj_new.origin_mode(1)
                # 初期化完了を待つ（最大5秒）
                f_fT0 = time.perf_counter()
                while (obj_new.get_status() == wizmo.wizmoStatus.Initial
                       and time.perf_counter() - f_fT0 < 5.0):
                    time.sleep(0.05)
                list_objWizmo[n_nIdx] = obj_new
                print(f"► デバイス{n_nIdx}: 再接続完了")
            except Exception as e:
                print(f"► デバイス{n_nIdx}: 再接続失敗: {e}")
            finally:
                set_reconnecting.discard(n_nIdx)

        # 1台が切断してもループは止めない（切断台だけ再接続、他は継続）
        while True:
            # 現在時刻を取得
            f_fCurrentTime = time.perf_counter()

            # 終了リクエスト（Escキー）を最優先で判定
            if g_bExitRequest:
                break

            # USB切断チェック → 切断された台だけ再接続（他は継続）
            for n_nIdx in range(len(list_objWizmo)):
                if n_nIdx not in set_reconnecting and not list_objWizmo[n_nIdx].is_running():
                    set_reconnecting.add(n_nIdx)
                    threading.Thread(target=_reconnect_worker, args=(n_nIdx,), daemon=True).start()
        
            # 拡張ディスプレイの映像ウィンドウを描画更新
            if obj_objVideoWindow is not None:
                try:
                    obj_objVideoWindow.update()
                except tk.TclError:
                    obj_objVideoWindow = None

            # 再生中は映像ウィンドウを表示、停止中は非表示
            if obj_objVideoWindow is not None:
                if g_bMainProcess and not b_bVideoShown:
                    obj_objVideoWindow.deiconify()
                    obj_objVideoWindow.attributes("-topmost", True)
                    obj_objVideoWindow.lift()
                    b_bVideoShown = True
                elif not g_bMainProcess and b_bVideoShown:
                    obj_objVideoWindow.withdraw()
                    b_bVideoShown = False

            # 待機中: is_origin=True→heave=1.0 / False→heave=0.0（Rキーで切替）
            if not g_bMainProcess:
                f_fStandbyHeave = 1.0 if g_bStandbyOrigin else 0.0
                async with objLock:
                    for idx, obj in enumerate(list_objWizmo):
                        if idx in set_reconnecting:
                            continue
                        obj.origin_mode(False)   # オリジンモードは常にオフ
                        obj.simple_motion_power_update(
                            g_dictSimvrVariable['accel_gain'],
                            g_dictSimvrVariable['speed_gain']
                        )
                        obj.simple_pose_update(
                            0.0, 0.0, 0.0,      # roll, pitch, yaw
                            f_fStandbyHeave,    # heave (True=1.0 / False=0.0)
                            0.0, 0.0            # sway, surge
                        )
                for obj in list_objWizmo:
                    obj.get_backlog(True)
                await aio.sleep(0.01)
                f_fLastUpdateTime = f_fCurrentTime  # 再開時のために時刻をリセット
                continue

            # 終了判定（動画 or シーケンス）→ スペース停止と同じ待機へ
            b_bReachedEnd = False
            if _objPlayer and f_fVideoLength and f_fVideoLength > 0:
                f_fVideoPosition = _objPlayer.get_time() / 1000.0
                if f_fVideoPosition >= (f_fVideoLength - 2.0) or g_bSimvrEndFlag:
                    b_bReachedEnd = True
            else:
                if g_bSimvrEndFlag:
                    b_bReachedEnd = True

            if b_bReachedEnd:
                # 再生終了 → スペース停止と同じ待機へ（GUIには戻らない）
                g_bMainProcess = False
                g_bStandbyOrigin = True
                b_bPaused = True
                b_bInitFlag = False
                g_dictSimvrVariable['is_origin'] = 0
                for obj in list_objWizmo:
                    obj.origin_mode(False)
                g_bResetRequest = True
                g_bSimvrEndFlag = False
                _objPlayer.stop()             # 終了後も確実に頭出しできるよう stop()
                print("\n► 再生が終了しました。待機中です。スペースキーで再開してください")
                continue

            # フェード処理
            f_fDeltaTime = f_fCurrentTime - f_fLastUpdateTime
            f_fDelta = f_fDeltaTime / f_fFadeDuration

            if b_bResumeFlag and not b_bInitFlag:                                          
                f_fScale = 0.0
                b_bResumeFlag = False
            else:
                # scale を 0→1 までインクリメント
                if f_fScale < 1.0:
                    f_fScale = min(f_fScale + f_fDelta, 1.0)                             
        
            # スケール適用
            dict_objScaledValues = {
                'roll':  g_dictSimvrVariable['roll'] * f_fScale,
                'pitch': g_dictSimvrVariable['pitch'] * f_fScale,
                'yaw':   g_dictSimvrVariable['yaw'] * f_fScale,
                'heave': g_dictSimvrVariable['heave'] * f_fScale,
                'sway':  g_dictSimvrVariable['sway'] * f_fScale,
                'surge': g_dictSimvrVariable['surge'] * f_fScale
            }

            # Wizmo 更新
            async with objLock:
                for idx, obj in enumerate(list_objWizmo):
                    if idx in set_reconnecting:
                        continue
                    obj.origin_mode(g_dictSimvrVariable['is_origin'] == 1)

                    # variable_modeがTrueの場合のみゲイン更新を行う
                    obj.simple_motion_power_update(
                        g_dictSimvrVariable['accel_gain'],
                        g_dictSimvrVariable['speed_gain']
                    )

                    obj.simple_pose_update(
                        dict_objScaledValues['roll'],
                        dict_objScaledValues['pitch'],
                        dict_objScaledValues['yaw'],
                        dict_objScaledValues['heave'],
                        dict_objScaledValues['sway'],
                        dict_objScaledValues['surge']
                    )
            for obj in list_objWizmo:
                obj.get_backlog(True)
        
            # 次の更新までの待機時間を計算
            f_fElapsedTime = time.perf_counter() - f_fCurrentTime
            f_fSleepTime = f_fTargetInterval - f_fElapsedTime
        
            if f_fSleepTime > 0:
                await aio.sleep(f_fSleepTime)
        
            f_fLastUpdateTime = f_fCurrentTime

    except KeyboardInterrupt:
        print('SIMVR System Canceled!')

    # 後片付け
    if _objPlayer:
        _objPlayer.stop()

    # 拡張ディスプレイの映像ウィンドウを閉じる
    if obj_objVideoWindow is not None:
        try:
            obj_objVideoWindow.destroy()
        except Exception:
            pass

    objScTask.cancel()
    await aio.sleep(1)
    for obj in list_objWizmo:
        obj.close()
        obj.get_backlog(True)
    windll.winmm.timeEndPeriod(1)
    g_bVideoRunning = False
    try:
        objKeyListener.stop()
    except Exception:
        pass
  
    print('-------- FINISH WIZMO-TOOLS --------')

def start_simvr(str_strVideoPath, str_strCsvPath, f_fFadeDuration, str_strConfigPath=None, n_nDisplayIndex=None, n_nDeviceCount=1):
    aio.run(_start_simvr_system(str_strVideoPath, str_strCsvPath, f_fFadeDuration, str_strConfigPath, n_nDisplayIndex, n_nDeviceCount))

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python script.py <video_path or empty> <csv_path> [config_path] [display_index] [device_count]")
    else:
        str_strVideoArg = sys.argv[1] if sys.argv[1] != "" else None
        str_strCsvArg   = sys.argv[2]
        str_strConfigArg = sys.argv[3] if len(sys.argv) > 3 else None
        n_nDisplayArg = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else None
        n_nCountArg = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5].isdigit() else 1
        start_simvr(str_strVideoArg, str_strCsvArg, 2.0, str_strConfigArg, n_nDisplayArg, n_nCountArg)