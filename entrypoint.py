from multiprocessing import Process
from hupu_app import app, hupu


def main():
    p1 = Process(target=app.run)
    p3 = Process(target=hupu.comment_posts)
    p1.start()
    p3.start()


if __name__ == '__main__':
    main()