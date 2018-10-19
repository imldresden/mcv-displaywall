"use strict";

let IP_SETTINGS = "MarcLaptop";  // MarcLaptop, LaborDesktop, Wall, SurfaceHub

let server_port = "8080";  // TODO: Decide which server to use.
let server_ip = "";
if (IP_SETTINGS === "MarcLaptop") {
    server_ip = "141.76.67.175";
} else if (IP_SETTINGS === "LaborDesktop") {
    server_ip = "141.76.67.209";
} else if (IP_SETTINGS === "Wall") {
    server_ip = "141.76.67.198";
} else if (IP_SETTINGS === "SurfaceHub") {
    server_ip = "141.76.67.202";
}

let complete_server_ip = server_ip + ":" + server_port;

export {
    IP_SETTINGS,
    server_port,
    server_ip,
    complete_server_ip,
}