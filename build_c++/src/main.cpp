/**************************************************************************
*
*              Copyright (c) 2014-2016 by Wizapply.
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


/* -- Include files ----------------------------------------------------- */

#include <wizmo.h>	//WIZMO SDK
#include <wizmo_state.h>
#include <wizmo_log.h>

#include <string>
#include <iostream>
#include <thread>

/* -- Global variable definition ---------------------------------------- */

//Objects
WIZMOSDK::WIZMO* g_pWIZMOSystem = NULL;

/* -- Main -------------------------------------------------------------- */
WIZMOSDK::WIZMODataPacket DefaultPacket()
{
	WIZMOSDK::WIZMODataPacket packet = {};
	packet.axis1 = 0.5f;
	packet.axis2 = 0.5f;
	packet.axis3 = 0.5f;
	packet.axis4 = 0.5f;
	packet.axis5 = 0.5f;
	packet.axis6 = 0.5f;

	//Axis speed/accel controls
	packet.speedAxis = 0.8f;
	packet.accelAxis = 0.5f;
	packet.speedAxis4 = 0.8f;
	packet.accelAxis4 = 0.5f;

	//Axis Processing
	packet.roll = 0.0f;
	packet.pitch = 0.0f;
	packet.yaw = 0.0f;
	packet.heave = 0.0f;
	packet.sway = 0.0f;
	packet.surge = 0.0f;

	packet.rotationMotionRatio = 1.0f;
	packet.gravityMotionRatio = 0.0f;

	packet.commandCount = 0;

	return packet;
}

void simvrUpdateBackLog() {

	if (system == NULL)
		return;

	char logbuffer[WIZMOSDK::Debug::WIZMOLOG_MAXCOUNT];

	auto size = WIZMOSDK::Debug::GetBackLogDataAvailable();
	if (size > 0) {
		size = WIZMOSDK::Debug::GetBackLogData(logbuffer,size);
		std::string cp(logbuffer, size);

		std::cout << "----- WIZMO LOG -----\n" << cp << "---------------------\n";
	}
}

int main(int argc, char *argv[])
{
	g_pWIZMOSystem = new WIZMOSDK::WIZMO();
	g_pWIZMOSystem->Open("");

	std::cout << "WIZMO-START..." << std::endl;

	std::this_thread::sleep_for(std::chrono::seconds(5));

	simvrUpdateBackLog();

	g_pWIZMOSystem->SetOriginMode(false);
	g_pWIZMOSystem->SetAxisProcessingMode(true);	//Axis mode

	auto packet = DefaultPacket();

	std::cout << "This program can change ROLL, PITCH, YAW of the WIZMO. \nSpecification value [-1.0 to 1.0]. To exit, input [exit]." << std::endl;

	while (g_pWIZMOSystem->IsRunning())
	{
		std::string input;

		//ROLL
		std::cout << "ROLL -> ";
		std::cin >> input;
		if (input == "exit") break;

		auto d = static_cast<float>(atof(input.c_str()));
		packet.roll = d;

		//PITCH
		std::cout << "PITCH -> ";
		std::cin >> input;
		if (input == "exit") break;

		d = static_cast<float>(atof(input.c_str()));
		packet.pitch = d;

		//YAW
		std::cout << "YAW -> ";
		std::cin >> input;
		if (input == "exit") break;

		d = static_cast<float>(atof(input.c_str()));
		packet.yaw = d;

		g_pWIZMOSystem->SetOriginMode(false);
		g_pWIZMOSystem->Write(&packet);
		simvrUpdateBackLog();
	}

	delete g_pWIZMOSystem;

	simvrUpdateBackLog();

	std::this_thread::sleep_for(std::chrono::milliseconds(500));
	std::cout << "WIZMO-SHUTDOWN" << std::endl;

	return 0;
}
