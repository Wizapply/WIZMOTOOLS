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
#include <string>

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

namespace WIZMOSDK {
namespace Debug {

	const int WIZMOLOG_MAXCOUNT = 4096;	//4KB

	WIZMOPORT void Log(std::string message);
	WIZMOPORT void Log(float message);
	WIZMOPORT void Log(int message);
	WIZMOPORT void LogWarning(std::string message);
	WIZMOPORT void Log(std::string serial, std::string message);
	WIZMOPORT void LogWarning(std::string serial, std::string message);
	WIZMOPORT int GetBackLogData(char* buffer_p, int buffer_size);
	WIZMOPORT int GetBackLogDataAvailable();

}
}
