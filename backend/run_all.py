import multiprocessing
import uvicorn
import sniffer


def run_main_webserver():
    from main_webserver import app, ws_manager
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(ws_manager.broadcast_from_queue())
    uvicorn.run(app, host="127.0.0.1", port=8082)

def run_captive_portal():
    from captive_portal import app
    uvicorn.run(app, host="127.0.0.1", port=8081)

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=run_main_webserver)
    #p2 = multiprocessing.Process(target=run_captive_portal)
    p3 = multiprocessing.Process(target=sniffer.start_sniffing)

    p1.start()
    #p2.start()
    p3.start()

    p1.join()
    #p2.join()
    p3.join()