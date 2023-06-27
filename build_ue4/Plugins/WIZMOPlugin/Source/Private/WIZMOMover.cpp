// Fill out your copyright notice in the Description page of Project Settings.

#include "WIZMOMover.h"
#include "WIZMOPluginPrivatePCH.h"

class WIZMOMover_Status6DOF
{
private:
	//Savitzky-Golay Smooth algorithm
	static const int SAVITZKY_GOLAY_SMOOTH_MAXCOUNT = 8;
	const float smoothPoint[SAVITZKY_GOLAY_SMOOTH_MAXCOUNT] = { 0.41667f,0.33333f,0.25f,0.16667f,0.08333f,0.0f,-0.08333f,-0.16667f };
	int smoothPointCurrent;

	TArray<float> s_smoothRoll;
	TArray<float> s_smoothPitch;
	TArray<float> s_smoothYaw;
	TArray<float> s_smoothHeave;
	TArray<float> s_smoothSway;
	TArray<float> s_smoothSurge;

public:
	WIZMOMover_Status6DOF()
	{
		s_smoothRoll.Init(0.0f, SAVITZKY_GOLAY_SMOOTH_MAXCOUNT);
		s_smoothPitch.Init(0.0f, SAVITZKY_GOLAY_SMOOTH_MAXCOUNT);
		s_smoothYaw.Init(0.0f, SAVITZKY_GOLAY_SMOOTH_MAXCOUNT);
		s_smoothHeave.Init(0.0f, SAVITZKY_GOLAY_SMOOTH_MAXCOUNT);
		s_smoothSway.Init(0.0f, SAVITZKY_GOLAY_SMOOTH_MAXCOUNT);
		s_smoothSurge.Init(0.0f, SAVITZKY_GOLAY_SMOOTH_MAXCOUNT);
		smoothPointCurrent = 0;
	}

	void StatusUpdate(float roll, float pitch, float yaw, float heave, float sway, float surge)
	{
		s_smoothRoll[smoothPointCurrent] = roll;
		s_smoothPitch[smoothPointCurrent] = pitch;
		s_smoothYaw[smoothPointCurrent] = yaw;
		s_smoothHeave[smoothPointCurrent] = heave;
		s_smoothSway[smoothPointCurrent] = sway;
		s_smoothSurge[smoothPointCurrent] = surge;

		++smoothPointCurrent;
		if (smoothPointCurrent >= SAVITZKY_GOLAY_SMOOTH_MAXCOUNT)
			smoothPointCurrent = 0;

	}

	float Roll()
	{
		float result = 0.0f;
		int index = smoothPointCurrent;
		for (int i = 0; i < SAVITZKY_GOLAY_SMOOTH_MAXCOUNT; ++i)
		{
			result += s_smoothRoll[index] * smoothPoint[i];
			++index;
			if (index >= SAVITZKY_GOLAY_SMOOTH_MAXCOUNT) index = 0;
		}

		return result;
	}
	float Pitch()
	{
		float result = 0.0f;
		int index = smoothPointCurrent;
		for (int i = 0; i < SAVITZKY_GOLAY_SMOOTH_MAXCOUNT; ++i)
		{
			result += s_smoothPitch[index] * smoothPoint[i];
			++index;
			if (index >= SAVITZKY_GOLAY_SMOOTH_MAXCOUNT) index = 0;
		}

		return result;
	}
	float Yaw()
	{
		float result = 0.0f;
		int index = smoothPointCurrent;
		for (int i = 0; i < SAVITZKY_GOLAY_SMOOTH_MAXCOUNT; ++i)
		{
			result += s_smoothYaw[index] * smoothPoint[i];
			++index;
			if (index >= SAVITZKY_GOLAY_SMOOTH_MAXCOUNT) index = 0;
		}

		return result;
	}
	float Heave()
	{
		float result = 0.0f;
		int index = smoothPointCurrent;
		for (int i = 0; i < SAVITZKY_GOLAY_SMOOTH_MAXCOUNT; ++i)
		{
			result += s_smoothHeave[index] * smoothPoint[i];
			++index;
			if (index >= SAVITZKY_GOLAY_SMOOTH_MAXCOUNT) index = 0;
		}

		return result;
	}
	float Sway()
	{
		float result = 0.0f;
		int index = smoothPointCurrent;
		for (int i = 0; i < SAVITZKY_GOLAY_SMOOTH_MAXCOUNT; ++i)
		{
			result += s_smoothSway[index] * smoothPoint[i];
			++index;
			if (index >= SAVITZKY_GOLAY_SMOOTH_MAXCOUNT) index = 0;
		}

		return result;
	}
	float Surge()
	{
		float result = 0.0f;
		int index = smoothPointCurrent;
		for (int i = 0; i < SAVITZKY_GOLAY_SMOOTH_MAXCOUNT; ++i)
		{
			result += s_smoothSurge[index] * smoothPoint[i];
			++index;
			if (index >= SAVITZKY_GOLAY_SMOOTH_MAXCOUNT) index = 0;
		}

		return result;
	}
};

// Sets default values for this component's properties
UWIZMOMover::UWIZMOMover()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PostUpdateWork;
	PrimaryComponentTick.TickInterval = 0.0f;

	Controller = nullptr;
	TrackingTarget = nullptr;

	Gcalc6Dof = new WIZMOMover_Status6DOF();
	Wscale = FVector(1.0f, 1.0f, 1.0f);
}


