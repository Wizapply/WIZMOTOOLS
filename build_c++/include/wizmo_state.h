/**************************************************************************
*
*              Copyright (c) 2014-2017 by Wizapply.
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
*  5F, KS Building,                        http://wizapply.com
*  3-7-10 Ichiokamotomachi, Minato-ku,
*  Osaka, 552-0002, Japan
*
***************************************************************************/

#pragma once

namespace WIZMOSDK {

	//State List
	enum class State
	{
		CanNotFindUsb = 0,
		CanNotFindWizmo,
		CanNotCalibration,
		TimeoutCalibration,
		ShutDownActuator,
		CanNotCertificate,

		Initial,
		Running,
		StopActuator,
		CalibrationRetry,
	};

	//Deivce List
	enum class WIZMODevice {
		NONE = 0,
		SIMVR4DOF,
		SIMVR6DOF,
		SIMVR6DOF_MASSIVE,
		ANTSEAT,
	};

}
