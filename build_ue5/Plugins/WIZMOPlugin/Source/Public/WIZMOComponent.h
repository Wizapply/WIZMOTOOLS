// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "Components/ActorComponent.h"
#include "WIZMOComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FWizmoSystemOnEvent, FString, message);

//plugin State Define
UENUM()
enum class EWIZMOState : int32
{
	CanNotFindUsb = 0,
	CanNotFindSimvr = 1,
	CanNotCalibration = 2,
	TimeoutCalibration = 3,
	ShutDownActuator = 4,
	CanNotCertificate = 5,
	Initial = 6,
	Running = 7,
	StopActuator = 8,
	CalibrationRetry = 9
};

//plugin SpeedGain Define
UENUM(BlueprintType)
enum class EWIZMOSpeedGain : uint8
{
	Normal = 0 UMETA(DisplayName = "Normal"),
	Variable UMETA(DisplayName = "Variable"),
	Manual UMETA(DisplayName = "Manual"),
};

typedef int WIZMOHANDLE;
#define WIZMOHANDLE_ERROR (-1)

UCLASS( ClassGroup=(WIZMO), meta=(BlueprintSpawnableComponent) )
class UWIZMOComponent : public UActorComponent
{
	GENERATED_BODY()

	WIZMOHANDLE wizmoHandle;
	bool stopActuatorTrigger;
	void UpdateState();

public:
	// Sets default values for this component's properties
	UWIZMOComponent();

	// Called when the game starts
	virtual void BeginPlay() override;
	// Called when the game ends
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	// Called every frame
	virtual void TickComponent( float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction ) override;

	//Status
	UPROPERTY(BlueprintReadOnly, Category = "Status", VisibleAnywhere)
		bool isOpened;

	UPROPERTY(BlueprintReadWrite, Category = "Status", EditAnywhere)
		bool automaticallyOpenAtStart;

	//AppCode
	UPROPERTY(BlueprintReadWrite, Category = "Application Codes", EditAnywhere)
		FString AppCode;
	//AppCode
	UPROPERTY(BlueprintReadWrite, Category = "Application Codes", EditAnywhere)
		FString AssignNo;

	//Status
	UPROPERTY(BlueprintReadWrite, Category = "Options", EditAnywhere)
		bool AxisProcessing;
	UPROPERTY(BlueprintReadWrite, Category = "Options", EditAnywhere)
		EWIZMOSpeedGain SpeedGainMode;

	//Rotation
	UPROPERTY(BlueprintReadWrite, Category = "Rotation and G", EditAnywhere, meta = (ClampMin = "-1.0", ClampMax = "1.0", UIMin = "-1.0", UIMax = "1.0", EditCondition="AxisProcessing"))
		float Roll;
	UPROPERTY(BlueprintReadWrite, Category = "Rotation and G", EditAnywhere, meta = (ClampMin = "-1.0", ClampMax = "1.0", UIMin = "-1.0", UIMax = "1.0", EditCondition="AxisProcessing"))
		float Pitch;
	UPROPERTY(BlueprintReadWrite, Category = "Rotation and G", EditAnywhere, meta = (ClampMin = "-1.0", ClampMax = "1.0", UIMin = "-1.0", UIMax = "1.0", EditCondition="AxisProcessing"))
		float Yaw;
	//G
	UPROPERTY(BlueprintReadWrite, Category = "Rotation and G", EditAnywhere, meta = (ClampMin = "-1.0", ClampMax = "1.0", UIMin = "-1.0", UIMax = "1.0", EditCondition="AxisProcessing"))
		float Heave;
	UPROPERTY(BlueprintReadWrite, Category = "Rotation and G", EditAnywhere, meta = (ClampMin = "-1.0", ClampMax = "1.0", UIMin = "-1.0", UIMax = "1.0", EditCondition="AxisProcessing"))
		float Sway;
	UPROPERTY(BlueprintReadWrite, Category = "Rotation and G", EditAnywhere, meta = (ClampMin = "-1.0", ClampMax = "1.0", UIMin = "-1.0", UIMax = "1.0", EditCondition="AxisProcessing"))
		float Surge;
	//Axis
	UPROPERTY(BlueprintReadWrite, Category = "Direct", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "!AxisProcessing"))
		float Axis1Value;
	UPROPERTY(BlueprintReadWrite, Category = "Direct", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "!AxisProcessing"))
		float Axis2Value;
	UPROPERTY(BlueprintReadWrite, Category = "Direct", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "!AxisProcessing"))
		float Axis3Value;
	UPROPERTY(BlueprintReadWrite, Category = "Direct", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "!AxisProcessing"))
		float Axis4Value;
	UPROPERTY(BlueprintReadWrite, Category = "Direct", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "!AxisProcessing"))
		float Axis5Value;
	UPROPERTY(BlueprintReadWrite, Category = "Direct", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "!AxisProcessing"))
		float Axis6Value;

	//Configures
	UPROPERTY(BlueprintReadWrite, Category = "Configures", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "SpeedGainMode == EWIZMOSpeedGain::Normal"))
	float Acceleration;
	UPROPERTY(BlueprintReadWrite, Category = "Configures", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "SpeedGainMode != EWIZMOSpeedGain::Variable"))
	float Speed;
	UPROPERTY(BlueprintReadWrite, Category = "Configures", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "SpeedGainMode == EWIZMOSpeedGain::Manual"))
	float Speed2;
	UPROPERTY(BlueprintReadWrite, Category = "Configures", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "SpeedGainMode == EWIZMOSpeedGain::Manual"))
	float Speed3;
	UPROPERTY(BlueprintReadWrite, Category = "Configures", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "SpeedGainMode == EWIZMOSpeedGain::Manual"))
	float Speed4;
	UPROPERTY(BlueprintReadWrite, Category = "Configures", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "SpeedGainMode == EWIZMOSpeedGain::Manual"))
	float Speed5;
	UPROPERTY(BlueprintReadWrite, Category = "Configures", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0", EditCondition = "SpeedGainMode == EWIZMOSpeedGain::Manual"))
	float Speed6;

	UPROPERTY(BlueprintReadWrite, Category = "Configures", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0"))
		float RotationMotionRatio;
	UPROPERTY(BlueprintReadWrite, Category =" Configures", EditAnywhere, meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0"))
		float GravityMotionRatio;
	UPROPERTY(BlueprintReadWrite, Category = "Configures", EditAnywhere)
		bool isOrigined;

	UPROPERTY(BlueprintAssignable, Category = "System Event")
		FWizmoSystemOnEvent OnSystemEventCall;

	UFUNCTION(BlueprintCallable, Category = "WIZMOController")
		void OpenWIZMO();
	UFUNCTION(BlueprintCallable, Category = "WIZMOController")
		void CloseWIZMO();

	UFUNCTION(BlueprintCallable, Category = "WIZMOController")
		EWIZMOState GetState();
	UFUNCTION(BlueprintCallable, Category = "WIZMOController")
		bool IsRunning();

	UFUNCTION(BlueprintCallable, Category = "WIZMOController")
		FString SerialNumber();
};
