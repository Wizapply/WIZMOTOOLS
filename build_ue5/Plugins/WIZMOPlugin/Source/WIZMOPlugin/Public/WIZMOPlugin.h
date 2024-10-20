#pragma once

#include "Modules/ModuleManager.h"
#include "WIZMOPacket.h"

DECLARE_LOG_CATEGORY_EXTERN(WIZMOLog, Log, All);

typedef int WIZMOHANDLE;
const int WIZMOHANDLE_ERROR = (-1);

class FWIZMOPluginModule : public IModuleInterface
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

	static FWIZMOPluginModule& Get() {
		return FModuleManager::LoadModuleChecked<FWIZMOPluginModule>("WIZMOPlugin");
	}
	static bool IsAvailable() {
		return FModuleManager::Get().IsModuleLoaded("WIZMOPlugin");
	}

public:
	// Method
	WIZMOHANDLE Open(const char* appCode, const char* serialAssign);
	void Close(WIZMOHANDLE handle);

	void UpdateBackLog();
	void UpdateWIZMO(WIZMOHANDLE handle, WIZMOPacket* data);

	void SetOriginMode(WIZMOHANDLE handle, bool value);
	bool GetOriginMode(WIZMOHANDLE handle);
	void SetAxisProcessingMode(WIZMOHANDLE handle, bool value);
	bool GetAxisProcessingMode(WIZMOHANDLE handle);
	void SetSpeedGainMode(WIZMOHANDLE handle, int value);
	int GetSpeedGainMode(WIZMOHANDLE handle);

	const char* GetAppCode(WIZMOHANDLE handle);
	const char* GetWIZMOSerialNumber(WIZMOHANDLE handle);
	const char* GetVersion(WIZMOHANDLE handle);
	bool IsRunning(WIZMOHANDLE handle);
	int GetState(WIZMOHANDLE handle);
	int GetStatusEXT4(WIZMOHANDLE handle);
};
