from django.shortcuts import HttpResponse
from _datetime import datetime
import requests
import redis, json, math, re
from DYAdmin.models import Task, Customer, Peer, PeerVideo, Comment
import threading
from .API import scrawl, dy_sign
import logging
from django.db import DatabaseError, transaction
from utils.general import AjaxReturn

# Redis keys
TASK_LIST = 'TASK_LIST'
DOING_LIST = 'DOING_LIST'
HOT_TOPIC = 'HOT_TOPIC'


def updateHotTopics(request):
    # 爬取后存redis
    data = dy_sign('hot_topic')
    red = redis.Redis(host='localhost', port=6379, decode_responses=True)
    red.set(HOT_TOPIC, json.dumps(data))
    red.close()
    return HttpResponse(datetime.now())


def taskBegin(task):
    logger = logging.getLogger('django')
    logger.error(f'begin----------{task.id} {task.title}-----------{datetime.now()}')
    # TODO 查看上次任务是否还在进行
    # TODO 每个视频上次爬到第几页

    task.save()
    now = datetime.now().timestamp()
    # 遍历task的video
    flag = True
    videoArr = task.video_set.all()
    for video in videoArr:
        logger.error(f'-------video {video.desc}-------')
        # 看看当前任务是否还在 TASK_LIST 里面
        if checkTask(task.id) and flag:
            # 查看视频上次评论数 对比本次新增，多20评论就请求第二页，多40就请求第三页（第一页都是高赞 作者回复）
            old_comment_num = video.comment_num
            if not video.comment_num:
                old_comment_num = 0
            firstPage = scrawl('comment', task.id, video.aweme_id, 1)
            if firstPage:
                # 更新评论数
                video.comment_num = firstPage['total']
                video.save()
                # 未采集过
                task.filter_words = '' if not task.filter_words else task.filter_words
                if task.filter_words == '':
                    match_arr = []
                else:
                    match_arr = task.filter_words.split(',')

                if old_comment_num == 0 and firstPage['has_more'] == 1:
                    for page in range(1, math.ceil(video.comment_num / 20) + 1):
                        if page == 1:
                            commentData = firstPage
                        else:
                            # if flag:
                            commentData = scrawl('comment', task.id, video.aweme_id, page)

                        if commentData and commentData['comments'] and len(commentData['comments']) > 0:
                            logger.error(f"V_comment----{len(commentData['comments'])}")
                            # 过滤任务关键词
                            for comm in commentData['comments']:
                                if not isWithinDays(now,comm['create_time'],task.within_days):
                                    break
                                hit = []
                                for word in match_arr:
                                    if word in comm['text']:
                                        hit.append(word)
                                if len(hit) > 0 or len(match_arr) == 0:

                                    '''---------------------------'''
                                    # 保存评论
                                    if checkNSubCommentNum(task.Customer_id):
                                        if Comment.objects.filter(cid=comm['cid'],
                                                                  Task_id=task.id).count() == 0:
                                            saveComment(comm, task.Customer_id, task.id, video.id, hit)
                                    else:
                                        flag = False
                                        break

                                # 保存赞超过50的
                                elif comm['digg_count'] >= 50:
                                    if Comment.objects.filter(cid=comm['cid'],
                                                              Task_id=task.id).count() == 0:
                                        saveComment(comm, task.Customer_id, task.id, video.id, hit, is_ai=1)

                        if commentData['has_more'] == 0:
                            break
                elif firstPage['has_more'] == 1 and flag:
                    # 搜头几页
                    totalPage = math.ceil((video.comment_num - old_comment_num) / 20) + 2
                    for page in range(1, totalPage):
                        if page == 1:
                            commentData = firstPage
                        else:
                            # if flag:
                            commentData = scrawl('comment', task.id, video.aweme_id, page)

                        if commentData and commentData['comments'] and len(commentData['comments']) > 0:
                            logger.error(f"V_comment----{len(commentData['comments'])}")
                            # 过滤任务关键词
                            for comm in commentData['comments']:
                                if not isWithinDays(now,comm['create_time'],task.within_days):
                                    break

                                hit = []
                                for word in match_arr:
                                    if word in comm['text']:
                                        hit.append(word)
                                if len(hit) > 0 or len(match_arr) == 0:

                                    '''---------------------------'''
                                    # 保存评论
                                    if checkNSubCommentNum(task.Customer_id):
                                        if Comment.objects.filter(cid=comm['cid'],
                                                                  Task_id=task.id).count() == 0:
                                            saveComment(comm, task.Customer_id, task.id, video.id, hit)
                                    else:
                                        flag = False
                                        break

                                # 保存赞超过50的
                                elif comm['digg_count'] >= 50:
                                    if Comment.objects.filter(cid=comm['cid'],
                                                              Task_id=task.id).count() == 0:
                                        saveComment(comm, task.Customer_id, task.id, video.id, hit, is_ai=1)

                        if commentData['has_more'] == 0:
                            break

        else:
            break
    # 更新同行视频列表 不要更新总评论数
    if flag:
        peerArr = Peer.objects.filter(id__in=json.loads(task.peer_monitor_ids)).all()
        for peer in peerArr:
            logger.error(f'-------peer {peer.nickname}-------')

            peerVedioList = scrawl('aweme_post', task.id, peer.sec_uid, 1)
            print(peer.sec_uid)
            if peerVedioList and peerVedioList['aweme_list'] and len(peerVedioList['aweme_list']) > 0:
                for video in peerVedioList['aweme_list']:
                    # # 更新粉丝 点赞
                    # peer.avatar_thumb = video['author']['avatar_thumb']['url_list'][0]
                    # peer.signature = video['author']['signature']
                    # 保存视频列表
                    if PeerVideo.objects.filter(Task_id=task.id, aweme_id=video['aweme_id']).count() == 0:
                        logger.error(f"add peerV {video['desc']} ")
                        peerVideo = PeerVideo(Customer_id=task.Customer_id, aweme_id=video['aweme_id'], Task_id=task.id,
                                              Peer_id=peer.id, desc=video['desc'])
                        peerVideo.save()
        # 遍历同行视频
        # 过滤 或者 点赞高的
        peerVideoArr = task.peervideo_set.all()
        print(peerVideoArr)
        for peerV in peerVideoArr:
            logger.error(f'-------peerVideo {peerV.desc}-------')
            # 看看当前任务是否还在 TASK_LIST 里面
            if checkTask(task.id) and flag:
                # 查看视频上次评论数 对比本次新增，多20评论就请求第二页，多40就请求第三页（第一页都是高赞 作者回复）
                old_comment_num = peerV.comment_num
                if not peerV.comment_num:
                    old_comment_num = 0
                firstPage = scrawl('comment', task.id, peerV.aweme_id, 1)

                logger.error(f'-------peerVideo comment total {firstPage["total"]}-------')
                if firstPage:
                    # 更新评论数
                    peerV.comment_num = firstPage['total']
                    peerV.save()
                    # 未采集过
                    task.filter_words = '' if not task.filter_words else task.filter_words
                    if task.filter_words == '':
                        match_arr = []
                    else:
                        match_arr = task.filter_words.split(',')

                    if old_comment_num == 0 and firstPage['has_more'] == 1:
                        for page in range(1, math.ceil(peerV.comment_num / 20) + 1):
                            if page == 1:
                                commentData = firstPage
                            else:
                                # if flag:
                                commentData = scrawl('comment', task.id, peerV.aweme_id, page)

                            if commentData and commentData['comments'] and len(commentData['comments']) > 0:
                                logger.error(f"peer_V_comment----{len(commentData['comments'])}")
                                # 过滤任务关键词
                                for comm in commentData['comments']:
                                    if not isWithinDays(now,comm['create_time'],task.within_days):
                                        break
                                    hit = []
                                    for word in match_arr:
                                        if word in comm['text']:
                                            hit.append(word)
                                    if len(hit) > 0 or len(match_arr) == 0:

                                        '''---------------------------'''
                                        # 保存评论

                                        if checkNSubCommentNum(task.Customer_id):
                                            if Comment.objects.filter(cid=comm['cid'],
                                                                      Task_id=task.id).count() == 0:
                                                saveComment(comm, task.Customer_id, task.id, peerV.id, hit,
                                                            is_peerVideo=True)
                                        else:
                                            flag = False
                                            break

                                    # 保存赞超过50的
                                    elif comm['digg_count'] >= 50:
                                        if Comment.objects.filter(cid=comm['cid'],
                                                                      Task_id=task.id).count() == 0:
                                            saveComment(comm, task.Customer_id, task.id, peerV.id, hit, is_ai=1,
                                                        is_peerVideo=True)

                            if commentData['has_more'] == 0:
                                break
                    elif firstPage['has_more'] == 1 and flag:
                        # 搜头几页
                        totalPage = math.ceil((peerV.comment_num - old_comment_num) / 20) + 2
                        for page in range(1, totalPage):
                            if page == 1:
                                commentData = firstPage
                            else:
                                # if flag:
                                commentData = scrawl('comment', task.id, peerV.aweme_id, page)

                            if commentData and commentData['comments'] and len(commentData['comments']) > 0:
                                logger.error(f"peer_V_comment----{len(commentData['comments'])}")
                                # 过滤任务关键词
                                for comm in commentData['comments']:
                                    if not isWithinDays(now,comm['create_time'],task.within_days):
                                        break
                                    hit = []
                                    for word in match_arr:
                                        if word in comm['text']:
                                            hit.append(word)
                                    if len(hit) > 0 or len(match_arr) == 0:
                                        '''---------------------------'''
                                        # 保存评论
                                        if checkNSubCommentNum(task.Customer_id):
                                            if Comment.objects.filter(cid=comm['cid'],
                                                                      Customer_id=task.Customer_id).count() == 0:
                                                saveComment(comm, task.Customer_id, task.id, peerV.id, hit,
                                                            is_peerVideo=True)

                                    # 保存赞超过50的
                                    elif comm['digg_count'] >= 50:
                                        if Comment.objects.filter(cid=comm['cid'],
                                                                  Customer_id=task.Customer_id).count() == 0:
                                            saveComment(comm, task.Customer_id, task.id, peerV.id, hit, is_ai=1,
                                                        is_peerVideo=True)
                            if commentData['has_more'] == 0:
                                break

            else:
                break

    logger.error(f'end=========={task.id} {task.title}============{datetime.now()}')


