/**************************************************************************
*
*              Copyright (c) 2014-2026 by WIZAPPLY.
*
*  This software is copyrighted by and is the sole property of Wizapply
*  All rights, title, ownership, or other interests in the software
*  remain the property of Wizapply.  This software may only be used
*  in accordance with the corresponding license agreement.
*  Any unauthorized use, duplication, transmission, distribution,
*  or disclosure of this software is expressly forbidden.
*
*  This Copyright notice may not be removed or modified without prior
*  written consent of Wizapply.
*
*  Wizpply reserves the right to modify this software without notice.
*  Unity : TM & Copyright Unity Technologies. All Rights Reserved
*
*  WIZAPPLY CO.,LTD.                       info@wizapply.com
*  5F, KS Building,                        https://wizapply.com
*  3-7-10 Ichiokamotomachi, Minato-ku,
*  Osaka, 552-0002, Japan
*
***************************************************************************/

#ifndef __WIZMO__
#define __WIZMO__

#include "wizmo_state.h"

namespace WIZMOSDK {

#ifndef __WIZMO_DATAPACKET__
#define __WIZMO_DATAPACKET__

const int WIZMODATA_AXIS_SIZE = 6;

//WIZMO Data packet（データパケット）
typedef struct _simvr_data_packet
{
	//軸オペレーション
	float axis[WIZMODATA_AXIS_SIZE];		//軸位置[配列]:0.0～1.0
	//軸速度・加速度オペレーション
	float speedAxis[WIZMODATA_AXIS_SIZE];	//軸速度[配列]:0.0～1.0
	float accelAxis;						//軸加速度レート:0.0～1.0
	//軸プロセッシング
	float roll;								//ロール:-1.0～1.0
	float pitch;							//ピッチ:-1.0～1.0
	float yaw;								//ヨー:-1.0～1.0
	float heave;							//ヒーブ:-1.0～1.0
	float sway;								//スウェイ:-1.0～1.0
	float surge;							//サージ:-1.0～1.0
	//レシオ
	float rotationMotionRatio;				//回転モーション比率:0.0～1.0
	float gravityMotionRatio;				//Gモーション比率:0.0～1.0
	//コマンド
	int commandSendCount;					//コマンド送信回数
	char command[256];						//コマンド送信文字列

} WIZMODataPacket;

#endif /*__WIZMO_DATAPACKET__*/

/////////// VARS AND DEFS ///////////

#ifdef WINDOWS
	#ifdef _WIZMO_EXPORTS
    #define WIZMOPORT __declspec(dllexport)
    #else
	#define WIZMOPORT __declspec(dllimport)
    #endif
#endif /*WINDOWS*/

#ifdef MACOSX
	#define WIZMOPORT 
#endif	/*MACOSX*/
	
#ifdef LINUX
	#define WIZMOPORT
#endif	/*LINUX*/

//バージョン
#define WIZMO_SDKVERSION "4.92"

//Default Packet
WIZMODataPacket WIZMOPORT DefaultWIZMOPacket();

struct Property;
class WIZMOPORT WIZMO
{
public:
	//コンストラクタ・デストラクタ
	WIZMO();
	~WIZMO();

	//メインメソッド
	//WIZMOをオープンし動作可能モード
	//@appCode = アプリコード
	//@assign = シリアル番号でデバイスを指定
	void Open(const char* appCode);
	void Open(const char* appCode, const char* assign);
	//WIZMOを閉じる
	void Close();
	//アクチュエータ制御にパケットの書き込み送信
	//@packet = パケット
	int Write(const WIZMODataPacket* packet);

	//コールバック関数メソッド
	//@func = 呼び出す関数
	void SetCallbackUpdateFunction(void(*func)());

	//プロパティ
	//乗降モード設定
	//@value = モードON or OFF
	void SetOriginMode(bool value);
	//現在の乗降モード取得
	bool GetOriginMode();
	//軸プロセスモード設定（姿勢計算モード）
	//@value = モードON or OFF
	void SetAxisProcessingMode(WIZMOAxisMode value);
	//現在の軸プロセスモードを取得
	WIZMOAxisMode GetAxisProcessingMode();

	//速度ゲインモード設定
	//@value = ゲインモード一覧(WIZMOSpeedGain)
	void SetSpeedGainMode(WIZMOSpeedGain value);
	//現在の速度ゲインモードを取得
	WIZMOSpeedGain GetSpeedGainMode();

	//現在接続されているアプリコードを取得
	const char* GetAppCode() const;
	//現在接続されているシリアル番号を取得
	const char* GetWIZMOSerialNumber() const;
	
	//デバイスの状態を取得
	State GetState();
	//ライブラリが動作中かどうか
	bool GetWIZMOStatus();
	//接続されているデバイスの種類を取得
	WIZMODevice GetWIZMODevice();
	//ライブラリのバージョンを取得
	const char* GetVersion() const;
	//デバイスが動作中かどうかを返す
	bool IsRunning() const;

	//外部データを取得
	int GetStatusEXT4() const;

private:
	void Update(WIZMODataPacket& packet);
	void ThreadUpdate();
	void CalcToAxisPacket(WIZMODataPacket& packet);
	void LogError();

	void LANStart();
	void LANStop();
	bool LANSelect(const char* deviceName, const char* serialNumber);
	void LANUpdate(WIZMODataPacket& packet);
	void LANUpdateKV(WIZMODataPacket& packet);

	struct Property* property;
};

}

#endif /*__WIZMO__*/
