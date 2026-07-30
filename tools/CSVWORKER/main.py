import os
import tkinter as tk
from tkinter import filedialog, PhotoImage, messagebox
from ctypes import windll, byref, sizeof, c_int

import main_simvr

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 595  # 設定・ディスプレイ・台数選択欄のために高さを増やす

# ── 追加: スペース単押しガード用フラグ ──
space_pressed = False

#----------------Define----------------
# 角を丸くするための関数
def round_corners(hwnd, radius=10):
    region =windll.gdi32.CreateRoundRectRgn(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, radius, radius)
    windll.user32.SetWindowRgn(hwnd, region, True)

def select_file(entry_widget, filetype):
    if filetype==0:
        fTyp = [("MP4動画ファイル", "*.mp4")]
    elif filetype==1:
        fTyp = [("CSVファイル", "*.csv")]
    else:  # filetype==2 for JSON config
        fTyp = [("JSON設定ファイル", "*.json"), ("すべてのファイル", "*.*")]
    
    file_path = filedialog.askopenfilename(filetypes=fTyp)
    if file_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path)

def add_shadow(hwnd):
    # WindowsのAPIを利用してウィンドウに影を追加 未対応?
    DWMWA_NCRENDERING_POLICY = 2
    DWMWA_ALLOW_NCPAINT = 4
    DWMWA_BORDER_COLOR = 34
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Windows 10 以降のダークモード対応
    DWMNCRP_ENABLED = 2

    # 影の設定を有効化
    set_window_attribute = windll.dwmapi.DwmSetWindowAttribute
    set_window_attribute(hwnd, DWMWA_NCRENDERING_POLICY, byref(c_int(DWMNCRP_ENABLED)), sizeof(c_int))
    set_window_attribute(hwnd, DWMWA_ALLOW_NCPAINT, byref(c_int(1)), sizeof(c_int))
    set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(c_int(2)), 4)

    # 影を適用する
    windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, byref(c_int(-1)))

def execute():
    global space_pressed
    # 実行後はすぐにフラグをリセットする (二重ガードでも安心)
    space_pressed = False

    # ユーザ入力を取得
    video_path = entry1.get().strip()
    csv_path   = entry2.get().strip()
    config_path = entry3.get().strip() or None  # 空欄の場合はNone
    
    # CSVは必須。存在チェックに失敗したらエラーを出して終了
    if not csv_path or not os.path.isfile(csv_path):
        messagebox.showerror(
            '動作ファイルが存在していません',
            '動作ファイル(csv)が存在していません。'
        )
        return
    
    # 動画パスが指定されている場合のみ存在チェック
    if video_path:
        if not os.path.isfile(video_path):
            # 存在しない場合は動画をスキップ
            messagebox.showwarning(
                '動画ファイルが見つかりません',
                '指定された動画ファイルが見つかりません。\n空欄にすると動画なしで実行します。'
            )
            video_path = None
    else:
        # 空欄ならNoneにしてスキップ
        video_path = None
    
    # 設定ファイルが指定されている場合の存在チェック
    if config_path and not os.path.isfile(config_path):
        result = messagebox.askyesno(
            '設定ファイルが見つかりません',
            f'指定された設定ファイル "{config_path}" が見つかりません。\nデフォルト設定を使用しますか？'
        )
        if not result:
            return
        config_path = None
    
    print("動画ファイル(mp4):", video_path or '（未指定）')
    print("動作ファイル(csv):", csv_path)
    print("設定ファイル(json):", config_path or '（デフォルト）')
    print('実行します。')
    
    # 表示ディスプレイの選択を取得（自動＝None、それ以外はインデックス）
    _strDisp = display_var.get()
    if _strDisp.startswith("自動"):
        display_index = None
    else:
        try:
            display_index = int(_strDisp.split()[1])
        except (IndexError, ValueError):
            display_index = None
    print("表示ディスプレイ:", display_index if display_index is not None else "（自動：拡張ディスプレイ）")

    # 使用台数を取得（数値入力。範囲外・不正は補正）
    try:
        device_count = int(device_var.get())
    except ValueError:
        device_count = 1
    device_count = max(1, min(device_count, _n_max_devices))
    print("使用台数:", device_count)

    # メインウィンドウを隠して処理実行
    root.withdraw()    
    main_simvr.start_simvr(video_path, csv_path, 2.0, config_path, display_index, device_count)
    # 終了後に戻す
    root.deiconify()
    root.focus_force()
    root.lift()

