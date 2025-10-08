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
		CanNotFindUsb = 0,			//���ڑ�
		CanNotFindWizmo,			//���ڑ�
		CanNotCalibration,			//�L�����u���[�V�����N�����s
		TimeoutCalibration,			//�L�����u���[�V�������̎��s
		ShutDownActuator,			//�A�N�`���G�[�^��~
		CanNotCertificate,			//�F�؎��s

		Initial,					//�������
		Running,					//���쒆
		StopActuator,				//�A�N�`���G�[�^�ꕔ��~
		CalibrationRetry,			//�L�����u���[�V�����Đݒ�
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
		SIMVR2DOF,
	};

	//�Q�C�����[�h�ꗗ
	enum class WIZMOSpeedGain {
		SPEEDGAIN_MODE_NORMAL = 0,	//�m�[�}�����x�Q�C���i�S���Œ葬�x�ݒ�j
		SPEEDGAIN_MODE_VARIABLE,	//�ϑ��x�Q�C���i�Ǐ]���x���[�h�j
		SPEEDGAIN_MODE_MANUAL,		//�}�j���A�����x�Q�C���i���ʂ̑��x�ݒ�j
	};

}
