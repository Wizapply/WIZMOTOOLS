#pragma once

#include "Modules/ModuleManager.h"
#include "WIZMOPacket.generated.h"

const int WIZMODATA_AXIS_SIZE = 6;

USTRUCT(BlueprintType)
struct FWIZMOPacket
{
	GENERATED_USTRUCT_BODY()

	//Axis position controls
	float axis[6];

	//Axis speed/accel controls
	float speedAxis[6];
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