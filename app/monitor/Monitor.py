import logging
from utils import PORTS
import threading
from time import sleep
import zmq

logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s.%(msecs)03d %(message)s',level=logging.INFO, datefmt='%H:%M:%S',)

class Monitor:
    def __init__(self, id, time, force = False):
        self.id = int(id)
        self.list = []
        self.time = float(time)
        self.rn = [0] * len(PORTS)
        self.send_token = False
        self.token_register = [0] * len(PORTS)
        self.request_and_recieve_lock = threading.Lock()
        self.stack = []
        self.que_ready = threading.Event()
        self.queue = []
        self.elements = [{"counter":0}]
        self.token = False
        self.send_token = False
        self.got_token = threading.Event()
        #id = 1 stars with a token
        if self.id == 1:
             self.got_token.set()
             self.token = True
             self.send_token = True
        self.port = PORTS[self.id]
        self.publisher = self.publisher_init()
        self.subscriber, self.pool = self.subscriber_init()
        self.data_to_exchange = {"number":[], "rn":[0]*len(PORTS), "elements": [{"counter":0}]}
        self.inc_messages_thread = threading.Thread(target=self.receive_messages)
        self.inc_messages_thread.start()

    def receive_messages(self):
        should_continue = True
        while should_continue:
            socks = dict(self.pool.poll(1000))
            self.request_and_recieve_lock.acquire()
            if self.subscriber in socks and socks[self.subscriber] == zmq.POLLIN:
                string = self.subscriber.recv_json()
                if string["type"] == "token" and string["target"] == self.id:
                    logging.info("ID: {} I got a token from {}".format(self.id, string["id_from"], string["number"]))
                    self.token = True
                    self.elements = string["elements"]
                    self.list = string["list"]
                    self.queue = string["queue"]
                    self.send_token = True
                    self.got_token.set()
                if string["type"] == "request":
                    for x in range(len(PORTS)):
                        if string["rn"][x] > self.data_to_exchange["rn"][x]:
                            self.data_to_exchange["rn"][x] = string["rn"][x]
                            if x not in self.queue and self.send_token:
                                self.queue.append(x)
                                self.que_ready.set()
                                logging.info("ID: {} I got request from {} ".format(self.id, string["id_from"]))
            self.request_and_recieve_lock.release()
  
    def send_request(self):
        self.request_and_recieve_lock.acquire()
        if self.token:
            self.list.append(self.id)
            self.token = False
            sleep(self.time)
            logging.info("ID: {} History of users {}".format(self.id, self.list))
        else:
            sleep(self.time)
            self.data_to_exchange["type"] = "request"
            self.data_to_exchange["id_from"] = self.id  
            self.rn[self.id] += 1
            self.data_to_exchange["rn"] = self.rn
            self.publisher.send_json(self.data_to_exchange)
            logging.info("ID: {} Sending request for token".format(self.id))
        self.request_and_recieve_lock.release()

    def go_into_critical(self):
        self.got_token.wait(1500)
        if self.send_token and self.token == False:
            self.que_ready.wait()

    def sending_token(self):
       if self.send_token and self.token == False:
            self.data_to_exchange["target"] = self.queue.pop(0)
            logging.info("ID: {} Token sending to: {} ".format(self.id, self.data_to_exchange["target"]))
            self.data_to_exchange["type"] = "token"
            self.data_to_exchange["list"] = self.list
            self.data_to_exchange["id_from"] = self.id  
            self.data_to_exchange["queue"] = self.queue 
            self.publisher.send_json(self.data_to_exchange)  
            self.send_token = False
            self.got_token.clear()
            self.que_ready.clear()

    def get_elements(self):
        if self.send_token and self.token == False:
            return self.elements

    def update_elements(self, elements):
        if self.send_token and self.token == False:
            self.data_to_exchange["elements"] = elements

    def publisher_init(self):
        pub_ctx = zmq.Context()
        pub_sock = pub_ctx.socket(zmq.PUB)
        pub_sock.bind('tcp://*:{}'.format(PORTS[self.id]))
        return pub_sock

    def subscriber_init(self):
        sub_ctx = zmq.Context()
        sub_sock = sub_ctx.socket(zmq.SUB)
        for port in PORTS:
            if port != self.port:
                sub_sock.connect('tcp://localhost:{}'.format(port))
        topicfilter = ""
        sub_sock.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
        sleep(1)
        poll = zmq.Poller()
        poll.register(sub_sock, zmq.POLLIN)
        return sub_sock, poll

    def close(self):
        self.publisher.close()
        logging.info("ID: {} Exits ".format(self.id))
        self.inc_messages_thread.join()


