//wizmo.rs
//WIZAPPLY CO., LTD.
//rust lang

//use
use std::ffi::CString;

// define
pub const WIZMO_ERROR_HANDLE: i32 = -1;
pub const WIZMO_LOG_MAXCOUNT: usize = 4096;

// packet struct
#[repr(C)]
pub struct WizmoPacket
{
	pub axis1: f32,
	pub axis2: f32,
	pub axis3: f32,
	pub axis4: f32,
	pub axis5: f32,
	pub axis6: f32,

	//Axis speed/accel controls
	pub speed1_all: f32,
	pub speed2: f32,
	pub speed3: f32,
	pub speed4: f32,
	pub speed5: f32,
	pub speed6: f32,
	pub accel: f32,

	//Axis Processing
	pub roll: f32,
	pub pitch: f32,
	pub yaw: f32,
	pub heave: f32,
	pub sway: f32,
	pub surge: f32,

	pub rotation_motion_ratio: f32,
	pub gravity_motion_ratio: f32,

	pub command_send_count: i32,
	pub command: [u8;256],
}

// status enum
pub enum WizmoState {
	CanNotFindUsb,
	CanNotFindWizmo,
	CanNotCalibration,
	TimeoutCalibration,
	ShutDownActuator,
	CanNotCertificate,
	Initial,
	Running,
	StopActuator,
	CalibrationRetry
}

//dll
#[link(name = "wizmo64")]
#[allow(dead_code)]
extern {
    fn wizmoOpen(appCode: *const u8) -> i32;
    fn wizmoOpenSerialAssign(appCode: *const u8, assign: *const u8) -> i32;
    fn wizmoClose(handle:i32) -> i32;
	fn wizmoGetState(handle:i32) -> i32;
	fn wizmoWrite(handle:i32, pakcet:*const u8);	//packet
	fn wizmoSetAxisProcessingMode(handle:i32, flag:i32);
	fn wizmoSetSpeedGainMode(handle:i32, flag:i32);
	fn wizmoSetOriginMode(handle:i32, flag:i32);
	fn wizmoGetOriginMode(handle:i32) -> i32;
	fn wizmoGetAxisProcessingMode(handle:i32) -> i32;
	fn wizmoGetSpeedGainMode(handle:i32) -> i32;
	fn wizmoGetAppCode(handle:i32) -> *const u8;
	fn wizmoGetVersion(handle:i32) -> *const u8;
	fn wizmoGetStatusEXT4(handle:i32) -> i32;

	fn wizmoIsRunning(handle:i32) -> i32;

	fn wizmoGetBackLog(strData: *const u8, str_size:i32) -> i32;
	fn wizmoBackLogDataAvailable() -> i32;
}

pub fn open(app_code: &str) -> i32 {
    let s_str = CString::new(app_code).unwrap();
    let app_code_str = s_str.as_ptr() as *const u8;
	unsafe {
		let handle = wizmoOpen(app_code_str);
		handle
	}
}

pub fn open_assign(app_code: &str, assign: &str) -> i32 {
    let s_str = CString::new(app_code).unwrap();
	let s_str_assign = CString::new(assign).unwrap();
    let app_code_str = s_str.as_ptr() as *const u8;
	let assign_str = s_str_assign.as_ptr() as *const u8;
	unsafe {
		let handle = wizmoOpenSerialAssign(app_code_str, assign_str) as i32;
		handle
	}
}

pub fn close(handle: i32) -> i32 {
	unsafe {
		let res_handle = wizmoClose(handle) as i32;
		res_handle
	}
}

pub fn get_state(handle: i32) -> WizmoState {
	unsafe {
		let mut res_wiz = WizmoState::CanNotFindUsb;
		let res_state = wizmoGetState(handle) as i32;
	
		match res_state {
			WIZMO_ERROR_HANDLE => {res_wiz = WizmoState::CanNotFindUsb}
			0 => {res_wiz = WizmoState::CanNotFindUsb}
			1 => {res_wiz = WizmoState::CanNotFindWizmo}
			2 => {res_wiz = WizmoState::CanNotCalibration}
			3 => {res_wiz = WizmoState::TimeoutCalibration}
			4 => {res_wiz = WizmoState::ShutDownActuator}
			5 => {res_wiz = WizmoState::CanNotCertificate}
			6 => {res_wiz = WizmoState::Initial}
			7 => {res_wiz = WizmoState::Running}
			8 => {res_wiz = WizmoState::StopActuator}
			9 => {res_wiz = WizmoState::CalibrationRetry}
			_ => println!("get_state() -> WizmoState ERROR."),
		}
		res_wiz
	}
}

pub fn get_state_index(handle: i32) -> i32 {
	unsafe {
		let res_state = wizmoGetState(handle) as i32;
		res_state
	}
}

pub fn write(handle: i32, packet: &WizmoPacket) {
	unsafe {
		let data_ptr: *const WizmoPacket = packet as *const WizmoPacket;
		wizmoWrite(handle, data_ptr as *const u8);
	}
}

pub fn set_axis_processing_mode(handle: i32, flag: i32) {
	unsafe { wizmoSetAxisProcessingMode(handle, flag); }
}

pub fn set_speed_gain_mode(handle: i32, flag: i32) {
	unsafe { wizmoSetSpeedGainMode(handle, flag); }
}

pub fn set_origin_mode(handle: i32, flag: i32) {
	unsafe { wizmoSetOriginMode(handle, flag); }
}

pub fn get_origin_mode(handle: i32) -> bool {
	unsafe { 
		let fn_res: i32 = wizmoGetOriginMode(handle);
		if fn_res != 0 { true } else{ false }
	}
}

pub fn get_axis_processing_mode(handle: i32) -> bool {
	unsafe { 
		let fn_res: i32 = wizmoGetAxisProcessingMode(handle);
		if fn_res != 0 { true } else{ false }
	}
}

pub fn get_speed_gain_mode(handle: i32) -> bool {
	unsafe { 
		let fn_res: i32 = wizmoGetSpeedGainMode(handle);
		if fn_res != 0 { true } else{ false }
	}
}

pub fn get_status_ext4(handle: i32) -> bool {
	unsafe { 
		let fn_res: i32 = wizmoGetStatusEXT4(handle);
		if fn_res != 0 { true } else{ false }
	}
}

pub fn is_running(handle: i32) -> bool {
	unsafe { 
		let fn_res: i32 = wizmoIsRunning(handle);
		if fn_res != 0 { true } else{ false }
	}
}

pub fn get_backlog() -> String {
	unsafe {
		let logsize = wizmoBackLogDataAvailable();
		if logsize > 0 {
			let logbuffer: [u8;WIZMO_LOG_MAXCOUNT] = [0;WIZMO_LOG_MAXCOUNT];
			let logbuffer_ptr = &logbuffer as *const u8;
			let i_ret = wizmoGetBackLog(logbuffer_ptr, logsize);
			if i_ret <= 0 { //Error
				return "".to_string();
			}
			let logstr = std::str::from_utf8(std::slice::from_raw_parts(logbuffer_ptr, logsize as usize));
			return logstr.unwrap().to_string();
		}
	}
	"".to_string()
}

