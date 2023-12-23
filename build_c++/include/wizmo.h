/**************************************************************************
*
*              Copyright (c) 2014-2023 by Wizapply.
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

#ifndef __WIZMO__
#define __WIZMO__

namespace WIZMOSDK {

#ifndef __WIZMO_DATAPACKET__
#define __WIZMO_DATAPACKET__

const int WIZMODATA_AXIS_SIZE = 6;

//! WIZMO Data packet
typedef struct _simvr_data_packet
{
	//Axis position controls
	float axis[WIZMODATA_AXIS_SIZE];

	//Axis speed/accel controls
	float speedAxis[WIZMODATA_AXIS_SIZE];
	float accelAxis;

	//Axis Processing
	float roll;
	float pitch;
	float yaw;
	float heave;
	float sway;
	float surge;

	float rotationMotionRatio;
	float gravityMotionRatio;

	int commandSendCount;
	char command[256];

} WIZMODataPacket;

#endif /*__WIZMO_DATAPACKET__*/

/////////// VARS AND DEFS ///////////

#ifdef WIN32
	#ifdef _WIZMO_EXPORTS
    #define WIZMOPORT __declspec(dllexport)
    #else
	#define WIZMOPORT __declspec(dllimport)
    #endif
#endif /*WIN32*/

#ifdef MACOSX
	#define WIZMOPORT 
#endif	/*MACOSX*/
	
#ifdef LINUX
	#define WIZMOPORT
#endif	/*LINUX*/

//Default Packet
WIZMODataPacket WIZMOPORT DefaultWIZMOPacket();

#define WIZMO_SDKVERSION "4.62"

struct Property;

class WIZMOPORT WIZMO
{
public:
	//!Constructor
	WIZMO();
	//!Destructor
	~WIZMO();

	//Initialize
	/*!	@brief Open the WIZMO System
		@param appCode : Appication Code(Not a serial number)
		@param assign : Serial Number Code*/
	void Open(const char* appCode);
	void Open(const char* appCode, const char* assign);
	/*!	@brief Close the WIZMO System */
	void Close();

	//Write
	int Write(const WIZMODataPacket* packet);

	//Callback
	void SetCallbackUpdateFunction(void(*func)());

	//Properties
	void SetOriginMode(bool value);
	bool GetOriginMode();

	void SetAxisProcessingMode(bool value);
	bool GetAxisProcessingMode();

	static const int SPEEDGAIN_MODE_NORMAL = 0;
	static const int SPEEDGAIN_MODE_VARIABLE = 1;
	static const int SPEEDGAIN_MODE_MANUAL = 2;
	void SetSpeedGainMode(int speedGain_value);
	int GetSpeedGainMode();

	const char* GetAppCode() const;
	const char* GetWIZMOSerialNumber() const;

	int GetState();
	int GetWIZMODevice();
	const char* GetVersion() const;
	bool IsRunning() const;

	int GetStatusEXT4() const;

private:
	void Update(WIZMODataPacket& packet);
	void ThreadUpdate();
	void CalcToAxisPacket(WIZMODataPacket& packet);
	void LogError();

	void LANStart();
	void LANStop();
	void LANUpdate(WIZMODataPacket& packet);

	Property* property;
};

}

#endif