// Called when the game starts
void UWIZMOMover::BeginPlay()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	Super::BeginPlay();
	Controller = GetOwner()->FindComponentByClass<UWIZMOComponent>();

	previousPos = FVector(0.0f, 0.0f, 0.0f);
	previousYaw = 0.0f;
	previousVec = FVector(0.0f, 0.0f, 0.0f);

	if (Controller == nullptr) {
		UE_LOG(WIZMOLog, Warning, TEXT("%s"), L"There is no WIZMOComponent. Please add WIZMOComponent.");
		return;
	}
	if (TrackingTarget != nullptr) {
		previousPos = TrackingTarget->GetActorLocation();
		previousYaw = -TrackingTarget->GetActorRotation().Euler().Z;
		previousVec = FVector(0.0f, 0.0f, 0.0f);
		AddTickPrerequisiteActor(TrackingTarget);
	}else{
		UE_LOG(WIZMOLog, Warning, TEXT("%s"), L"TrackingTarget value is not specified.");

	}
}

void UWIZMOMover::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	Super::EndPlay(EndPlayReason);
}

// Called every frame
void UWIZMOMover::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	if (Controller == nullptr)
		return;

	Controller->Roll = 0.0f;
	Controller->Pitch = 0.0f;
	Controller->Yaw = 0.0f;
	Controller->Heave = 0.0f;
	Controller->Sway = 0.0f;
	Controller->Surge = 0.0f;

	if (TrackingTarget != nullptr)
	{
		AddTickPrerequisiteActor(TrackingTarget);

		FVector curPos = TrackingTarget->GetActorLocation();
		FVector vecPos = (curPos - previousPos) / DeltaTime;
		FVector vecChange = vecPos - previousVec;
		previousPos = curPos;
		previousVec = vecPos;

		vecChange /= Wscale;
		
		//G_calc
		FVector surge, sway, heave;
		surge.X = vecChange.X * TrackingTarget->GetActorForwardVector().X;
		surge.Y = vecChange.Y * TrackingTarget->GetActorForwardVector().Y;
		surge.Z = vecChange.Z * TrackingTarget->GetActorForwardVector().Z;
		sway.X = vecChange.X * TrackingTarget->GetActorRightVector().X;
		sway.Y = vecChange.Y * TrackingTarget->GetActorRightVector().Y;
		sway.Z = vecChange.Z * TrackingTarget->GetActorRightVector().Z;
		heave.X = vecChange.X * TrackingTarget->GetActorUpVector().X;
		heave.Y = vecChange.Y * TrackingTarget->GetActorUpVector().Y;
		heave.Z = vecChange.Z * TrackingTarget->GetActorUpVector().Z;

		//G
		float dataSurge = (surge.X + surge.Y + surge.Z);
		float dataSway = (sway.X + sway.Y + sway.Z);
		float dataHeave = (heave.X + heave.Y + heave.Z);

		//YAW_G calc
		float yaws = FMath::FindDeltaAngleDegrees(-TrackingTarget->GetActorRotation().Euler().Z, previousYaw);	//+-10“x = +-1.0
		previousYaw = -TrackingTarget->GetActorRotation().Euler().Z;

		//Roll, Pitch
		float rolls = FMath::FindDeltaAngleDegrees(-TrackingTarget->GetActorRotation().Euler().X, 0.0f) / 10.0f;	//+-10“x
		float pitchs = FMath::FindDeltaAngleDegrees(-TrackingTarget->GetActorRotation().Euler().Y, 0.0f) / 10.0f;	//+-10“x

		Gcalc6Dof->StatusUpdate(rolls, pitchs, yaws, dataHeave, dataSway, dataSurge);

		//Update
		Controller->Roll = ToRoundDown(rolls, 2);
		Controller->Pitch = ToRoundDown(pitchs, 2);
		Controller->Yaw = ToRoundDown(Gcalc6Dof->Yaw(),2);
		Controller->Heave = ToRoundDown(Gcalc6Dof->Heave(), 2);
		Controller->Sway = ToRoundDown(Gcalc6Dof->Sway(), 2);
		Controller->Surge = ToRoundDown(Gcalc6Dof->Surge(), 2);

		//UE_LOG(LogTemp, Log, TEXT("WIZMOMover Surge %f,%f"), Controller->Surge, dataSurge);
	}
	else
	{
		previousPos = FVector(0.0f, 0.0f, 0.0f);
		previousYaw = 0.0f;
		previousVec = FVector(0.0f, 0.0f, 0.0f);
	}

	//Force power
	Controller->Roll += RollForce;
	Controller->Pitch += PitchForce;
	Controller->Yaw += YawForce;
	Controller->Heave += HeaveForce;
	Controller->Sway += SwayForce;
	Controller->Surge += SurgeForce;
}

float UWIZMOMover::ToRoundDown(float dValue, int iDigits)
{
	float dCoef = FMath::Pow(10.0f, iDigits);

	return dValue > 0 ? FMath::FloorToFloat(dValue * dCoef) / dCoef :
		FMath::CeilToFloat(dValue * dCoef) / dCoef;
}