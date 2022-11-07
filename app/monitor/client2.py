from Monitor import Monitor
import logging

logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s.%(msecs)03d %(message)s',level=logging.INFO, datefmt='%H:%M:%S',)

class Client:
    def __init__(self):
        self.should_continue = True
        self.id = 2
        self.monitor = Monitor(self.id, 0.5)

    def start(self):
        while self.should_continue:
            self.monitor.send_request()
            self.monitor.go_into_critical()
            self.data = self.monitor.get_elements()
            ############ START OF CRITICAL SECTION ############
            if self.data is not None:
                for item in self.data:
                    if 'counter' in item.keys():
                        item["counter"] += 3
                        logging.info("ID: {} Counter state: {}".format(self.id, item["counter"]))
            self.monitor.update_elements(self.data)
            ############ END OF CRITICAL SECTION ############
            self.monitor.sending_token()


if __name__ == "__main__":
    client = Client()
    client.start()