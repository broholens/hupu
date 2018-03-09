from multiprocessing import Process
from hupu_app import app, hp


# def main():
#     p1 = Process(target=app.run)
#     p2 = Process(target=hp.run)
#     p1.start()
#     p2.start()


if __name__ == '__main__':
    # main()
    hupu = HuPu()
    hupu.login('wechat')
    hupu.get_latest_post()