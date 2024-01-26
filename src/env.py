import torch
import torch.nn as nn
from display import *

BATCH_SIZE = 32
LR = 0.01
EPSILON = 0.5
GAMMA = 0.95
TARGET_REPLACE_ITER = 100
MEMORY_CAPACITY = 1000
N_STATES = 6
N_ACTIONS = 3
N_COUNT = 30


class Network(nn.Module):
    def __init__(self):
        super().__init__()
        self.i_l = nn.Linear(N_STATES, N_COUNT)
        self.o_l = nn.Linear(N_COUNT, N_ACTIONS)

    def forward(self, in_data: torch.Tensor) -> torch.Tensor:
        return self.o_l(torch.relu(self.i_l(in_data)))


# class ReplayMemory(object):
#     def __init__(self, capacity):
#         self.capacity = capacity
#         self.memory = []
#
#     def push(self, event):
#         self.memory.append(event)
#         if len(self.memory) > self.capacity:
#             del self.memory[0]
#
#     def sample(self, batch_size):
#         samples = zip(*random.sample(self.memory, batch_size))  # covert to a tuple
#         return map(lambda x: Variable(torch.cat(x, 0)), samples)


class DQN:
    def __init__(self):
        self.memory = np.zeros((MEMORY_CAPACITY, N_STATES * 2 + 2))
        self.last_reward = 0
        self.eval_net, self.target_net = Network(), Network()
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=LR)
        self.loss_func = nn.functional.mse_loss
        self.memory_counter = 0
        self.learn_step_counter = 0

    def select_action(self, in_data: torch.FloatTensor) -> int:
        if np.random.uniform() > EPSILON:
            return torch.max(self.eval_net(in_data), 0)[1]
        return np.random.randint(N_ACTIONS)

    def store_transition(self, s: np.ndarray, a: int, r: float, s_: np.ndarray):
        index = self.memory_counter % MEMORY_CAPACITY
        self.memory[index, :] = np.hstack((s, a, r, s_))
        self.memory_counter += 1

    def learn(self):  # 定义学习函数(记忆库已满后便开始学习)
        # 目标网络参数更新
        if self.learn_step_counter % TARGET_REPLACE_ITER == 0:
            self.target_net.load_state_dict(self.eval_net.state_dict())
            sample_index = np.random.choice(MEMORY_CAPACITY, BATCH_SIZE)
            b_memory = self.memory[sample_index, :]
            b_s = torch.FloatTensor(b_memory[:, :N_STATES])
            b_a = torch.LongTensor(b_memory[:, N_STATES:N_STATES + 1].astype(int))
            b_r = torch.FloatTensor(b_memory[:, N_STATES + 1:N_STATES + 2])
            print('best reward: %.2f' % torch.max(b_r))
            b_s_ = torch.FloatTensor(b_memory[:, -N_STATES:])
            q_eval = self.eval_net(b_s).gather(1, b_a)
            q_next = self.target_net(b_s_).detach()
            q_target = b_r + GAMMA * q_next.max(1)[0].view(BATCH_SIZE, 1)
            loss = self.loss_func(q_eval, q_target)
            # print('learning: loss = %.2f' % loss.item())
            self.optimizer.zero_grad()
            loss.backward()  # 2d-tensor(actions) used
            self.optimizer.step()
        self.learn_step_counter += 1


class Env:
    def __init__(self, max_steps: int = MEMORY_CAPACITY):
        self.dqn = DQN()
        self.process = Process()
        self.agent = self.process.player
        self.sensor = self.process.sensor
        self.s = np.zeros(6)  # resetting storing last_state in env
        self.s[:] = self.sensor.get_state()
        self.max_steps = max_steps

    def step(self, a: int) -> tuple[float, np.ndarray, bool]:
        throttle, turning = 0., 0.
        if a == 0:
            turning = -1.
            throttle = 0.5
        elif a == 1:
            turning = 1.
            throttle = 0.5
        elif a == 2:
            throttle = 1.
        done = self.agent.update(throttle, turning)
        self.sensor.update_pos()
        return self.agent.acceleration + self.agent.speed, self.sensor.get_state(), done

    def iterate(self):
        total_reward = 0.
        done = False
        steps = 0
        while not done and steps < self.max_steps:
            self.process.update_screen()
            a = self.dqn.select_action(torch.FloatTensor(self.s))
            r, s_, done = self.step(a)
            self.dqn.store_transition(self.s, a, r, s_)
            if self.dqn.memory_counter > MEMORY_CAPACITY:  # 如果累计的transition数量超过了记忆库的固定容量2000
                self.dqn.learn()
            self.s[:] = s_
            total_reward += r
            steps += 1
        self.agent.reset()
        return total_reward


class MyMod(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer = nn.Linear(3, 4)

    def forward(self, ts):
        return self.layer(ts)
