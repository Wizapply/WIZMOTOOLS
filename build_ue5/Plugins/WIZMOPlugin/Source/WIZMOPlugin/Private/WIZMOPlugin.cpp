// Copyright Epic Games, Inc. All Rights Reserved.

#include "WIZMOPlugin.h"

#define LOCTEXT_NAMESPACE "FWIZMOPluginModule"
DEFINE_LOG_CATEGORY(WIZMOLog);

//--------------------------------

#define WIN32_LEAN_AND_MEAN
#include "Windows/WindowsSystemIncludes.h"
#include <windows.h>
#include <stdlib.h>	// for mbstowcs_s(), wcstombs_s()

//LoadLibrary
extern "C" {
	typedef WIZMOHANDLE(*wizmoOpen_ptr)(const char* appCode);
	typedef WIZMOHANDLE(*wizmoOpenSerialAssign_ptr)(const char* appCode, const char* assign);
	typedef WIZMOHANDLE(*wizmoClose_ptr)(WIZMOHANDLE handle);
	typedef void(*wizmoWrite_ptr)(WIZMOHANDLE handle, WIZMOPacket* packet);
	typedef void(*wizmoSetOriginMode_ptr)(WIZMOHANDLE handle, bool value);
	typedef bool(*wizmoGetOriginMode_ptr)(WIZMOHANDLE handle);
	typedef void(*wizmoSetAxisProcessingMode_ptr)(WIZMOHANDLE handle, bool value);
	typedef bool(*wizmoGetAxisProcessingMode_ptr)(WIZMOHANDLE handle);
	typedef void(*wizmoSetSpeedGainMode_ptr)(WIZMOHANDLE handle, int value);
	typedef int(*wizmoGetSpeedGainMode_ptr)(WIZMOHANDLE handle);
	typedef const char* (*wizmoGetAppCode_ptr)(WIZMOHANDLE handle);
	typedef const char* (*wizmoGetSerialNumber_ptr)(WIZMOHANDLE handle);
	typedef int(*wizmoGetState_ptr)(WIZMOHANDLE handle);
	typedef int(*wizmoGetStatusEXT4_ptr)(WIZMOHANDLE handle);
	typedef const char* (*wizmoGetVersion_ptr)(WIZMOHANDLE handle);
	typedef int (*wizmoGetBackLog_ptr)(char* buffer_p, int buffer_size);
	typedef int (*wizmoBackLogDataAvailable_ptr)();
	typedef bool(*wizmoIsRunning_ptr)(WIZMOHANDLE handle);
}

static wizmoOpen_ptr wizmoOpen;
static wizmoOpenSerialAssign_ptr wizmoOpenSerialAssign;
static wizmoClose_ptr wizmoClose;
static wizmoWrite_ptr wizmoWrite;
static wizmoSetOriginMode_ptr wizmoSetOriginMode;
static wizmoGetOriginMode_ptr wizmoGetOriginMode;
static wizmoSetAxisProcessingMode_ptr wizmoSetAxisProcessingMode;
static wizmoGetAxisProcessingMode_ptr wizmoGetAxisProcessingMode;
static wizmoSetSpeedGainMode_ptr wizmoSetSpeedGainMode;
static wizmoGetSpeedGainMode_ptr wizmoGetSpeedGainMode;
static wizmoGetAppCode_ptr wizmoGetAppCode;
static wizmoGetSerialNumber_ptr wizmoGetSerialNumber;
static wizmoGetState_ptr wizmoGetState;
static wizmoGetStatusEXT4_ptr wizmoGetStatusEXT4;
static wizmoGetVersion_ptr wizmoGetVersion;
static wizmoGetBackLog_ptr wizmoGetBackLog;
static wizmoBackLogDataAvailable_ptr wizmoBackLogDataAvailable;
static wizmoIsRunning_ptr wizmoIsRunning;

static HINSTANCE hLibrary = NULL;
static bool isDllLoaded = false;

//--------------------------------

