// Copyright 1998-2015 Epic Games, Inc. All Rights Reserved.

#pragma once

#include "Modules/ModuleManager.h"
#include "Engine.h"

#include "CoreUObject.h"
#include "IWIZMOPlugin.generated.h"

DECLARE_LOG_CATEGORY_EXTERN(WIZMOLog, Log, All);

typedef int WIZMOHANDLE;
const int WIZMOHANDLE_ERROR = (-1);
const int WIZMODATA_AXIS_SIZE = 6;

//Struct
USTRUCT(BlueprintType)
struct FWIZMOPacket
{
	GENERATED_USTRUCT_BODY()
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
};

typedef struct FWIZMOPacket WIZMOPacket;

/**
 * The public interface to this module.  In most cases, this interface is only public to sibling modules
 * within this plugin.
 */
class IWIZMOPlugin : public IModuleInterface
{
public:
	static inline IWIZMOPlugin& Get() {
		return FModuleManager::LoadModuleChecked< IWIZMOPlugin >("WIZMOPlugin");
	}
	static inline bool IsAvailable() {
		return FModuleManager::Get().IsModuleLoaded("WIZMOPlugin");
	}

public:
	//Control
	virtual WIZMOHANDLE Open(const char* appCode, const char* serialAssign) = 0;
	virtual void Close(WIZMOHANDLE handle) = 0;

	virtual void UpdateBackLog() = 0;
	virtual void UpdateWIZMO(WIZMOHANDLE handle, WIZMOPacket* data) = 0;

	virtual void SetOriginMode(WIZMOHANDLE handle, bool value) = 0;
	virtual bool GetOriginMode(WIZMOHANDLE handle) = 0;
	virtual void SetAxisProcessingMode(WIZMOHANDLE handle, bool value) = 0;
	virtual bool GetAxisProcessingMode(WIZMOHANDLE handle) = 0;
	virtual void SetSpeedGainMode(WIZMOHANDLE handle, int value) = 0;
	virtual int GetSpeedGainMode(WIZMOHANDLE handle) = 0;

	virtual const char* GetAppCode(WIZMOHANDLE handle) = 0;
	virtual const char* GetWIZMOSerialNumber(WIZMOHANDLE handle) = 0;
	virtual const char* GetVersion(WIZMOHANDLE handle) = 0;
	virtual bool IsRunning(WIZMOHANDLE handle) = 0;
	virtual int GetState(WIZMOHANDLE handle) = 0;
	virtual int GetStatusEXT4(WIZMOHANDLE handle) = 0;
};