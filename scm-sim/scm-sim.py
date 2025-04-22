import string
import networkx as nx
import json
from random import random
import matplotlib.pyplot as plt

my_json = {
  "nodes": [
    {
      "name": "Material Requirement Creation",
      "queues": 1,
      "processing_time": 2,
      "connected_nodes": ["Material Planning"]
    },
    {
      "name": "Material Planning",
      "queues": 2,
      "processing_time": 3,
      "connected_nodes": ["Purchase Requisition", "Production Planning"]
    },
    {
      "name": "Purchase Requisition",
      "queues": 1,
      "processing_time": 1,
      "connected_nodes": ["Purchase Order"]
    },
    {
      "name": "Production Planning",
      "queues": 3,
      "processing_time": 4,
      "connected_nodes": ["Production Order"]
    },
    {
      "name": "Purchase Order",
      "queues": 2,
      "processing_time": 5,
      "connected_nodes": ["Goods Receipt"]
    },
    {
      "name": "Production Order",
      "queues": 2,
      "processing_time": 6,
      "connected_nodes": ["Goods Receipt"]
    },
    {
      "name": "Goods Receipt",
      "queues": 1,
      "processing_time": 2,
      "connected_nodes": ["Material Enters Warehouse"]
    },
    {
      "name": "Material Enters Warehouse",
      "queues": 1,
      "processing_time": 0,
      "connected_nodes": []
    }
  ],
  "edges": [
    {
      "from": "Material Requirement Creation",
      "to": "Material Planning",
      "probability": 1.0
    },
    {
      "from": "Material Planning",
      "to": "Purchase Requisition",
      "probability": 0.6
    },
    {
      "from": "Material Planning",
      "to": "Production Planning",
      "probability": 0.4
    },
    {
      "from": "Purchase Requisition",
      "to": "Purchase Order",
      "probability": 1.0
    },
    {
      "from": "Production Planning",
      "to": "Production Order",
      "probability": 1.0
    },
    {
      "from": "Purchase Order",
      "to": "Goods Receipt",
      "probability": 1.0
    },
    {
      "from": "Production Order",
      "to": "Goods Receipt",
      "probability": 1.0
    },
    {
      "from": "Goods Receipt",
      "to": "Material Enters Warehouse",
      "probability": 1.0
    }
  ]
}

class Event:
   """
   Represents a change in state. (when processing an object starts or stops)
   """
   def __init__(self, event_time: int, node: string, callback, e):
      self.time_trigger = event_time
      self.node = node
      self.callback = callback
      self.entity = e

sim_time = 0
event_queue = []
completed_entities = []

def make_graph():

   # Load the input file
   #  data = {}
   #  with open('./sample_data/input.json') as f:
   #     data = json.load(f)
   #     print(data)
   data = my_json

   # Make the directed graph
   G = nx.DiGraph()
   for node in data["nodes"]:
      if node["name"] == "Material Requirement Creation":
         G.add_node(node["name"], node=StartNode(node["name"], node["queues"], node["processing_time"]))
      else:
         G.add_node(node["name"], node=Node(node["name"], node["queues"], node["processing_time"]))
   for edge in data["edges"]:
      G.add_edge(edge["from"], edge["to"], weight=edge["probability"])
   print(G)
   return G

def draw_graph():
   pos = nx.shell_layout(graph)
   labels = nx.get_node_attributes(graph, 'name')
   #print(labels)

   plt.figure(figsize=(10, 10))
   nx.draw_networkx(graph, pos, with_labels=True, labels = labels, node_size=3000, node_color='skyblue', font_size=8, font_weight='bold', arrowsize=20)

   edge_labels = nx.get_edge_attributes(graph, 'label')
   probability_labels = nx.get_edge_attributes(graph, 'weight')

   combined_edge_labels = {key: f"{edge_labels[key]} (p={probability_labels[key]:.2f})" for key in edge_labels}

   nx.draw_networkx_edge_labels(graph, pos, edge_labels=probability_labels, font_size=8)

   plt.title("Material Flow")
   plt.axis('off')  # Turn off axis
   plt.show()

