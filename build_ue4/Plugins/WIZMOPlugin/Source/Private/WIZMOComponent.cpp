// Fill out your copyright notice in the Description page of Project Settings.

#include "WIZMOComponent.h"
#include "WIZMOPluginPrivatePCH.h"

// Sets default values for this component's properties
UWIZMOComponent::UWIZMOComponent()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = true;

	Roll = 0.f;
	Pitch = 0.0f;
	Yaw = 0.0f;
	Heave = 0.0f;
	Sway = 0.0f;
	Surge = 0.0f;
	Speed = 1.0f;
	Acceleration = 0.5f;

	AxisProcessing = true;
	Axis1Value = 0.5f;
	Axis2Value = 0.5f;
	Axis3Value = 0.5f;
	Axis4Value = 0.5f;
	Axis5Value = 0.5f;
	Axis6Value = 0.5f;

	RotationMotionRatio = 0.8f;
	GravityMotionRatio = 0.8f;

	isOrigined = false;
	isOpened = false;
	automaticallyOpenAtStart = true;
}


// Called when the game starts
void UWIZMOComponent::BeginPlay()
{
	Super::BeginPlay();

	if(automaticallyOpenAtStart)
		OpenWIZMO();
}

void UWIZMOComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	Super::EndPlay(EndPlayReason);
	CloseWIZMO();
}

// Called every frame
void UWIZMOComponent::TickComponent( float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction )
{
	Super::TickComponent( DeltaTime, TickType, ThisTickFunction );

	if(!isOpened)
		return;

	WIZMOPacket p;
	p.roll = Roll;
	p.pitch = Pitch;
	p.yaw = Yaw;
	p.heave = Heave;
	p.sway = Sway;
	p.surge = Surge;
	p.speedAxis123 = Speed;
	p.accelAxis123 = Acceleration;
	p.speedAxis4 = Speed;		//This parameter is obsolete.
	p.accelAxis4 = Acceleration;	//This parameter is obsolete.

	if (!AxisProcessing) {
		p.axis1 = Axis1Value;
		p.axis2 = Axis2Value;
		p.axis3 = Axis3Value;
		p.axis4 = Axis4Value;
		p.axis5 = Axis5Value;
		p.axis6 = Axis6Value;
	}

	p.rotationMotionRatio = RotationMotionRatio;
	p.gravityMotionRatio = GravityMotionRatio;

	p.commandCount = 0;

	UpdateState();

	IWIZMOPlugin::Get().SetAxisProcesser(AxisProcessing);
	IWIZMOPlugin::Get().SetOrigin(isOrigined);
	IWIZMOPlugin::Get().UpdateWIZMO(&p);

	IWIZMOPlugin::Get().UpdateBackLog();
}

void UWIZMOComponent::UpdateState()
{
	int state = IWIZMOPlugin::Get().GetState();
	// Error if less than Initial
	if (state >= 0 && state <= Initial)
	{
		FString output = "";
		switch (state)
		{
		case Initial:
			output = "Initialize";
			break;
		case CanNotFindUsb:
			output = "MachineNotDetected";
			break;
		case CanNotFindSimvr:
			output = "InaccessibleToTheMachine";
			break;
		case CanNotCalibration:
			output = "ZeroReturnFailure";
			break;
		case TimeoutCalibration:
			output = "ErrorReturningToZero";
			break;
		case ShutDownActuator:
			output = "ShutDown";
			break;
		case CanNotCertificate:
			output = "AuthenticationFailure";
			break;
		case CalibrationRetry:
			output = "InternalDisconnectionError";
			break;
		}
		OnSystemEventCall.Broadcast(output);
		CloseWIZMO();
	}
	if (state == StopActuator)
	{
		if (!stopActuatorTrigger)
		{
			OnSystemEventCall.Broadcast("OverloadError");
			stopActuatorTrigger = true;
		}
	}
}

void UWIZMOComponent::OpenWIZMO()
{
	if(!isOpened) {
		IWIZMOPlugin::Get().Open(TCHAR_TO_UTF8(*AppCode));
		isOpened = true;
		stopActuatorTrigger = false;
	}
}

void UWIZMOComponent::CloseWIZMO()
{
	if(isOpened) {
		IWIZMOPlugin::Get().Close();
		IWIZMOPlugin::Get().UpdateBackLog();
		isOpened = false;
	}
}

int UWIZMOComponent::GetState()
{
	return IWIZMOPlugin::Get().GetState();
}