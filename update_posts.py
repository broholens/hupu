from multiprocessing import Process
from apscheduler.schedulers.background import BackgroundScheduler
from hupu_app import app, hupu


def schedule():
    scheduler = BackgroundScheduler()
    scheduler.add_job(hupu.store_posts, 'interval', hours=2)
    scheduler.start()


def main():
    p1 = Process(target=app.comment_posts, kwargs={'port': 80})
    p2 = Process(target=schedule)
    p1.start()
    hupu.is_logged()
    p2.start()


if __name__ == '__main__':
    main()