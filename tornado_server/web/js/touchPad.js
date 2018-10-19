"use strict";

import {complete_server_ip} from "./configApp.js";

/**
 * Creates a controller for a canvas that should be used as an touchpad.
 */
export class TouchPad {
    constructor() {
        //this._webSocketId = webSocketId;
        this._webSocketId = undefined;

        // Create the web socket for the touch pad.
        this._webSocket = new WebSocket(`ws://${complete_server_ip}/ws/touch_pad`);
        this._webSocket.onmessage = (m) => this._onWebSocketMessage(m);
        this._webSocket.onopen = () => this._send_TouchPadData();

        // Set variables for this object.
        this._width = window.innerWidth;
        this._height = window.innerHeight;

        this._svg = d3.select(".touchPad")
            .attr("width", this._width)
            .attr("height", this._height);

        this._svg.on("touchstart", (e) => this._onTouch("touchDown"));
        this._svg.on("touchend", (e) => this._onTouch("touchUp"));

        this._mcSvg = new Hammer.Manager(this._svg.node());
        this._mcSvg.add(new Hammer.Swipe({
            event: "swipe",
            pointers: 1,
            threshold: 10,
            velocity: 0.3,
            direction: Hammer.DIRECTION_ALL
        }));
        this._mcSvg.on("swipedown", (e) => this._onSwipe("swipeDown"));
        this._mcSvg.on("swipeup", (e) => this._onSwipe("swipeUp"));
    }

    // -------------- UI EVENTS -------------------------------------
    _onTouch(touchType) {
        this._send_TouchUpdate(touchType);
    }

    _onSwipe(swipeType) {
        this._send_TouchUpdate(swipeType);
    }

    // -------------- Events for the server connection --------------
    // -------------- MESSAGE ---------------------------------------
    /**
     * Handles the incoming messages from the touchpad web socket.
     * @param {!MessageEvent} message - The received message.
     * @private
     */
    _onWebSocketMessage(message) {

    }

    // -------------- SEND ------------------------------------------
    /**
     * Sends a "TouchPadData-Request" through the webSocket.
     * @private
     */
    _send_TouchPadData() {
        // TODO: Check that the webSocketId isn't undefined;
        this._webSocket.send(JSON.stringify({
            "messageType": "TouchPadData-Request",
            "data": {},
        }))
    }

    /**
     * Sends a "TouchUpdate" through the webSocket.
     * @param {!string} updateType - Should either be "touchdown" or "touchup".
     * @private
     */
    _send_TouchUpdate(updateType) {
        this._webSocket.send(JSON.stringify({
            "messageType": "TouchUpdate",
            "data": {
                "updateType": updateType,
            },
        }));
    }

}

