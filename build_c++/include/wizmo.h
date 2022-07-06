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

#ifndef __WIZMO__
#define __WIZMO__

namespace WIZMOSDK {

#ifndef __WIZMO_DATAPACKET__
#define __WIZMO_DATAPACKET__

//! WIZMO Data packet
typedef struct _simvr_data_packet
{
	//Axis position controls
	float axis1;
	float axis2;
	float axis3;
	float axis4;
	float axis5;
	float axis6;

	//Axis speed/accel controls
	float speedAxis;
	float accelAxis;
	float speedAxis4;
	float accelAxis4;

	//Axis Processing
	float roll;
	float pitch;
	float yaw;
	float heave;
	float sway;
	float surge;

	float rotationMotionRatio;
	float gravityMotionRatio;

	int commandSendCount;	//送信するときは1を入れる
	int commandStride;		//使わない
	char command[256];

} WIZMODataPacket;

WIZMODataPacket DefaultWIZMOPacket();
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

struct Property;

#define WIZMO_SDKVERSION "4.1"

class WIZMOPORT WIZMO
{
public:
	//!Constructor
	WIZMO();
	//!Destructor
	~WIZMO();

	//Initialize
	/*!	@brief Open the WIZMO System
		@param appCode : Appication Code(Not a serial number)*/
	void Open(const char* appCode);
	void Open(const char* appCode, const char* assign);
	/*!	@brief Close the WIZMO System */
	void Close();

	//Write
	/*!	@brief This function sets data to WIZMO. 
		@param qt Set an image processing method. */
	int Write(const WIZMODataPacket* packet);

	//Callback
	/*!	@brief This function sets data to WIZMO.
		@param qt Set an image processing method. */
	void SetCallbackUpdateFunction(void(*func)());

	//Properties
	/*!	@brief This function sets data to WIZMO.
		@param qt Set an image processing method. */
	void SetOriginMode(bool value);
	bool GetOriginMode();

	void SetAxisProcessingMode(bool value);
	bool GetAxisProcessingMode();

	void SetVariableGainMode(bool value);
	bool GetVariableGainMode();

	const char* GetAppCode() const;
	const char* GetWIZMOSerialNumber() const;

	int GetState();
	const char* GetVersion() const;
	bool IsRunning() const;

	int GetStatusEXT4() const;

private:
	void Update(WIZMODataPacket& packet);
	void ThreadUpdate();
	void LogError();

	void LANStart();
	void LANStop();
	void LANUpdate(WIZMODataPacket& packet);

	Property* property;
};

}

#endif
