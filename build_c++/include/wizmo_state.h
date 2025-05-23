/**************************************************************************
*
*              Copyright (c) 2014-2024 by Wizapply.
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
*  Wizapply                                info@wizapply.com
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
		CanNotFindUsb = 0,			//未接続
		CanNotFindWizmo,			//未接続
		CanNotCalibration,			//キャリブレーション起動失敗
		TimeoutCalibration,			//キャリブレーション中の失敗
		ShutDownActuator,			//アクチュエータ停止
		CanNotCertificate,			//認証失敗

		Initial,					//初期状態
		Running,					//動作中
		StopActuator,				//アクチュエータ一部停止
		CalibrationRetry,			//キャリブレーション再設定
	};

	//Deivce List
	enum class WIZMODevice {
		NONE = 0,
		SIMVR4DOF,
		SIMVR6DOF,
		SIMVR6DOF_MASSIVE,
		SIMVRDRIVEX,
		ANTSEAT,
		SIMVRMASSIVE_KV,
		SIMVR2DOF_KV,
	};

	//ゲインモード一覧
	enum class WIZMOSpeedGain {
		SPEEDGAIN_MODE_NORMAL = 0,	//ノーマル速度ゲイン（全軸固定速度設定）
		SPEEDGAIN_MODE_VARIABLE,	//可変速度ゲイン（追従速度モード）
		SPEEDGAIN_MODE_MANUAL,		//マニュアル速度ゲイン（軸別の速度設定）
	};

}
