from env import *

PATH = './model.pth'

if __name__ == '__main__':
    pygame.init()
    # process = Process()
    # end = False
    # while not end:
    #     process.update_screen()
    #     end = process.update()
    # pygame.quit()
    env = Env()
    print('emulation started')
    env.dqn.eval_net.load_state_dict(torch.load(PATH))
    for i in range(100):
        r = env.iterate()
        print('it: %d, total_reward: %.2f' % (i, r))
    torch.save(env.dqn.target_net.state_dict(), PATH)
