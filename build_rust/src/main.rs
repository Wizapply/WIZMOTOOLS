//main.rs
//WIZAPPLY CO., LTD.
//rust lang

pub mod wizmo;

//use
use std::{thread, time};

#[warn(unused_variables)]
macro_rules! default_packet
{
	() => {
		wizmo::WizmoPacket {
			axis1:0.5,
			axis2:0.5,
			axis3:0.5,
			axis4:0.5,
			axis5:0.5,
			axis6:0.5,

			//Axis speed/accel controls
			speed_axis:0.8,
			accel_axis:0.5,
			speed_axis4:0.8,
			accel_axis4:0.5,

			//Axis Processing
			roll: 0.0,
			pitch: 0.0,
			yaw: 0.0,
			heave: 0.0,
			sway: 0.0,
			surge: 0.0,

			rotation_motion_ratio: 1.0,
			gravity_motion_ratio: 0.0,

			command_send_count: 0,
			command_stride: 0,
			command: [0;256],
		}
	};
}

fn read<T: std::str::FromStr>() -> T {
    let mut s = String::new();
    std::io::stdin().read_line(&mut s).ok();
    s.trim().parse().ok().unwrap()
}

fn main() {
    let handle = wizmo::open("");
	let mut packet = default_packet!();

	println!("WIZMO-START...");
    thread::sleep(time::Duration::from_secs(3));

	println!("This program can change ROLL, PITCH, YAW of the WIZMO. \nSpecification value [-1.0 to 1.0]. To exit, input [exit].");
	
	while wizmo::is_running(handle)
	{
		//input
		println!("ROLL->");
		packet.roll = read::<f32>();

		println!("PITCH->");
		packet.pitch = read::<f32>();

		println!("YAW->");
		packet.yaw = read::<f32>();

		//wizmo write
		wizmo::write(handle, &packet);

		//log
		let log = wizmo::get_backlog();
		if log != "" {
			println!("{}", log);
		}
	}

	thread::sleep(time::Duration::from_secs(1));
    println!("WIZMO-SHUTDOWN");
}