def process_next_event():
    '''
    Consume the next time-sequence event.
    '''
    e = event_queue.pop(0)
    global sim_time
    sim_time = e.time_trigger
    print(f'\nEvent triggered at time {sim_time}')
    e.callback(e.entity)

def sort_by_time(e):
   return e.time_trigger

def schedule_event( e: Event):
   """
   Insert an event into the event queue.
   """
   #print("Scheduled event")
   event_queue.append(e)
   event_queue.sort(key = sort_by_time) # time-consuming to run, fast to write :)

def run_simulation(end_time):
   """
   Start sources
   """
   e = Entity(0, sim_time)
   graph.nodes["Material Requirement Creation"]["node"].spawn_object(e)

   print("First object has been scheduled.")

   while sim_time < end_time and event_queue:
      print("Continuing onto the next event timestep.")
      process_next_event()
   end_simulation()

def end_simulation():
   """
   Pull together summary stats.
   """
   pass

class Entity:
   def __init__(self, name, born):
      self.name = name
      self.born = born
      self.age = 0

      self.time_started_curr_step = 0
      self.time_waiting_max = 0


   # Todo: trigger entity updates when their events are processed.
   def add_age(self, i: int) -> None:
      self.age += i

   def write_summary(self) -> None:
      pass
   
class Node:
   """
   A work center.
   Contains multiple workers each capable of processing Entities.
   """
   def __init__(self, name, num_workers, worktime):

        self.name = name
        self.workers = num_workers
        self.workers_available = num_workers
        self.queued_objs = []
        self.worktime = worktime

   def obj_arrival(self, obj):
      print(f'Entity {obj.name} arrived at Node {self.name}')
      self.queued_objs.append(obj)

      if (self.workers_available):
         self.start_work()

   def start_work(self):
      # Get the worker started on the next object in the queue
      self.workers_available = self.workers_available - 1
      obj = self.queued_objs.pop(0)
      print(f'Node {self.name} has started work on entity {obj.name}')

      # And schedule when the worker will be done
      print("Scheduling the next event")
      schedule_event(Event(sim_time + self.worktime, self.name, self.finish_work, obj))

   def finish_work(self, e):
        # Note we don't need to schedule an event for anything that happens concurrently, like starting a new item. We are already in an event.
        # Therefore, start the next item if we have one queued!
        print(f'Node {self.name} has completed work on entity {e.name}')

        if self.queued_objs and self.workers_available:
            print(f'{self.name} has a queue of {len(self.queued_objs)} objects. Starting next object')
            self.start_work()
        else:
            self.workers_available = self.workers_available + 1
        self.route_to_neighbor(e)

   def route_to_neighbor(self, e):
        # TODO: random roll the entity to the next node.
        prob = random()
        sum_weights = 0
        next_node = None
        for n in graph.neighbors(self.name):
            #print(graph[self.name][n]["weight"])
            sum_weights = sum_weights + graph[self.name][n]["weight"]
            if prob <= sum_weights:
               print(f'Routing entity from {self.name} to {n}')
               next_node = n
               break
        # If there are no viable paths, end the entity's simulation # TODO change this so we check whether we are at an exit node or errored
        if not next_node:
           completed_entities.append(e)
           e.write_summary()
        # Otherwise, queue the entity at the next node
        else:
           graph.nodes[next_node]["node"].obj_arrival(e)

class StartNode(Node):
   def __init__(self, name, num_workers, worktime):
      # Inherit the same setup as our parent
      super(StartNode, self).__init__(name, num_workers, worktime)

      # But add some extras for spawning entities into the graph
      self.object_counter = 1

   def spawn_object(self, e):

      self.route_to_neighbor(e)

      # Now prepare the next event
      self.object_counter = self.object_counter + 1
      e2 = Entity(self.object_counter, sim_time + self.worktime)
      schedule_event(Event(sim_time + self.worktime, self.name, self.spawn_object, e2))


graph = make_graph()
draw_graph()
run_simulation(100)