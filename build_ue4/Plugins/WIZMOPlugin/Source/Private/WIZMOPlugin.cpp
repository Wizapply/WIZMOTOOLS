// Copyright 1998-2015 Epic Games, Inc. All Rights Reserved.


#include "WIZMOPluginPrivatePCH.h"
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdlib.h>	// for mbstowcs_s(), wcstombs_s()

DEFINE_LOG_CATEGORY(WIZMOLog);

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
	typedef void(*wizmoSetVariableGainMode_ptr)(WIZMOHANDLE handle, bool value);
	typedef bool(*wizmoGetVariableGainMode_ptr)(WIZMOHANDLE handle);
	typedef const char*(*wizmoGetAppCode_ptr)(WIZMOHANDLE handle);
	typedef const char*(*wizmoGetSerialNumber_ptr)(WIZMOHANDLE handle);
	typedef int(*wizmoGetState_ptr)(WIZMOHANDLE handle);
	typedef int(*wizmoGetStatusEXT4_ptr)(WIZMOHANDLE handle);
	typedef const char*(*wizmoGetVersion_ptr)(WIZMOHANDLE handle);
	typedef int (*wizmoGetBackLog_ptr)(char* buffer_p, int buffer_size);
	typedef int (*wizmoBackLogDataAvailable_ptr)();
	typedef bool(*wizmoIsRunning_ptr)(WIZMOHANDLE handle);
}

class FWIZMOPlugin : public IWIZMOPlugin
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

	//Control
	virtual WIZMOHANDLE Open(const char* appCode, const char* serialAssign) override;
	virtual void Close(WIZMOHANDLE handle) override;

	virtual void UpdateBackLog() override;
	virtual void UpdateWIZMO(WIZMOHANDLE handle, WIZMOPacket* data) override;
	
	virtual void SetOriginMode(WIZMOHANDLE handle, bool value) override;
	virtual bool GetOriginMode(WIZMOHANDLE handle) override;
	virtual void SetAxisProcessingMode(WIZMOHANDLE handle, bool value) override;
	virtual bool GetAxisProcessingMode(WIZMOHANDLE handle) override;
	virtual void SetVariableGainMode(WIZMOHANDLE handle, bool value) override;
	virtual bool GetVariableGainMode(WIZMOHANDLE handle) override;
	
	virtual const char* GetAppCode(WIZMOHANDLE handle) override;
	virtual const char* GetWIZMOSerialNumber(WIZMOHANDLE handle) override;
	virtual const char* GetVersion(WIZMOHANDLE handle) override;
	virtual bool IsRunning(WIZMOHANDLE handle) override;
	virtual int GetState(WIZMOHANDLE handle) override;
	virtual int GetStatusEXT4(WIZMOHANDLE handle) override;

private:
	HINSTANCE hLibrary;

public:
	wizmoOpen_ptr wizmoOpen;
	wizmoOpenSerialAssign_ptr wizmoOpenSerialAssign;
	wizmoClose_ptr wizmoClose;
	wizmoWrite_ptr wizmoWrite;
	wizmoSetOriginMode_ptr wizmoSetOriginMode;
	wizmoGetOriginMode_ptr wizmoGetOriginMode;
	wizmoSetAxisProcessingMode_ptr wizmoSetAxisProcessingMode;
	wizmoGetAxisProcessingMode_ptr wizmoGetAxisProcessingMode;
	wizmoSetVariableGainMode_ptr wizmoSetVariableGainMode;
	wizmoGetVariableGainMode_ptr wizmoGetVariableGainMode;
	wizmoGetAppCode_ptr wizmoGetAppCode;
	wizmoGetSerialNumber_ptr wizmoGetSerialNumber;
	wizmoGetState_ptr wizmoGetState;
	wizmoGetStatusEXT4_ptr wizmoGetStatusEXT4;
	wizmoGetVersion_ptr wizmoGetVersion;
	wizmoGetBackLog_ptr wizmoGetBackLog;
	wizmoBackLogDataAvailable_ptr wizmoBackLogDataAvailable;
	wizmoIsRunning_ptr wizmoIsRunning;

	bool isDllLoaded;
	bool isOpen;
	bool endWIZMO;
};

IMPLEMENT_MODULE(FWIZMOPlugin, WIZMOPlugin)