def checkTask(id):
    red = redis.Redis(host='localhost', port=6379, decode_responses=True)
    arr = json.loads(red.get(TASK_LIST))
    red.close()
    if id in arr:
        return True
    return


def checkNSubCommentNum(Customer_id):
    # 扣评论数
    try:
        with transaction.atomic():
            cus = Customer.objects.filter(id=Customer_id).get()
            if cus.comment_num_left <= 0:
                print(f'1  {cus.comment_num_left}')
                return
            cus.comment_num_left -= 1
            cus.save()
    except DatabaseError:
        return

    print(f'2  {cus.comment_num_left}')
    return True


def saveComment(comm, Customer_id, Task_id, Video_id, hit, is_ai=0, is_peerVideo=False):
    vx = re.compile(r'[a-zA-Z0-9]{6,20}').findall(comm['user']['signature'])
    phone = re.compile(r'1[356789]\d{9}').findall(comm['user']['signature'])
    vx = ','.join((str(x) for x in vx)) if len(vx) > 0 else None
    phone = ','.join((str(x) for x in phone)) if len(phone) > 0 else None
    dict = {
        'Customer_id': Customer_id,
        'Task_id': Task_id,
        'cid': comm['cid'],
        'uid': comm['user']['uid'],
        'sec_uid': comm['user']['sec_uid'],
        'unique_id': comm['user']['unique_id'],
        'nickname': comm['user']['nickname'],
        'avatar_thumb': comm['user']['avatar_thumb']['url_list'][0],
        'vx': vx, 'phone': phone, 'text': comm['text'],
        'hit_word': ','.join((str(x) for x in hit)), 'is_ai': is_ai
    }
    if is_peerVideo:
        dict['PeerVideo_id'] = Video_id
    else:
        dict['Video_id'] = Video_id
    c = Comment(**dict)
    c.save()
    return True


