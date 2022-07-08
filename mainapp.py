import time
import sys
import logging
logging.Formatter.converter = time.gmtime
logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/mainapp_full_log.log"),
    ],
    format='%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s',
    level=logging.INFO
)
import queue
from controller.api_worker import APIWorker
from controller import api_controller
from monitor.monitor import UniswapMonitor
from web3 import Web3
from fastapi import FastAPI, HTTPException, status
from starlette.responses import Response, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from exceptions.exceptions import *
from dotenv import load_dotenv

load_dotenv()

api_logger = logging.getLogger("api_logger")
handler = logging.FileHandler(f"logs/api_log.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s :  %(name)s  : %(funcName)s : %(message)s')
handler.setFormatter(formatter)
api_logger.addHandler(handler)


app = FastAPI()

origins = [
    "*",
    "http://127.0.0.1",
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def analyse_token(token):
    try:
        token = Web3.toChecksumAddress(token)

    except:
        raise HTTPException(status_code=400, detail="You supplied an invalid address")

    try:
        result = api_controller.analyse_token(token)

    except APIError as error:
        api_logger.warning("An API error occurred:", exc_info=True)
        raise HTTPException(status_code=500, detail=f"One or more external API's failed to process the requested token {token}")

    except Exception as d:
        api_logger.error("Analysis failed:", exc_info=True)
        raise HTTPException(status_code=500, detail=f"The application was not able to process the requested token {token}")

    return result


@app.get("/analyse/{token}")
def analyse_token_get(token):
    return analyse_token(token)


@app.post("/analyse")
def analyse_token_post(token: str):
    return analyse_token(token)


@app.get("/getTokenFromMonitor/{token}")
def get_token_automatic(token):
    try:
        token = Web3.toChecksumAddress(token)

    except:
        raise HTTPException(status_code=400, detail="You supplied an invalid address")

    result = api_controller.get_token_from_monitor(token)

    if result is None:
        raise HTTPException(status_code=404, detail="The requested token was not automatically analysed by the monitor")

    return result


@app.get("/getTokenFromSubmission/{token}")
def get_token_manual(token):
    try:
        token = Web3.toChecksumAddress(token)

    except:
        raise HTTPException(status_code=400, detail="You supplied an invalid address")

    result = api_controller.get_token_from_submission(token)

    if result is None:
        raise HTTPException(status_code=404, detail="The requested token was not yet submitted to be analysed")

    return result


@app.get("/getRecentScans")
def get_token_automatic(page_num: int = 0, page_size: int = 10):
    result = api_controller.get_recent_from_monitor(page_num, page_size)

    if result is None:
        raise HTTPException(status_code=404, detail="The requested token was not automatically analysed by the monitor")

    return result


@app.get("/getScanHistory/{token}")
def get_token_automatic(token):
    try:
        token = Web3.toChecksumAddress(token)

    except:
        raise HTTPException(status_code=400, detail="You supplied an invalid address")

    result = api_controller.get_scan_history(token)

    if result is []:
        raise HTTPException(status_code=404, detail="The requested token was not yet analysed by the monitor")

    return result


def main():
    # make queue here and give it to monitor
    main_queue = queue.Queue()

    api_worker = APIWorker("API Worker", main_queue, "eth-scam-checker")
    api_worker.start()

    monitor_thread = UniswapMonitor(1, "Uniswap Monitor", main_queue, 300.0)

    monitor_thread.start()


if __name__ == '__main__':

    log_config = uvicorn.config.LOGGING_CONFIG
    log_config['handlers']['default'] = {
        'formatter': 'default',
        'class': 'logging.FileHandler',
        'filename': 'logs/uvicorn.log'
    }
    log_config['handlers']['access'] = {
        'formatter': 'access',
        'class': 'logging.FileHandler',
        'filename': 'logs/access.log'
    }
    log_config['loggers']['uvicorn.error']['propagate'] = False
    log_config['loggers']['uvicorn.error']['level'] = 'ERROR'
    # log_config['loggers']['uvicorn']['level'] = 'CRITICAL'
    log_config['loggers']['uvicorn']['propagate'] = False

    main()
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_config=log_config)
    except Exception as e:
        pass


