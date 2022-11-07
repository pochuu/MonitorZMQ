from Monitor import Monitor
import logging

logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s.%(msecs)03d %(message)s',level=logging.INFO, datefmt='%H:%M:%S',)

class Client:
    def __init__(self):
        self.should_continue = True
        self.id = 1
        self.counter = 0 
        self.monitor = Monitor(self.id, 0.5)

    def start(self):
        while self.should_continue:
            self.monitor.send_request()
            self.monitor.go_into_critical()
            ############ START OF CRITICAL SECTION ############
            self.data = self.monitor.get_elements()
            if self.data is not None:
                for item in self.data:
                    if 'counter' in item.keys():
                        item["counter"] += 1
                        logging.info("ID: {} Counter state: {}".format(self.id,item["counter"] ))
                        self.counter +=1 
            self.monitor.update_elements(self.data)
            ############ END OF CRITICAL SECTION ############
            self.monitor.sending_token()

            ############ Closes 1st client after 2 succesful token sends ############
            if self.counter == 2:
                self.monitor.close()


if __name__ == "__main__":
    client = Client()
    client.start()