'''一小时执行一次'''


def commentTasks(request):
    red = redis.Redis(host='localhost', port=6379, decode_responses=True)
    # 所有进行中的任务
    taskList = Task.objects.filter(status=1).all()

    arr = []
    # doing = []
    for task in taskList:
        arr.append(task.id)
        thread_task = threading.Thread(target=taskBegin, args=(task,))
        thread_task.start()

    red.set(TASK_LIST, json.dumps(arr))
    red.close()

    return HttpResponse(datetime.now())


'''新增任务'''


def addTask(task):
    # 更新 TASK_LIST
    # 启动一条任务线程
    # 30分钟前执行过的才执行
    import time

    logger = logging.getLogger('django')
    now = time.time()
    # if now - task.updated_at.timestamp() > 3 * 60 or now - task.created_at.timestamp() < 3 * 60:
    if True:
        red = redis.Redis(host='localhost', port=6379, decode_responses=True)

        arr = json.loads(red.get(TASK_LIST))
        arr.append(task.id)
        thread_task = threading.Thread(target=taskBegin, args=(task,))
        thread_task.start()

        red.set(TASK_LIST, json.dumps(arr))
        red.close()

        logger.error(f'addTask----------{task.id} {task.title}-----------{datetime.now()}')
    else:
        logger.error(f'addTask Failed----------{task.id} {task.title}-----------{datetime.now()}')
    return HttpResponse(datetime.now())


def isWithinDays(now,create_time,days):
    if days == 0:
        return True
    if (now-create_time)/86400 <= days:
        return True
    else:
        return

def testTask(request):
    # e = requests.post('http://localhost:8000/dy_sign',{'method':'search_video','kw':'周末'})
    # return AjaxReturn(1,'获取成功',e.json())
    pass


