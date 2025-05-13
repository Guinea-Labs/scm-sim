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