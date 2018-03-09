from multiprocessing import Process
from apscheduler.schedulers.background import BackgroundScheduler
from hupu_app import app, hupu


def schedule():
    scheduler = BackgroundScheduler()
    scheduler.add_job(hupu.comment_posts, 'corn', hour=7)
    scheduler.start()


def main():
    p1 = Process(target=app.run, kwargs={'port': 8080})
    p2 = Process(target=schedule)
    p1.start()
    hupu.is_logged()
    p2.start()


if __name__ == '__main__':
    main()