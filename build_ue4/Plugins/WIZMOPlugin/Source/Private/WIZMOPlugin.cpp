// Copyright 1998-2015 Epic Games, Inc. All Rights Reserved.


#include "WIZMOPluginPrivatePCH.h"
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdlib.h>	// for mbstowcs_s(), wcstombs_s()

DEFINE_LOG_CATEGORY(WIZMOLog);

//LoadLibrary
extern "C" {
	typedef int(*WIZMOOpen_ptr)(const char* serialNo);
	typedef int(*WIZMOClose_ptr)();
	typedef void(*WIZMOWrite_ptr)(WIZMOPacket* packet);

	typedef void(*WIZMOSetOriginMode_ptr)(bool value);
	typedef bool(*WIZMOGetOriginMode_ptr)();

	typedef void(*WIZMOSetAxisProcessingMode_ptr)(bool value);
	typedef bool(*WIZMOGetAxisProcessingMode_ptr)();

	typedef const char*(*WIZMOGetAppCode_ptr)();

	typedef int(*WIZMOGetState_ptr)();
	typedef const char*(*WIZMOGetVersion_ptr)();

	typedef int (*WIZMOGetBackLog_ptr)(char* str, int str_size);
	typedef int (*WIZMOBackLogDataAvailable_ptr)();

	typedef bool(*WIZMOIsRunning_ptr)();
}

class FWIZMOPlugin : public IWIZMOPlugin
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

	//Control
	virtual void Open(const char* serialId) override;
	virtual void Close() override;
	virtual void UpdateBackLog() override;
	virtual void UpdateWIZMO(WIZMOPacket* data) override;

	virtual void SetAxisProcesser(bool value) override;
	virtual void SetOrigin(bool value) override;
	virtual char* GetAppCode() override;
	virtual int GetState() override;

private:
	HINSTANCE hLibrary;

public:
	WIZMOOpen_ptr wizmoOpen;
	WIZMOClose_ptr wizmoClose;
	WIZMOWrite_ptr wizmoWrite;
	WIZMOSetOriginMode_ptr wizmoSetOrigin;
	WIZMOGetOriginMode_ptr wizmoGetOrigin;
	WIZMOSetAxisProcessingMode_ptr wizmoSetAxisProcessingMode;
	WIZMOGetAxisProcessingMode_ptr wizmoGetAxisProcessingMode;
	WIZMOGetAppCode_ptr wizmoGetAppCode;
	WIZMOGetState_ptr wizmoGetState;
	WIZMOGetVersion_ptr wizmoGetVersion;
	WIZMOGetBackLog_ptr wizmoGetBackLogData;
	WIZMOBackLogDataAvailable_ptr wizmoGetBackLogDataAvailable;
	WIZMOIsRunning_ptr wizmoIsRunning;

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
		wizmoOpen = reinterpret_cast<WIZMOOpen_ptr>(::GetProcAddress(hLibrary, "wizmoOpen"));
		wizmoClose = reinterpret_cast<WIZMOClose_ptr>(::GetProcAddress(hLibrary, "wizmoClose"));
		wizmoWrite = reinterpret_cast<WIZMOWrite_ptr>(::GetProcAddress(hLibrary, "wizmoWrite"));
		wizmoSetOrigin = reinterpret_cast<WIZMOSetOriginMode_ptr>(::GetProcAddress(hLibrary, "wizmoSetOriginMode"));
		wizmoGetOrigin = reinterpret_cast<WIZMOGetOriginMode_ptr>(::GetProcAddress(hLibrary, "wizmoGetOriginMode"));
		wizmoSetAxisProcessingMode = reinterpret_cast<WIZMOSetAxisProcessingMode_ptr>(::GetProcAddress(hLibrary, "wizmoSetAxisProcessingMode"));
		wizmoGetAxisProcessingMode = reinterpret_cast<WIZMOGetAxisProcessingMode_ptr>(::GetProcAddress(hLibrary, "wizmoGetAxisProcessingMode"));
		wizmoGetAppCode = reinterpret_cast<WIZMOGetAppCode_ptr>(::GetProcAddress(hLibrary, "wizmoGetAppCode"));
		wizmoGetState = reinterpret_cast<WIZMOGetState_ptr>(::GetProcAddress(hLibrary, "wizmoGetState"));
		wizmoGetVersion = reinterpret_cast<WIZMOGetVersion_ptr>(::GetProcAddress(hLibrary, "wizmoGetVersion"));
		wizmoGetBackLogData = reinterpret_cast<WIZMOGetBackLog_ptr>(::GetProcAddress(hLibrary, "wizmoGetBackLog"));
		wizmoGetBackLogDataAvailable = reinterpret_cast<WIZMOBackLogDataAvailable_ptr>(::GetProcAddress(hLibrary, "wizmoBackLogDataAvailable"));
		wizmoIsRunning = reinterpret_cast<WIZMOIsRunning_ptr>(::GetProcAddress(hLibrary, "wizmoIsRunning"));

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
		Close();
		FreeLibrary(hLibrary);
	}
}

void FWIZMOPlugin::Open(const char* serialId)
{
	if (!isDllLoaded)
		return;

	if (wizmoOpen(serialId) < 0) {
		UE_LOG(WIZMOLog, Log, TEXT("WIZMO Open Error. Check the code!"));
		return;
	}
}

void FWIZMOPlugin::Close()
{
	if (!isDllLoaded)
		return;

	wizmoClose();
}

void FWIZMOPlugin::UpdateBackLog()
{
	if (!isDllLoaded)
		return;

	const int BUFFERSIZE = 2048;
	char wizmoLogBuf[BUFFERSIZE];
	WCHAR wStrW[BUFFERSIZE];

	auto size = wizmoGetBackLogDataAvailable();
	if (size > 0) {
		size = wizmoGetBackLogData(wizmoLogBuf, size);
		if (size > 0) {
			size_t wLen = 0;
			mbstowcs_s(&wLen, wStrW, size, wizmoLogBuf, _TRUNCATE);
			UE_LOG(WIZMOLog, Log, TEXT("%s"), wStrW);
		}
	}
}

void FWIZMOPlugin::UpdateWIZMO(WIZMOPacket* data)
{
	if (!isDllLoaded)
		return;

	if (wizmoIsRunning() == false)
		return;

	wizmoWrite(data);
}

void FWIZMOPlugin::SetAxisProcesser(bool value) 
{
	if (!isDllLoaded)
		return;

	wizmoSetAxisProcessingMode(value);
}

void FWIZMOPlugin::SetOrigin(bool value)
{
	if (!isDllLoaded)
		return;

	wizmoSetOrigin(value);
}

char* FWIZMOPlugin::GetAppCode()
{
	if (!isDllLoaded)
		return NULL;

	return (char*)wizmoGetAppCode();
}

int FWIZMOPlugin::GetState()
{
	if (!isDllLoaded)
		return -1;

	return wizmoGetState();
}