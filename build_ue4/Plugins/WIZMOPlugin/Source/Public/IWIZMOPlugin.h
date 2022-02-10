// Copyright 1998-2015 Epic Games, Inc. All Rights Reserved.

#pragma once

#include "Modules/ModuleManager.h"
#include "Engine.h"

#include "CoreUObject.h"
#include "IWIZMOPlugin.generated.h"

DECLARE_LOG_CATEGORY_EXTERN(WIZMOLog, Log, All);

//Struct
USTRUCT(BlueprintType)
struct FWIZMOPacket
{
	GENERATED_USTRUCT_BODY()

	//Axis position controls
	float axis1;
	float axis2;
	float axis3;
	float axis4;
	float axis5;
	float axis6;

	//Axis speed/accel controls
	float speedAxis123;
	float accelAxis123;
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

	int commandCount;
	int commandStride;
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
	static inline IWIZMOPlugin& Get(){
		return FModuleManager::LoadModuleChecked< IWIZMOPlugin >( "WIZMOPlugin" );
	}
	static inline bool IsAvailable() {
		return FModuleManager::Get().IsModuleLoaded( "WIZMOPlugin" );
	}

public:
	//Control
	virtual void Open(const char* serialId) = 0;
	virtual void Close() = 0;
	virtual void UpdateBackLog() = 0;
	virtual void UpdateWIZMO(WIZMOPacket* data) = 0;

	virtual void SetAxisProcesser(bool value) = 0;
	virtual void SetOrigin(bool value) = 0;
	virtual char* GetAppCode() = 0;
	virtual int GetState() = 0;
};
