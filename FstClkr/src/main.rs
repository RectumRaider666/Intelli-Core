use std::{env, ptr};
use x11::xlib;
use x11::xtest;

fn click(display: *mut xlib::Display, x: i32, y: i32) {
    unsafe {
        xlib::XWarpPointer(
            display,
            0,
            xlib::XDefaultRootWindow(display),
            0,
            0,
            0,
            0,
            x,
            y,
        );

        xtest::XTestFakeButtonEvent(display, 1, 1, 0);
        xtest::XTestFakeButtonEvent(display, 1, 0, 0);
        xlib::XFlush(display);
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() != 3 {
        eprintln!("Usage: fstclkr <x> <y>");
        std::process::exit(1);
    }

    let x: i32 = args[1].parse().expect("Invalid X");
    let y: i32 = args[2].parse().expect("Invalid Y");

    unsafe {
        let display = xlib::XOpenDisplay(ptr::null());
        if display.is_null() {
            panic!("Cannot open X display")
        }

        let mut clicks: u64 = 0;

        loop {
            click(display, x, y);
            clicks += 1;
            if clicks % 100 == 0 {
                println!("Clicks: {}", clicks)
            }
        }
    }
}