from django_apscheduler.jobstores import register_job
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from .models import AnimalLeaderBoard, Like_Animal
from django.utils import timezone
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler


# 实例化调度器
scheduler = BackgroundScheduler()
# 调度器使用默认的DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), 'default')


@register_job(scheduler,trigger=IntervalTrigger(seconds=10),replace_existing=True)  # 每10秒执行一次
def update_leaderboard():
    # print(f"Updating leaderboard at {datetime.now()}")
    leaderboards = AnimalLeaderBoard.objects.all()
    for leaderboard in leaderboards:
        if leaderboard.auto_update_score:
            # 计算得分：最近一天的点赞数
            score = Like_Animal.objects.filter(animal=leaderboard.animal).count()
            leaderboard.set_score(score)
            leaderboard.save()
    # print("new leaderboard:")
    # leaderboards = AnimalLeaderBoard.objects.all()
    # for leaderboard in leaderboards:
    #     print(f"{leaderboard.animal.nickname}: {leaderboard.score}")

scheduler.start()
#print(scheduler.get_jobs()[0].id)
#scheduler.remove_job(job_id='material.tasks.update_leaderboard')
