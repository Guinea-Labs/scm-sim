import string
import networkx as nx
import json
from random import random
import matplotlib.pyplot as plt

from node import StartNode, Node, Entity

with open('./data/input/sample.json') as f:
  my_json = json.load(f)


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




print("Running")
graph = make_graph()
#draw_graph()

run_simulation(100)
print("Done!")