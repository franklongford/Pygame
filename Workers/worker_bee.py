class Worker(object):
    def __init__(self, x, y, world, hive, dc, dm, dt):
        self.world = world
        self.hive = hive
        self.len = self.world.pixel
        self.pos = [int(x), int(y)]
        self.rect = pygame.rect.Rect((self.pos[0], self.pos[1], self.len, self.len))
        self.speed = self.world.pixel
        self.direction = int(np.random.rand() * 8)

        self.scout = True
        self.gather = False
        self.deliver = False
        self.dancing = False
        self.watching = False
        
        self.food = 0.0
        self.carry = dc
        self.memory = dm
        self.P_turn = dt
        self.res_mem = []

        tot_carry.append(dc)
        tot_P_turn.append(dt)
        tot_memory.append(dm)
        #print self.index, index, self.hive.index, self.pos, self.direction

    def update(self):

        self.check_status()
        #print self, self.scout, self.gather, self.deliver
        if self.dancing or self.watching: pass
        else: #self.step_forward()
            if np.random.rand() < self.P_turn: self.turn()
            else: self.step_forward()


    def check_status(self):

        #if self.scout == True:
            #self.collect()
        if self.gather: 
            #self.collect()
            self.choose_direction(self.res_mem[0].pos)
        elif self.deliver: 
            self.choose_direction(self.hive.pos)
        #if self.dancing: self.choose_direction(self.hive.dance_floor)


    def visit_hive(self):
#
        if self.food > 0: 
            self.deliver_food()
            #if np.random.rand() > 0.5: self.dance()
            if len(self.hive.res_map) == 0: self.scout = True
            else: 
                self.res_mem.append(random.choice(self.hive.res_map))
                self.choose_direction(self.res_mem[0].pos)
        #elif len(self.hive.dancing_bees) == 0: self.watch = True 

    def deliver_food(self):
        
        self.hive.food += self.food
        self.hive.total_food += self.food
        self.food = 0

        if self.res_mem[0] in self.hive.res_map: self.hive.res_map.remove(self.res_mem[0])
        self.hive.res_map.append(self.res_mem[0])
        self.res_mem.remove(self.res_mem[0])

        print self.hive.res_map

        #if self.hive.food >= 2.5: self.hive.create(self)
        #self.dancing = True

            
    def collect(self):

        if self.gather:
            for res in self.res_mem:
                if self.rect.colliderect(res.resource.rect):
                    self.pick_up(res.resource)
        else: 
            for resource in self.world.resource:
                if self.rect.colliderect(resource.rect):
                    self.pick_up(resource)
                    pos = [resource.pos[0] + (np.random.rand() - 0.5) * self.memory, 
                           resource.pos[1] + (np.random.rand() - 0.5) * self.memory]
                    food = resource.food + (np.random.rand() - 0.5) * self.memory
                    self.res_mem.append(Res_Memory(resource, pos, food))

        if self.food >= self.carry:
            self.scout = False 
            self.gather = False
            self.deliver = True

    def pick_up(self, res):

        self.food += 1
        res.food -= 1
        res.update()
        print res, self.food, res.food
        self.direction = np.mod(self.direction+4, 8)
        self.rect.move_ip(DIR_DELTA[self.direction] * self.speed)


    def dance(self): 

        if self.dancing == False:
            choice = np.random.rand()
            P1 = 0
            P2 = 0
            P_tot = 0
            for res in self.hive.res_map:
                P_tot += 1. / res.food
            for res in self.hive.res_map:
                P1 += 1. / res.food
                if choice >= P2 and choice < P1:
                    self.res_mem.append(res)

            self.dancing = True
            self.hive.dancing_bees.append(self)

        elif np.random.rand() < 0.2: self.dancing = False


    def choose_direction(self, destination):

        dx = destination[0] - self.rect[0]
        dy = destination[1] - self.rect[1]
        dx -= self.world.len * int( 2 * dx / self.world.len )
        dy -= self.world.len * int( 2 * dy / self.world.len )
        vector = unit_vector([dx, dy])

        for index, direction in enumerate(DIR_DELTA):
            print index, direction, np.array(vector), np.array(vector) - direction
            if np.sum((np.array(vector) - direction)**2) == 0:
                self.direction = index
                break
        print destination, self.rect, vector, self.direction, DIR_DELTA[self.direction]

    def step_forward(self):

        self.rect.move_ip(DIR_DELTA[self.direction] * self.speed)

        if self.gather:
            for res in self.res_mem:
                if self.rect.colliderect(res.resource.rect):
                    self.pick_up(res.resource)
        elif self.deliver:
            if self.rect.colliderect(self.hive.rect): self.visit_hive()
        
        for resource in self.world.resource:
            if self.rect.colliderect(resource.rect):
                if self.deliver or self.gather:
                    self.direction = np.mod(self.direction+4, 8)
                    self.rect.move_ip(DIR_DELTA[self.direction] * 2 * self.speed)
                else:
                    self.pick_up(resource)
                    pos = [resource.pos[0] + (np.random.rand() - 0.5) * self.memory, 
                           resource.pos[1] + (np.random.rand() - 0.5) * self.memory]
                    food = resource.food + (np.random.rand() - 0.5) * self.memory
                    self.res_mem.append(Res_Memory(resource, pos, food))

        self.check_periodicity()

        if self.food >= self.carry:
            self.scout = False 
            self.gather = False
            self.deliver = True


    def check_periodicity(self):

        if self.rect[0] >= self.world.len: self.rect[0] -= self.world.len
        if self.rect[1] >= self.world.len: self.rect[1] -= self.world.len
        if self.rect[0] < 0: self.rect[0] += self.world.len
        if self.rect[1] < 0: self.rect[1] += self.world.len


    def turn(self):
        rand_move = int(np.random.rand() * 3) - 1
        self.direction = np.mod(self.direction + rand_move, 8)             


    def watch(self):
        
        wait = np.random.rand()
        if wait > self.decide:
            choice = np.random.rand()
            P1 = 0
            P2 = 0
            P_tot = 0
            for bee in self.hive.dancing_bees:
                P_tot += 1. / bee.res_mem[0].food
            for bee in self.hive.dancing_bees:
                P1 += 1. / bee.res_mem[0].food
                if choice >= P2 and choice < P1:
                    self.res_mem.append(bee.res_mem[0])
                    self.gather = True
                    return

    def draw(self):
        pygame.draw.rect(self.world.screen, (0, 0, 0), self.rect)