void FWIZMOPlugin::StartupModule()
{
	isDllLoaded = false;
	isOpen = false;

	hLibrary = LoadLibrary(TEXT("wizmo.dll"));
	if (hLibrary != NULL)
	{
		wizmoOpen = reinterpret_cast<wizmoOpen_ptr>(::GetProcAddress(hLibrary, "wizmoOpen"));
		wizmoOpenSerialAssign = reinterpret_cast<wizmoOpenSerialAssign_ptr>(::GetProcAddress(hLibrary, "wizmoOpenSerialAssign"));
		wizmoClose = reinterpret_cast<wizmoClose_ptr>(::GetProcAddress(hLibrary, "wizmoClose"));
		wizmoWrite = reinterpret_cast<wizmoWrite_ptr>(::GetProcAddress(hLibrary, "wizmoWrite"));
		wizmoSetOriginMode = reinterpret_cast<wizmoSetOriginMode_ptr>(::GetProcAddress(hLibrary, "wizmoSetOriginMode"));
		wizmoGetOriginMode = reinterpret_cast<wizmoGetOriginMode_ptr>(::GetProcAddress(hLibrary, "wizmoGetOriginMode"));
		wizmoSetAxisProcessingMode = reinterpret_cast<wizmoSetAxisProcessingMode_ptr>(::GetProcAddress(hLibrary, "wizmoSetAxisProcessingMode"));
		wizmoGetAxisProcessingMode = reinterpret_cast<wizmoGetAxisProcessingMode_ptr>(::GetProcAddress(hLibrary, "wizmoGetAxisProcessingMode"));
		wizmoSetVariableGainMode = reinterpret_cast<wizmoSetVariableGainMode_ptr>(::GetProcAddress(hLibrary, "wizmoSetVariableGainMode"));
		wizmoGetVariableGainMode = reinterpret_cast<wizmoGetVariableGainMode_ptr>(::GetProcAddress(hLibrary, "wizmoGetVariableGainMode"));
		wizmoGetAppCode = reinterpret_cast<wizmoGetAppCode_ptr>(::GetProcAddress(hLibrary, "wizmoGetAppCode"));
		wizmoGetState = reinterpret_cast<wizmoGetState_ptr>(::GetProcAddress(hLibrary, "wizmoGetState"));
		wizmoGetSerialNumber = reinterpret_cast<wizmoGetSerialNumber_ptr>(::GetProcAddress(hLibrary, "wizmoGetSerialNumber"));
		wizmoGetStatusEXT4 = reinterpret_cast<wizmoGetStatusEXT4_ptr>(::GetProcAddress(hLibrary, "wizmoGetStatusEXT4"));
		wizmoGetVersion = reinterpret_cast<wizmoGetVersion_ptr>(::GetProcAddress(hLibrary, "wizmoGetVersion"));
		wizmoGetBackLog = reinterpret_cast<wizmoGetBackLog_ptr>(::GetProcAddress(hLibrary, "wizmoGetBackLog"));
		wizmoBackLogDataAvailable = reinterpret_cast<wizmoBackLogDataAvailable_ptr>(::GetProcAddress(hLibrary, "wizmoBackLogDataAvailable"));
		wizmoIsRunning = reinterpret_cast<wizmoIsRunning_ptr>(::GetProcAddress(hLibrary, "wizmoIsRunning"));

		isDllLoaded = true;
	}
	else
	{
		::MessageBox(NULL, TEXT("wizmo.dll file is not found! \'Binaries/Win64/wizmo.dll\'"), TEXT("wizmo.dll load error!"), MB_OK);
	}
}

void FWIZMOPlugin::ShutdownModule()
{
	if (hLibrary != NULL) {
		FreeLibrary(hLibrary);
	}
}

WIZMOHANDLE FWIZMOPlugin::Open(const char* appCode, const char* serialAssign)
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

void FWIZMOPlugin::Close(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return;

	wizmoClose(handle);
}

void FWIZMOPlugin::UpdateBackLog()
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

void FWIZMOPlugin::UpdateWIZMO(WIZMOHANDLE handle, WIZMOPacket* data)
{
	if (!isDllLoaded)
		return;

	if (wizmoIsRunning(handle) == false)
		return;

	wizmoWrite(handle, data);
}

void FWIZMOPlugin::SetOriginMode(WIZMOHANDLE handle, bool value)
{
	if (!isDllLoaded)
		return;
	wizmoSetOriginMode(handle, value);
}

bool FWIZMOPlugin::GetOriginMode(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return false;
	return wizmoGetOriginMode(handle);
}

void FWIZMOPlugin::SetAxisProcessingMode(WIZMOHANDLE handle, bool value) 
{
	if (!isDllLoaded)
		return;
	wizmoSetAxisProcessingMode(handle, value);
}

bool FWIZMOPlugin::GetAxisProcessingMode(WIZMOHANDLE handle) 
{
	if (!isDllLoaded)
		return false;
	return wizmoGetAxisProcessingMode(handle);
}

void FWIZMOPlugin::SetVariableGainMode(WIZMOHANDLE handle, bool value) 
{
	if (!isDllLoaded)
		return;
	wizmoSetVariableGainMode(handle, value);
}

bool FWIZMOPlugin::GetVariableGainMode(WIZMOHANDLE handle) 
{
	if (!isDllLoaded)
		return false;
	return wizmoGetVariableGainMode(handle);
}


const char* FWIZMOPlugin::GetAppCode(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return NULL;

	return wizmoGetAppCode(handle);
}

const char* FWIZMOPlugin::GetWIZMOSerialNumber(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return NULL;

	return wizmoGetSerialNumber(handle);
}

const char* FWIZMOPlugin::GetVersion(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return NULL;

	return wizmoGetVersion(handle);
}

bool FWIZMOPlugin::IsRunning(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return false;

	return wizmoIsRunning(handle);
}

int FWIZMOPlugin::GetState(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return WIZMOHANDLE_ERROR;

	return wizmoGetState(handle);
}

int FWIZMOPlugin::GetStatusEXT4(WIZMOHANDLE handle)
{
	if (!isDllLoaded)
		return WIZMOHANDLE_ERROR;

	return wizmoGetStatusEXT4(handle);
}
