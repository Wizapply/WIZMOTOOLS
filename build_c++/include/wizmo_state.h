/**************************************************************************
*
*              Copyright (c) WIZAPPLY.
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

#pragma once

namespace WIZMOSDK {

	//State List
	enum class State
	{
		// エラー＆ストップ
		CanNotFindUsb = 0,			//未接続
		CanNotFindWizmo,			//未接続
		CanNotCalibration,			//キャリブレーション起動失敗
		TimeoutCalibration,			//キャリブレーション中の失敗
		ShutDownActuator,			//アクチュエータ停止
		CanNotCertificate,			//認証失敗
		// ランニング
		Initial,					//初期状態 通電中
		CalibrationRunning,			//キャリブレーション中
		Running,					//動作中
		// フォールトトレラント
		StopActuator,				//アクチュエータ一部停止
		CalibrationRetry,			//キャリブレーション再設定
	};

	//Deivce List
	enum class WIZMODevice {
		NONE = 0,
		SIMVR2DOF,
		SIMVR4DOF,
		SIMVR6DOF,
		ANTSEAT,
		SIMVRMASSIVE_KV,
		SIMVRMASSIVE500_KV,

		SIMVR_KDIVE2_OEM = 100,
		SIMVR_KICKBOARD_KV_OEM,
		SIMVR_E2M_EMU_OEM,
		SIMVR_DRIVEX_OEM,
		SIMVR_OSDX_OEM
	};

	//ゲインモード一覧
	enum class WIZMOSpeedGain {
		SPEEDGAIN_MODE_NORMAL = 0,	//ノーマル速度ゲイン（全軸固定速度設定）※デフォルト
		SPEEDGAIN_MODE_VARIABLE,	//可変速度ゲイン（追従速度モード）
		SPEEDGAIN_MODE_MANUAL,		//マニュアル速度ゲイン（軸別の速度設定）
	};

	//姿勢計算モード一覧(for MASSIVE)
	enum class WIZMOAxisMode {
		AXIS_MODE_MANUAL = 0,	//アクチュエータごとに設定（自作で計算する場合など）
		AXIS_MODE_GLOBALPOSE,	//グローバル座標での姿勢計算　※デフォルト
		AXIS_MODE_LOCALPOSE,	//ローカル座標での姿勢計算
	};
}
