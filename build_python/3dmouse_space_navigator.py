import hid
import struct
import csv
import time
import keyboard
import wizmo
from datetime import datetime
from ctypes import windll

# -----------------------------
# SIMVR / WIZMO 変数
# -----------------------------
simvr_variable = {
    'heave': 0.0,
    'sway': 0.0,
    'surge': 0.0,
    'pitch': 0.0,
    'roll': 0.0,
    'yaw': 0.0,
    'accel_gain': 0.5,
    'speed_gain': 0.5,
    'is_origin': 0
}

# -----------------------------
# SpaceNavigator 設定
# -----------------------------
VENDOR_ID = 0x46D
PRODUCT_ID = 0xC626
MAX_VAL = 350.0

def normalize(v):
    return max(-1.0, min(1.0, v / MAX_VAL))

# -----------------------------
# WIZMO 初期化
# -----------------------------
windll.winmm.timeBeginPeriod(1)

wm = None

try:
    wm = wizmo.wizmo(True)
except FileNotFoundError:
    print("ERROR: WIZMO DLL が見つかりません。wizmo.dll を確認してください。")
    exit(1)
except Exception as e:
    print("ERROR: WIZMO 初期化中に予期しないエラーが発生しました:", e)
    exit(1)

try:
    wm.starter('')
except Exception as e:
    print("ERROR: WIZMO の starter() 実行に失敗しました:", e)
    wm.close()
    exit(1)

# 初期化完了待ち
timeout = 5.0
start_wait = time.time()

while wm.get_status() == wizmo.wizmoStatus.Initial:
    if time.time() - start_wait > timeout:
        print("ERROR: WIZMO が初期化状態から進みません（タイムアウト）")
        wm.close()
        exit(1)
    time.sleep(0.1)

# 初期設定
try:
    wm.simple_motion_ratio_update(0.66, 0.1)
    wm.speed_gain_mode(wizmo.wizmoSpeedGain.Variable)
except Exception as e:
    print("ERROR: WIZMO 初期設定に失敗しました:", e)
    wm.close()
    exit(1)

print("WIZMO initialized successfully")

# -----------------------------
# SpaceNavigator 初期化
# -----------------------------
h = hid.device()
h.open(VENDOR_ID, PRODUCT_ID)
h.set_nonblocking(True)

print("SpaceNavigator connected")

sixdof = {
    "roll": 0.0,
    "pitch": 0.0,
    "yaw": 0.0,
    "heave": 0.0,
    "sway": 0.0,
    "surge": 0.0,
}

# -----------------------------
# CSV ファイル名
# -----------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"spacenav_data_{timestamp}.csv"

csv_file = open(csv_filename, "w", newline="", encoding="utf-8")
writer = csv.writer(csv_file)
writer.writerow(["time", "roll", "pitch", "yaw", "heave", "sway", "surge"])

# -----------------------------
# 録画制御
# -----------------------------
recording = False
pure_time = 0.0
last_record_time = None
running = True

def toggle_recording(e):
    global recording, last_record_time
    recording = not recording
    if recording:
        last_record_time = time.time()
        print("Recording started")
    else:
        print("Recording paused")

def stop_program(e):
    global running
    running = False
    print("ESC pressed. Exiting...")

keyboard.on_press_key("space", toggle_recording)
keyboard.on_press_key("esc", stop_program)

print("Press SPACE to start/pause recording. Press ESC to exit.")

# -----------------------------
# メインループ
# -----------------------------
WRITE_INTERVAL = 1.0 / 100.0
last_write = time.time()

while running:
    data = h.read(64)

    if data:
        report_id = data[0]

        if report_id == 1:
            raw_x = struct.unpack('<h', bytes(data[1:3]))[0]
            raw_y = struct.unpack('<h', bytes(data[3:5]))[0]
            raw_z = struct.unpack('<h', bytes(data[5:7]))[0]

            sixdof["surge"] = -normalize(raw_y)# 逆のため変換
            sixdof["sway"]  = normalize(raw_x)
            sixdof["heave"] = normalize(raw_z)

        elif report_id == 2:
            rx = struct.unpack('<h', bytes(data[1:3]))[0]
            ry = struct.unpack('<h', bytes(data[3:5]))[0]
            rz = struct.unpack('<h', bytes(data[5:7]))[0]

            sixdof["pitch"] = normalize(rx)
            sixdof["roll"]  = -normalize(ry)# 逆のため変換
            sixdof["yaw"]   = normalize(rz)

    now = time.time()

    # 記録時間の加算
    if recording:
        pure_time += now - last_record_time
        last_record_time = now

    # 100Hz 更新
    if recording and (now - last_write >= WRITE_INTERVAL):

        print(
            f"time:{pure_time:6.3f}  "
            f"roll:{sixdof['roll']:+.3f}  "
            f"pitch:{sixdof['pitch']:+.3f}  "
            f"yaw:{sixdof['yaw']:+.3f}  "
            f"heave:{sixdof['heave']:+.3f}  "
            f"sway:{sixdof['sway']:+.3f}  "
            f"surge:{sixdof['surge']:+.3f}"
        )

        # -----------------------------
        # SpaceNavigator → simvr_variable
        # -----------------------------
        simvr_variable['roll']  = sixdof['roll']
        simvr_variable['pitch'] = sixdof['pitch']
        simvr_variable['yaw']   = sixdof['yaw']
        simvr_variable['heave'] = sixdof['heave']
        simvr_variable['sway']  = sixdof['sway']
        simvr_variable['surge'] = sixdof['surge']

        # -----------------------------
        # WIZMO へ送信
        # -----------------------------
        wm.origin_mode(simvr_variable['is_origin'] == 1)

        wm.simple_motion_power_update(
            simvr_variable['accel_gain'],
            simvr_variable['speed_gain']
        )

        wm.simple_pose_update(
            simvr_variable['roll'],
            simvr_variable['pitch'],
            simvr_variable['yaw'],
            simvr_variable['heave'],
            simvr_variable['sway'],
            simvr_variable['surge']
        )        

        # -----------------------------
        # CSV 書き込み
        # -----------------------------
        writer.writerow([
            round(pure_time, 3),
            round(sixdof["roll"], 3),
            round(sixdof["pitch"], 3),
            round(sixdof["yaw"], 3),
            round(sixdof["heave"], 3),
            round(sixdof["sway"], 3),
            round(sixdof["surge"], 3)
        ])

        csv_file.flush()
        last_write = now

    time.sleep(0.001)

# -----------------------------
# 終了処理
# -----------------------------
csv_file.close()
wm.close()
windll.winmm.timeEndPeriod(1)

print("Program terminated.")