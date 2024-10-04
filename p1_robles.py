import socketserver
import threading
import random

# The server based on threads for each connection
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

# Session of the game
class AgentHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print("Connected: %s on %s" % (self.client_address, threading.current_thread().name))
        try:
            self.initialize()

            if self.agent_id == '1':  # Agent 1 is the help requester
                self.delayed_help_request()  # Trigger the delayed help request
            else:
                self.wait_and_respond_to_help()  # Other agents wait and respond to the help request

        except Exception as e:
            print(e)
        finally:
            print("Closed: client %s on %s" % (self.client_address, threading.current_thread().name))

    def send(self, message):
        self.wfile.write(("%s\n" % message).encode('utf-8'))

    def initialize(self):
        Game.join(self)
        if self.agent_id == '1':  # Agent 1 requests help
            self.send('WELCOME Agent 1. Waiting to send help request after 10 seconds.')
            self.game.current_agent = self
        else:
            self.send(f'WELCOME Agent {self.agent_id}. Waiting for help request.')

    def delayed_help_request(self):
        print("Agent 1 started waiting for 10 seconds.")
        # Simulate a 10-second delay using a loop
        for _ in range(1000000000):  # Loop for some time to simulate waiting
            pass

        # After the pseudo-delay, Agent 1 sends one help message
        help_message = "Help Needed!"
        help_id = self.game.new_help_request(help_message)
        self.send(f"Help request {help_id} sent by Agent 1.")
        print(f"Agent 1 sent help request: {help_message}")

        # Now, we wait for responses from other agents with a timeout of 10 seconds
        self.wait_for_responses(help_id)

    def wait_for_responses(self, help_id):
        responses_needed = 2
        responses_received = 0
        timeout = 10  # Timeout duration in seconds

        # Simulate time passage without using time.sleep()
        loop_count = 0
        while responses_received < responses_needed:
            # Check for the elapsed time based on loop iterations
            if loop_count > 1000000000:  # This should represent around 10 seconds
                break
            
            response = self.game.get_response(help_id)
            if response:
                responses_received += 1
                self.send(f"Received support from Agent {response}")
                print(f"Agent 1 received support from Agent {response}")

            loop_count += 1  # Increment loop count

        # Check if the required number of responses has been received
        if responses_received == 2:
            self.send(f"Help request {help_id} satisfied with quorum. Ending program.")
            print(f"Help request {help_id} satisfied with quorum. Ending program.")
            self.game.end_game()  # End the game
        else:
            self.send(f"Help request {help_id} expired with {responses_received} supports. Ending program.")
            print(f"Help request {help_id} expired with {responses_received} supports. Ending program.")
            self.game.end_game()  # End the game

    def wait_and_respond_to_help(self):
        while not self.game.is_help_request_active():
            pass  # Keep waiting for the help request

        # 80% chance to respond
        if random.random() <= 0.8:
            response = self.game.respond_to_help(self.agent_id)
            if response:
                self.send(f"Agent {self.agent_id} responded to help request {response}.")
                print(f"Agent {self.agent_id} responded to help request {response}.")
        else:
            self.send(f"Agent {self.agent_id} did not respond.")
            print(f"Agent {self.agent_id} did not respond.")


class Game:
    next_game = None
    game_lock = threading.Lock()
    help_active = False  # To track if a help request is active
    agent_count = 0

    def __init__(self):
        self.current_agent = None
        self.lock = threading.Lock()
        self.help_requests = []
        self.responses = {}
        self.game_ended = False

    def new_help_request(self, help_message):
        with self.lock:
            help_id = len(self.help_requests)
            self.help_requests.append(help_message)
            self.responses[help_id] = []
            self.help_active = True  # Help request is now active
            return help_id

    def respond_to_help(self, agent_id):
        with self.lock:
            if self.help_requests and not self.game_ended:
                help_id = len(self.help_requests) - 1  # Respond to the latest help request
                self.responses[help_id].append(agent_id)
                print(f"Agent {agent_id} responded to help request {help_id}")
                return help_id
            return None

    def get_response(self, help_id):
        with self.lock:
            if help_id in self.responses and self.responses[help_id]:
                return self.responses[help_id].pop(0)
            return None

    def is_help_request_active(self):
        with self.lock:
            return self.help_active

    def end_game(self):
        with self.lock:
            self.help_active = False  # Deactivate help requests
            self.game_ended = True  # End the game

    @classmethod
    def join(cls, agent):
        with cls.game_lock:
            if cls.next_game is None:
                cls.next_game = Game()
                agent.game = cls.next_game
                agent.agent_id = '1'  # First agent is the help requester
            else:
                agent.agent_id = str(cls.agent_count + 2)  # Agents 2, 3, and 4 are helpers
                agent.game = cls.next_game
            cls.agent_count += 1


# Start the server
server = ThreadedTCPServer(('', 9999), AgentHandler)
try:
    print("Server started on port 9999.")
    server.serve_forever()
except KeyboardInterrupt:
    pass
server.server_close()
