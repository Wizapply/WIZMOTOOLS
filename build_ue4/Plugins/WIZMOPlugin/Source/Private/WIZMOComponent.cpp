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
	SpeedGainMode = EWIZMOSpeedGain::Normal;
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
	wizmoHandle = WIZMOHANDLE_ERROR;
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

	p.speed1_all= Speed;
	p.speed2 = Speed;
	p.speed3 = Speed;
	p.speed4 = Speed;
	p.speed5 = Speed;
	p.speed6 = Speed;
	p.accel = Acceleration;

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
	p.commandSendCount = 0;

	UpdateState();

	IWIZMOPlugin::Get().SetAxisProcessingMode(wizmoHandle, AxisProcessing);
	IWIZMOPlugin::Get().SetOriginMode(wizmoHandle, isOrigined);
	IWIZMOPlugin::Get().SetSpeedGainMode(wizmoHandle, (int)SpeedGainMode);
	IWIZMOPlugin::Get().UpdateWIZMO(wizmoHandle, &p);

	IWIZMOPlugin::Get().UpdateBackLog();
}

void UWIZMOComponent::UpdateState()
{
	EWIZMOState state = (EWIZMOState)IWIZMOPlugin::Get().GetState(wizmoHandle);
	// Error if less than Initial
	if (state >= EWIZMOState::CanNotFindUsb && state <= EWIZMOState::Initial)
	{
		FString output = "";
		switch (state)
		{
		case EWIZMOState::Initial:
			output = "Initialize";
			break;
		case EWIZMOState::CanNotFindUsb:
			output = "MachineNotDetected";
			break;
		case EWIZMOState::CanNotFindSimvr:
			output = "InaccessibleToTheMachine";
			break;
		case EWIZMOState::CanNotCalibration:
			output = "ZeroReturnFailure";
			break;
		case EWIZMOState::TimeoutCalibration:
			output = "ErrorReturningToZero";
			break;
		case EWIZMOState::ShutDownActuator:
			output = "ShutDown";
			break;
		case EWIZMOState::CanNotCertificate:
			output = "AuthenticationFailure";
			break;
		case EWIZMOState::CalibrationRetry:
			output = "InternalDisconnectionError";
			break;
		}
		OnSystemEventCall.Broadcast(output);
		CloseWIZMO();
	}
	if (state == EWIZMOState::StopActuator)
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
	if (isOpened)
		return;

	wizmoHandle = IWIZMOPlugin::Get().Open(TCHAR_TO_UTF8(*AppCode), TCHAR_TO_UTF8(*AssignNo));
	if(wizmoHandle >= 0) {
		isOpened = true;
		stopActuatorTrigger = false;

		IWIZMOPlugin::Get().SetAxisProcessingMode(wizmoHandle, AxisProcessing);
		IWIZMOPlugin::Get().SetOriginMode(wizmoHandle, isOrigined);
		IWIZMOPlugin::Get().SetSpeedGainMode(wizmoHandle, (int)SpeedGainMode);
	}
}

void UWIZMOComponent::CloseWIZMO()
{
	if(isOpened) {
		IWIZMOPlugin::Get().Close(wizmoHandle);
		IWIZMOPlugin::Get().UpdateBackLog();
		isOpened = false;
	}
}

EWIZMOState UWIZMOComponent::GetState()
{
	return (EWIZMOState)IWIZMOPlugin::Get().GetState(wizmoHandle);
}

bool UWIZMOComponent::IsRunning()
{
	return IWIZMOPlugin::Get().IsRunning(wizmoHandle);
}