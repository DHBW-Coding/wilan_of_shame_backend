#!/usr/bin/python

import multiprocessing
import uvicorn
import sniffer


def run_main_webserver(event_queue):
    from main_webserver import app

    app.state.event_queue = event_queue
    uvicorn.run(app, host="192.168.4.1", port=8083)

def run_captive_portal():
    from captive_portal import app
    uvicorn.run(app, host="192.168.4.1", port=8080)

def run_sniffer(event_queue):
    sniffer.start_sniffing(event_queue)

if __name__ == "__main__":
    event_queue = multiprocessing.Queue()

    p1 = multiprocessing.Process(target=run_main_webserver, args=(event_queue,))
    p2 = multiprocessing.Process(target=run_captive_portal)
    p3 = multiprocessing.Process(target=run_sniffer, args=(event_queue,))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