void FWIZMOPluginModule::StartupModule()
{
	isDllLoaded = false;

	hLibrary = LoadLibrary(TEXT("wizmo.dll"));
	if (hLibrary != NULL)
	{
		wizmoOpen = reinterpret_cast<wizmoOpen_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoOpen")));
		wizmoOpenSerialAssign = reinterpret_cast<wizmoOpenSerialAssign_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoOpenSerialAssign")));
		wizmoClose = reinterpret_cast<wizmoClose_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoClose")));
		wizmoWrite = reinterpret_cast<wizmoWrite_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoWrite")));
		wizmoSetOriginMode = reinterpret_cast<wizmoSetOriginMode_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoSetOriginMode")));
		wizmoGetOriginMode = reinterpret_cast<wizmoGetOriginMode_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoGetOriginMode")));
		wizmoSetAxisProcessingMode = reinterpret_cast<wizmoSetAxisProcessingMode_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoSetAxisProcessingMode")));
		wizmoGetAxisProcessingMode = reinterpret_cast<wizmoGetAxisProcessingMode_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoGetAxisProcessingMode")));
		wizmoSetSpeedGainMode = reinterpret_cast<wizmoSetSpeedGainMode_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoSetSpeedGainMode")));
		wizmoGetSpeedGainMode = reinterpret_cast<wizmoGetSpeedGainMode_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoGetSpeedGainMode")));
		wizmoGetAppCode = reinterpret_cast<wizmoGetAppCode_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoGetAppCode")));
		wizmoGetState = reinterpret_cast<wizmoGetState_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoGetState")));
		wizmoGetSerialNumber = reinterpret_cast<wizmoGetSerialNumber_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoGetSerialNumber")));
		wizmoGetStatusEXT4 = reinterpret_cast<wizmoGetStatusEXT4_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoGetStatusEXT4")));
		wizmoGetVersion = reinterpret_cast<wizmoGetVersion_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoGetVersion")));
		wizmoGetBackLog = reinterpret_cast<wizmoGetBackLog_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoGetBackLog")));
		wizmoBackLogDataAvailable = reinterpret_cast<wizmoBackLogDataAvailable_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoBackLogDataAvailable")));
		wizmoIsRunning = reinterpret_cast<wizmoIsRunning_ptr>(reinterpret_cast<void*>(::GetProcAddress(hLibrary, "wizmoIsRunning")));

		isDllLoaded = true;
	}
	else
	{
		::MessageBox(NULL, TEXT("wizmo.dll file is not found! \'Binaries/Win64/wizmo.dll\'"), TEXT("wizmo.dll load error!"), MB_OK);
	}
}

void FWIZMOPluginModule::ShutdownModule()
{
	if (hLibrary != NULL) {
		FreeLibrary(hLibrary);
	}

	isDllLoaded = false;
}

WIZMOHANDLE FWIZMOPluginModule::Open(const char* appCode, const char* serialAssign)
{
	if (!isDllLoaded)
		return WIZMOHANDLE_ERROR;

	WIZMOHANDLE handle = wizmoOpenSerialAssign(appCode, serialAssign);
	if (handle < 0) {
		UE_LOG(WIZMOLog, Log, TEXT("WIZMO Open Error. Check the code!"));
		return WIZMOHANDLE_ERROR;
	}
	return handle;
}

void FWIZMOPluginModule::Close(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return;

	wizmoClose(handle);
}

void FWIZMOPluginModule::UpdateBackLog()
{
	if (!isDllLoaded)
		return;

	const int BUFFERSIZE = 2048;
	char wizmoLogBuf[BUFFERSIZE];
	WCHAR wStrW[BUFFERSIZE];

	auto size = wizmoBackLogDataAvailable();
	if (size > 0) {
		size = wizmoGetBackLog(wizmoLogBuf, size);
		if (size > 0) {
			size_t wLen = 0;
			mbstowcs_s(&wLen, wStrW, size, wizmoLogBuf, _TRUNCATE);
			UE_LOG(WIZMOLog, Log, TEXT("%s"), wStrW);
		}
	}
}

void FWIZMOPluginModule::UpdateWIZMO(WIZMOHANDLE handle, WIZMOPacket* data)
{
	if (!isDllLoaded)
		return;

	if (wizmoIsRunning(handle) == false)
		return;

	wizmoWrite(handle, data);
}

void FWIZMOPluginModule::SetOriginMode(WIZMOHANDLE handle, bool value)
{
	if (!isDllLoaded)
		return;
	wizmoSetOriginMode(handle, value);
}

bool FWIZMOPluginModule::GetOriginMode(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return false;
	return wizmoGetOriginMode(handle);
}

void FWIZMOPluginModule::SetAxisProcessingMode(WIZMOHANDLE handle, bool value)
{
	if (!isDllLoaded)
		return;
	wizmoSetAxisProcessingMode(handle, value);
}

bool FWIZMOPluginModule::GetAxisProcessingMode(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return false;
	return wizmoGetAxisProcessingMode(handle);
}

void FWIZMOPluginModule::SetSpeedGainMode(WIZMOHANDLE handle, int value)
{
	if (!isDllLoaded)
		return;
	wizmoSetSpeedGainMode(handle, value);
}

int FWIZMOPluginModule::GetSpeedGainMode(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return false;
	return wizmoGetSpeedGainMode(handle);
}


const char* FWIZMOPluginModule::GetAppCode(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return NULL;

	return wizmoGetAppCode(handle);
}

const char* FWIZMOPluginModule::GetWIZMOSerialNumber(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return NULL;

	return wizmoGetSerialNumber(handle);
}

const char* FWIZMOPluginModule::GetVersion(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return NULL;

	return wizmoGetVersion(handle);
}

bool FWIZMOPluginModule::IsRunning(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return false;

	return wizmoIsRunning(handle);
}

int FWIZMOPluginModule::GetState(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return WIZMOHANDLE_ERROR;

	return wizmoGetState(handle);
}

int FWIZMOPluginModule::GetStatusEXT4(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return WIZMOHANDLE_ERROR;

	return wizmoGetStatusEXT4(handle);
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FWIZMOPluginModule, WIZMOPlugin)