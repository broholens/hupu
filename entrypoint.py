from multiprocessing import Process
from hupu_app import app, hupu


def main():
    p1 = Process(target=app.run, kwargs=dict(host='0.0.0.0', port=8080))
    p3 = Process(target=hupu.comment_posts)
    p1.start()
    p3.start()


if __name__ == '__main__':
    main()
