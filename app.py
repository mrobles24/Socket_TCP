import socketserver
import threading
import random

# A multithreaded TCP server, handling each connection in a separate thread
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True  # Automatically close threads when the server shuts down
    allow_reuse_address = True  # Allow address reuse to avoid "Address already in use" errors

# Handler for each game session (Agent interaction)
class AgentHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print("Connected: %s on %s" % (self.client_address, threading.current_thread().name))
        try:
            self.initialize()  # Initialize the agent in the game

            if self.agent_id == '1':  # Agent 1 is the one requesting help
                self.delayed_help_request()  # Agent 1 triggers the help request after a delay
            else:
                self.wait_and_respond_to_help()  # Other agents wait and potentially respond to the help request

        except Exception as e:
            print(e)
        finally:
            print("Disconnected: client %s on %s" % (self.client_address, threading.current_thread().name))

    # Helper function to send messages to the agent
    def send(self, message):
        self.wfile.write(("%s\n" % message).encode('utf-8'))

    # Initialize the agent and assign a role (help requester or helper)
    def initialize(self):
        Game.join(self)  # Join the game session
        if self.agent_id == '1':  # If this is Agent 1, they request help
            self.send('WELCOME Agent 1. Waiting to send help request after 10 seconds.')
            self.game.current_agent = self  # Set Agent 1 as the current agent in the game
        else:
            self.send(f'WELCOME Agent {self.agent_id}. Waiting for help request.')

    # Simulates a delay for Agent 1 before sending a help request
    def delayed_help_request(self):
        print("Agent 1 started waiting for 10 seconds.")
        # Simulated delay with a loop (instead of time.sleep)
        for _ in range(1000000000):  # Loop to simulate a 10-second delay
            pass

        # After the delay, Agent 1 sends a help request
        help_message = "Help Needed!"
        help_id = self.game.new_help_request(help_message)  # Register a new help request
        self.send(f"Help request {help_id} sent by Agent 1.")
        print(f"Agent 1 sent help request: {help_message}")

        # Wait for responses from other agents
        self.wait_for_responses(help_id)

    # Waits for responses from other agents and checks if the help request is satisfied
    def wait_for_responses(self, help_id):
        responses_needed = 2  # Number of responses needed to satisfy the request
        responses_received = 0
        timeout = 10  # Timeout period (not actively used in the code)

        loop_count = 0
        while responses_received < responses_needed:
            # Simulated time passing by counting loop iterations (instead of using time.sleep)
            if loop_count > 1000000000:  # Approximate simulation of 10 seconds
                break
            
            # Check if any agent has responded
            response = self.game.get_response(help_id)
            if response:
                responses_received += 1
                self.send(f"Received support from Agent {response}")
                print(f"Agent 1 received support from Agent {response}")

            loop_count += 1  # Increase loop count to simulate time

        # If enough responses were received, end the game successfully
        if responses_received == 2:
            self.send(f"Help request {help_id} satisfied. Ending program sucessfully.")
            print(f"Help request {help_id} satisfied. Ending program successfully.")
            self.game.end_game()  # End the game when the help request is satisfied
        else:
            # If not enough responses, end the game due to timeout or insufficient help
            self.send(f"Help request {help_id} expired with {responses_received} supports. Ending program unsucessfully.")
            print(f"Help request {help_id} expired with {responses_received} supports. Ending program unsucessfully.")
            self.game.end_game()

    # Other agents wait for a help request and decide whether to respond
    def wait_and_respond_to_help(self):
        while not self.game.is_help_request_active():  # Wait until a help request is active
            pass

        # 30% chance for each agent to respond to the help request
        if random.random() <= 0.3:
            response = self.game.respond_to_help(self.agent_id)  # Respond to the active request
            if response:
                self.send(f"Agent {self.agent_id} responded to help request {response}.")
                print(f"Agent {self.agent_id} responded to help request {response}.")
        else:
            self.send(f"Agent {self.agent_id} did not respond.")
            print(f"Agent {self.agent_id} did not respond.")

# Game class that manages the help requests and responses from agents
class Game:
    next_game = None  # Holds the reference to the next game session
    game_lock = threading.Lock()  # Lock to synchronize access to game state
    help_active = False  # Indicates if there is an active help request
    agent_count = 0  # Tracks the number of agents connected

    def __init__(self):
        self.current_agent = None
        self.lock = threading.Lock()  # Lock for modifying game state
        self.help_requests = []  # List of help requests
        self.responses = {}  # Dictionary of responses to each help request
        self.game_ended = False  # Flag to check if the game has ended

    # Creates a new help request and activates the help process
    def new_help_request(self, help_message):
        with self.lock:
            help_id = len(self.help_requests)  # Get a unique help request ID
            self.help_requests.append(help_message)
            self.responses[help_id] = []  # Initialize an empty response list for this help request
            self.help_active = True  # Mark that a help request is now active
            return help_id

    # Registers an agent's response to a help request
    def respond_to_help(self, agent_id):
        with self.lock:
            if self.help_requests and not self.game_ended:
                help_id = len(self.help_requests) - 1  # Respond to the latest help request
                self.responses[help_id].append(agent_id)  # Add the agent's response
                print(f"Agent {agent_id} responded to help request {help_id}")
                return help_id
            return None

    # Retrieves a response for a specific help request
    def get_response(self, help_id):
        with self.lock:
            if help_id in self.responses and self.responses[help_id]:
                return self.responses[help_id].pop(0)  # Return the first response from the queue
            return None

    # Checks if a help request is currently active
    def is_help_request_active(self):
        with self.lock:
            return self.help_active

    # Ends the game session by deactivating help requests
    def end_game(self):
        with self.lock:
            self.help_active = False  # Deactivate help requests
            self.game_ended = True  # Set the game to ended

    # Assigns agents to the game session
    @classmethod
    def join(cls, agent):
        with cls.game_lock:
            if cls.next_game is None:  # If no game exists, create one
                cls.next_game = Game()
                agent.game = cls.next_game
                agent.agent_id = '1'  # First agent is assigned as Agent 1 (help requester)
            else:
                # Subsequent agents are helpers (Agent 2, 3, 4, etc.)
                agent.agent_id = str(cls.agent_count + 2)
                agent.game = cls.next_game
            cls.agent_count += 1  # Increment the number of agents

# Start the multithreaded TCP server on port 9999
server = ThreadedTCPServer(('', 9999), AgentHandler)
try:
    print("Server started on port 9999.")
    server.serve_forever()  # Keep the server running
except KeyboardInterrupt:
    pass
server.server_close()  # Close the server when interrupted