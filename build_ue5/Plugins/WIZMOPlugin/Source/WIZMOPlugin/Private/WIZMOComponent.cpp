#include "WIZMOComponent.h"

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
	Speed = 0.667f;
	Acceleration = 0.5f;

	Speed2 = Speed;
	Speed3 = Speed;
	Speed4 = Speed;
	Speed5 = Speed;
	Speed6 = Speed;

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
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	if (!isOpened)
		return;

	WIZMOPacket p;
	p.roll = Roll;
	p.pitch = Pitch;
	p.yaw = Yaw;
	p.heave = Heave;
	p.sway = Sway;
	p.surge = Surge;

	p.speedAxis[0] = Speed;
	p.speedAxis[1] = Speed2;
	p.speedAxis[2] = Speed3;
	p.speedAxis[3] = Speed4;
	p.speedAxis[4] = Speed5;
	p.speedAxis[5] = Speed6;
	p.accelAxis = Acceleration;

	if (!AxisProcessing) {
		p.axis[0] = Axis1Value;
		p.axis[1] = Axis2Value;
		p.axis[2] = Axis3Value;
		p.axis[3] = Axis4Value;
		p.axis[4] = Axis5Value;
		p.axis[5] = Axis6Value;
	}

	p.rotationMotionRatio = RotationMotionRatio;
	p.gravityMotionRatio = GravityMotionRatio;
	p.commandSendCount = 0;

	UpdateState();

	wizmoPlugin->SetAxisProcessingMode(wizmoHandle, AxisProcessing);
	wizmoPlugin->SetOriginMode(wizmoHandle, isOrigined);
	wizmoPlugin->SetSpeedGainMode(wizmoHandle, (int)SpeedGainMode);
	wizmoPlugin->UpdateWIZMO(wizmoHandle, &p);

	wizmoPlugin->UpdateBackLog();
}

void UWIZMOComponent::UpdateState()
{
	int state_int = wizmoPlugin->GetState(wizmoHandle);

	//UE_LOG(WIZMOLog, Log, TEXT("state_int=%d"), state_int);
	if (state_int < 0)
		return;

	// Error if less than Initial
	EWIZMOState state = (EWIZMOState)state_int;
	if (!IsRunning())
	{
		FString output = "";
		switch (state)
		{
		case EWIZMOState::Initial:
			output = "Initialize";
			break;
		case EWIZMOState::CanNotFindUsb:
			output = "MachineNotDetected";
			CloseWIZMO();
			break;
		case EWIZMOState::CanNotFindSimvr:
			output = "InaccessibleToTheMachine";
			CloseWIZMO();
			break;
		case EWIZMOState::CanNotCalibration:
			output = "ZeroReturnFailure";
			CloseWIZMO();
			break;
		case EWIZMOState::TimeoutCalibration:
			output = "ErrorReturningToZero";
			CloseWIZMO();
			break;
		case EWIZMOState::ShutDownActuator:
			output = "ShutDown";
			CloseWIZMO();
			break;
		case EWIZMOState::CanNotCertificate:
			output = "AuthenticationFailure";
			CloseWIZMO();
			break;
		case EWIZMOState::CalibrationRetry:
			output = "InternalDisconnectionError";
			CloseWIZMO();
			break;
		}
		OnSystemEventCall.Broadcast(output);
	}

	//fail soft design
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

	wizmoHandle = wizmoPlugin->Open(TCHAR_TO_UTF8(*AppCode), TCHAR_TO_UTF8(*AssignNo));
	if (wizmoHandle >= 0) {
		isOpened = true;
		stopActuatorTrigger = false;

		wizmoPlugin->SetAxisProcessingMode(wizmoHandle, AxisProcessing);
		wizmoPlugin->SetOriginMode(wizmoHandle, isOrigined);
		wizmoPlugin->SetSpeedGainMode(wizmoHandle, (int)SpeedGainMode);
	}
}

void UWIZMOComponent::CloseWIZMO()
{
	if (isOpened) {
		wizmoPlugin->Close(wizmoHandle);
		wizmoPlugin->UpdateBackLog();
		isOpened = false;
		stopActuatorTrigger = false;
	}
}

EWIZMOState UWIZMOComponent::GetState()
{
	return (EWIZMOState)wizmoPlugin->GetState(wizmoHandle);
}

bool UWIZMOComponent::IsRunning()
{
	return wizmoPlugin->IsRunning(wizmoHandle);
}

FString UWIZMOComponent::SerialNumber()
{
	return wizmoPlugin->GetWIZMOSerialNumber(wizmoHandle);
}