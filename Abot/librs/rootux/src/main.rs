use std::net::UdpSocket;

fn main() -> std::io::Result<()> {
    let addr = "0.0.0.0:5000";

    let socket = UdpSocket::bind(addr)?;

    println!("Worker agent listening on {}", addr);

    let mut buffer = [0u8; 4096];

    loop {
        let (size, sender) = socket.recv_from(&mut buffer)?;

        println!("--------------------------------");
        println!("From : {}", sender);
        println!("Bytes: {}", size);

        match std::str::from_utf8(&buffer[..size]) {
            Ok(text) => println!("Data : {}", text),
            Err(_) => println!("Data : <binary>"),
        }
    }
}