def close_app():
    root.destroy()

# def execute_key(self, event=None):
#     execute()

# 単押し用: 押下時
def execute_key(event):
    global space_pressed
    if space_pressed:
        return
    space_pressed = True
    execute()

# 単押し用: 離上時
def reset_space_flag(event):
    global space_pressed
    space_pressed = False

# ウィンドウをドラッグで移動するための関数
def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def on_move(event):
    x = root.winfo_x() + (event.x - root.x)
    y = root.winfo_y() + (event.y - root.y)
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

# 画面中央に配置（マージンを追加）
def center_window(w, h):
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - w) // 2
    y = (screen_height - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.resizable(False, False)

def create_default_config():
    """デフォルト設定ファイルを作成"""
    if not os.path.exists("filter_config.json"):
        try:
            import json
            default_config = {
                "description": "SIVMRフィルタおよび正規化設定ファイル",
                "filter_settings": {
                    "sample_rate": 100,
                    "filters": {
                        "heave": {
                            "type": "LOW_PASS",
                            "cutoff": 2.55,
                            "normalization": 3.3
                        },
                        "sway": {
                            "type": "LOW_PASS",
                            "cutoff": 2.55,
                            "normalization": 3.3
                        },
                        "surge": {
                            "type": "LOW_PASS",
                            "cutoff": 2.55,
                            "normalization": 3.3
                        },
                        "roll": {
                            "type": "LOW_PASS",
                            "cutoff": 1.25,
                            "normalization": 16.0,
                            "is_radian": True
                        },
                        "pitch": {
                            "type": "LOW_PASS",
                            "cutoff": 1.25,
                            "normalization": 16.0,
                            "is_radian": True
                        },
                        "yaw": {
                            "type": "LOW_PASS",
                            "cutoff": 1.25,
                            "normalization": 16.0,
                            "is_radian": True
                        }
                    }
                },
                "motion_ratio": {
                    "rotation": 0.9,
                    "gravity": 0.8
                },
                "gain_mode": {
                    "variable_mode": True  # 可変モード（CSVデータ使用）のみ指定
                },
                "smoothing": {
                    "enabled": True,
                    "buffer_size": 3
                }
            }
            with open("filter_config.json", 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print("デフォルト設定ファイル 'filter_config.json' を作成しました。")
        except Exception as e:
            print(f"設定ファイルの作成に失敗: {e}")

#-------------------------------------------------------------------------

# ── 引数モード: 引数があればGUIを飛ばして再生待機へ直行 ──
# 使い方: python main.py <mp4パス or ""> <csvパス> [configパス] [ディスプレイ番号] [使用台数]
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        _strVideoArg  = sys.argv[1].strip() if len(sys.argv) >= 2 else ""
        _strCsvArg    = sys.argv[2].strip() if len(sys.argv) >= 3 else ""
        _strConfigArg = sys.argv[3].strip() if len(sys.argv) >= 4 else ""
        _strDisplayArg = sys.argv[4].strip() if len(sys.argv) >= 5 else ""
        _strCountArg   = sys.argv[5].strip() if len(sys.argv) >= 6 else ""

        _videoPath  = _strVideoArg or None
        _csvPath    = _strCsvArg or None
        _configPath = _strConfigArg or None
        _displayIndex = int(_strDisplayArg) if _strDisplayArg.isdigit() else None
        _deviceCount = int(_strCountArg) if _strCountArg.isdigit() else 1

        # CSVは必須
        if not _csvPath or not os.path.isfile(_csvPath):
            print("エラー: 動作ファイル(csv)が存在しません:", _csvPath)
            sys.exit(1)

        # 動画は任意（無ければ動画なし）
        if _videoPath and not os.path.isfile(_videoPath):
            print("警告: 動画ファイルが見つかりません。動画なしで実行します:", _videoPath)
            _videoPath = None

        # 設定は任意（無ければデフォルト）
        if _configPath and not os.path.isfile(_configPath):
            print("警告: 設定ファイルが見つかりません。デフォルト設定を使用します:", _configPath)
            _configPath = None

        create_default_config()

        print("引数モードで起動します。スペースキーで再生を開始してください。")
        print("動画ファイル(mp4):", _videoPath or "（未指定）")
        print("動作ファイル(csv):", _csvPath)
        print("設定ファイル(json):", _configPath or "（デフォルト）")
        print("表示ディスプレイ:", _displayIndex if _displayIndex is not None else "（自動：拡張ディスプレイ）")
        print("使用台数:", _deviceCount)

        main_simvr.start_simvr(_videoPath, _csvPath, 2.0, _configPath, _displayIndex, _deviceCount)
        sys.exit(0)


# メインウィンドウの作成
root = tk.Tk()
root.title("WIZMO VIDEO SIM") 
root.overrideredirect(True)  # タイトルバーを非表示にする
root.configure(bg="#2c2f33")  # ダークテーマの背景色
root.attributes("-topmost", True)

#センター
center_window(WINDOW_WIDTH,WINDOW_HEIGHT)

# ウィンドウの角を丸くする
root.update_idletasks()
hwnd = windll.user32.GetParent(root.winfo_id())
round_corners(hwnd)
#add_shadow(hwnd)

# デフォルト設定ファイルを作成（存在しない場合）
create_default_config()

# スタイリング
button_style = {"font": ("ＭＳ ゴシック", 11), "bg": "#7289da", "fg": "white", "padx": 10, "pady": 5, "bd": 0, "relief": tk.FLAT}
button_style_finish = {"font": ("ＭＳ ゴシック", 11), "bg": "#33499a", "fg": "white", "padx": 10, "pady": 5, "bd": 0, "relief": tk.FLAT}
entry_style = {"font": ("ＭＳ ゴシック", 11), "width": 30, "bd": 2, "relief": tk.FLAT, "bg": "#23272a", "fg": "white"}
label_style = {"font": ("ＭＳ ゴシック", 11), "bg": "#2c2f33", "fg": "white", "width": 19, "anchor": "w"}
label_style_small = {"font": ("ＭＳ ゴシック", 9), "bg": "#2c2f33", "fg": "#999999"}

# コンテンツ全体にマージンを追加
content_frame = tk.Frame(root, bg="#2c2f33", padx=10, pady=10)
content_frame.pack(fill=tk.BOTH, expand=True)

# 画像のロード（ロゴ）
logo_image = PhotoImage(file="wizmo_lib.glib") 
logo_label = tk.Label(content_frame,width=330, height=180, image=logo_image, cursor="fleur", borderwidth=0)
logo_label.pack()

# ウィンドウ移動のためのバインド
logo_label.bind("<ButtonPress-1>", start_move)
logo_label.bind("<ButtonRelease-1>", stop_move)
logo_label.bind("<B1-Motion>", on_move)

# #スペースで再生
# root.bind("<space>", execute_key)

# スペースキーのバインドを「押下」と「離上」に分ける
root.bind("<KeyPress-space>", execute_key)
root.bind("<KeyRelease-space>", reset_space_flag)

# ファイル1選択（動画）
frame1 = tk.Frame(content_frame, bg="#2c2f33")
frame1.pack(pady=5, fill=tk.X)
tk.Label(frame1, text="動画ファイル(mp4):", **label_style).pack(side=tk.LEFT)
entry1 = tk.Entry(frame1, **entry_style)
entry1.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
button1 = tk.Button(frame1, text="開く", command=lambda: select_file(entry1, 0), **button_style)
button1.pack(side=tk.RIGHT)

# ファイル2選択（CSV）
frame2 = tk.Frame(content_frame, bg="#2c2f33")
frame2.pack(pady=5, fill=tk.X)
tk.Label(frame2, text="動作ファイル(csv):", **label_style).pack(side=tk.LEFT)
entry2 = tk.Entry(frame2, **entry_style)
entry2.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
button2 = tk.Button(frame2, text="開く", command=lambda: select_file(entry2, 1), **button_style)
button2.pack(side=tk.RIGHT)

# ファイル3選択（設定ファイル）
frame3 = tk.Frame(content_frame, bg="#2c2f33")
frame3.pack(pady=5, fill=tk.X)
tk.Label(frame3, text="設定ファイル(json):", **label_style).pack(side=tk.LEFT)
entry3 = tk.Entry(frame3, **entry_style)
entry3.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
# デフォルトでfilter_config.jsonを設定
entry3.insert(0, "filter_config.json")
button3 = tk.Button(frame3, text="開く", command=lambda: select_file(entry3, 2), **button_style)
button3.pack(side=tk.RIGHT)

# 表示ディスプレイ選択
frame4 = tk.Frame(content_frame, bg="#2c2f33")
frame4.pack(pady=5, fill=tk.X)
tk.Label(frame4, text="表示ディスプレイ:", **label_style).pack(side=tk.LEFT)

_list_monitors = main_simvr.get_monitors()
display_options = ["自動（拡張ディスプレイ）"]
for _i, (_l, _t, _r, _b) in enumerate(_list_monitors):
    display_options.append(f"ディスプレイ {_i} ({_r - _l}x{_b - _t})")

display_var = tk.StringVar(value=display_options[0])
display_menu = tk.OptionMenu(frame4, display_var, *display_options)
display_menu.config(font=("ＭＳ ゴシック", 10), bg="#23272a", fg="white",
                    bd=0, highlightthickness=0, activebackground="#7289da",
                    relief=tk.FLAT, anchor="w", padx=8, pady=3, cursor="hand2")
display_menu["menu"].config(bg="#23272a", fg="white",
                            activebackground="#7289da", activeforeground="white")
display_menu.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

# 使用台数（数値入力）
frame5 = tk.Frame(content_frame, bg="#2c2f33")
frame5.pack(pady=5, fill=tk.X)
tk.Label(frame5, text="使用台数:", **label_style).pack(side=tk.LEFT)

_n_max_devices = len(main_simvr.get_device_serials())
device_var = tk.StringVar(value="1")   # デフォルト1台
device_spin = tk.Spinbox(
    frame5, from_=1, to=_n_max_devices, textvariable=device_var,
    font=("ＭＳ ゴシック", 11), width=5, justify=tk.CENTER,
    bd=2, relief=tk.FLAT, bg="#23272a", fg="white",
    insertbackground="white", buttonbackground="#7289da", highlightthickness=0
)
device_spin.pack(side=tk.LEFT, padx=5)
tk.Label(frame5, text=f"台（最大 {_n_max_devices}）",
         font=("ＭＳ ゴシック", 10), bg="#2c2f33", fg="#999999").pack(side=tk.LEFT)

# 設定ファイルの説明
info_label = tk.Label(content_frame, text="※ 設定ファイルを空欄にするとデフォルト設定を使用します", **label_style_small)
info_label.pack(pady=2)

# 実行ボタン
execute_button = tk.Button(content_frame, text="再生・実行", width=20, height=2, command=execute, **button_style)
execute_button.pack(pady=10)

# 終了ボタン
close_button = tk.Button(content_frame, text="終了", width=20, height=2, command=close_app, **button_style_finish)
close_button.pack(pady=10)

# メインループ
if __name__ == "__main__":
    root.mainloop()